from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import SessionLocal, init_db
from app.services.dev_seed import seed_development_data
from app.services.seed import ensure_super_admin


def main() -> None:
    init_db()
    with SessionLocal() as db:
        ensure_super_admin(db)
        seed_development_data(db)


if __name__ == "__main__":
    main()
