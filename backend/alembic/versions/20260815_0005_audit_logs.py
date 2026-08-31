"""add admin audit logs

Revision ID: 20260815_0005
Revises: 20260627_0004
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260815_0005"
down_revision: str | None = "20260627_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "session_version" not in user_columns:
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(sa.Column("session_version", sa.Integer(), server_default="0", nullable=False))

    if "audit_logs" not in inspector.get_table_names():
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("actor_id", sa.Integer(), nullable=True),
            sa.Column("actor_email", sa.String(length=255), nullable=False),
            sa.Column("actor_role", sa.String(length=32), nullable=False),
            sa.Column("action", sa.String(length=32), nullable=False),
            sa.Column("resource", sa.String(length=500), nullable=False),
            sa.Column("status_code", sa.Integer(), nullable=False),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = sa.inspect(bind)
    existing_indexes = {index["name"] for index in inspector.get_indexes("audit_logs")}
    for name, columns in (
        (op.f("ix_audit_logs_id"), ["id"]),
        (op.f("ix_audit_logs_actor_id"), ["actor_id"]),
        (op.f("ix_audit_logs_created_at"), ["created_at"]),
    ):
        if name not in existing_indexes:
            op.create_index(name, "audit_logs", columns, unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("session_version")
