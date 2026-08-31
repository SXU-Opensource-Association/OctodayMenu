from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import MetaData, create_engine, select, text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the configured database into an empty, migrated SQLite database."
    )
    parser.add_argument("target", type=Path, help="Path to the destination SQLite database")
    return parser.parse_args()


def table_count(connection, table) -> int:
    return int(connection.execute(select(text("count(*)")).select_from(table)).scalar_one())


def main() -> None:
    args = parse_args()
    target_path = args.target.expanduser().resolve()
    if not target_path.is_file():
        raise SystemExit("Target database must already exist and be migrated to the latest revision.")

    source_engine = create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        isolation_level="REPEATABLE READ",
    )
    target_engine = create_engine(f"sqlite:///{target_path}")

    source_metadata = MetaData()
    target_metadata = MetaData()
    source_metadata.reflect(bind=source_engine)
    target_metadata.reflect(bind=target_engine)

    source_tables = set(source_metadata.tables)
    target_tables = set(target_metadata.tables)
    if source_tables != target_tables:
        missing = sorted(source_tables - target_tables)
        extra = sorted(target_tables - source_tables)
        raise SystemExit(f"Schema table mismatch; missing={missing}, extra={extra}")

    table_names = [
        table.name
        for table in source_metadata.sorted_tables
        if table.name != "alembic_version"
    ]

    copied_counts: dict[str, int] = {}
    with source_engine.connect() as source, target_engine.connect() as target:
        source_transaction = source.begin()
        target.execute(text("PRAGMA foreign_keys=OFF"))
        target.commit()
        target_transaction = target.begin()
        try:
            for name in table_names:
                source_table = source_metadata.tables[name]
                target_table = target_metadata.tables[name]

                source_columns = [column.name for column in source_table.columns]
                target_columns = [column.name for column in target_table.columns]
                if source_columns != target_columns:
                    raise RuntimeError(
                        f"Column mismatch for {name}: source={source_columns}, target={target_columns}"
                    )
                if table_count(target, target_table) != 0:
                    raise RuntimeError(f"Destination table is not empty: {name}")

                rows = [dict(row._mapping) for row in source.execute(select(source_table))]
                if rows:
                    target.execute(target_table.insert(), rows)
                copied_counts[name] = len(rows)

            target_transaction.commit()
            source_transaction.commit()
        except Exception:
            target_transaction.rollback()
            source_transaction.rollback()
            raise

    with target_engine.connect() as target:
        target.execute(text("PRAGMA foreign_keys=ON"))
        integrity = target.execute(text("PRAGMA integrity_check")).scalar_one()
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")
        violations = target.execute(text("PRAGMA foreign_key_check")).all()
        if violations:
            raise RuntimeError(f"SQLite foreign key check failed: {len(violations)} violation(s)")

        for name, expected in copied_counts.items():
            actual = table_count(target, target_metadata.tables[name])
            if actual != expected:
                raise RuntimeError(f"Row count mismatch for {name}: {expected} != {actual}")

    os.chmod(target_path, 0o600)
    print(f"Copied and verified {sum(copied_counts.values())} rows across {len(copied_counts)} tables.")
    for name in sorted(copied_counts):
        print(f"{name}: {copied_counts[name]}")


if __name__ == "__main__":
    main()
