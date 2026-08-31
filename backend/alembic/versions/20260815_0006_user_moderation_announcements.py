"""add user moderation and announcements

Revision ID: 20260815_0006
Revises: 20260815_0005
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260815_0006"
down_revision: str | None = "20260815_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        if "is_blacklisted" not in user_columns:
            batch_op.add_column(sa.Column("is_blacklisted", sa.Boolean(), server_default=sa.false(), nullable=False))
        if "is_muted" not in user_columns:
            batch_op.add_column(sa.Column("is_muted", sa.Boolean(), server_default=sa.false(), nullable=False))

    inspector = sa.inspect(bind)
    if "announcements" not in inspector.get_table_names():
        op.create_table(
            "announcements",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("level", sa.String(length=20), server_default="INFO", nullable=False),
            sa.Column("created_by_id", sa.Integer(), nullable=True),
            sa.Column("created_by_email", sa.String(length=255), nullable=False),
            sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = sa.inspect(bind)
    existing_indexes = {index["name"] for index in inspector.get_indexes("announcements")}
    for name, columns in (
        (op.f("ix_announcements_id"), ["id"]),
        (op.f("ix_announcements_created_by_id"), ["created_by_id"]),
        (op.f("ix_announcements_published_at"), ["published_at"]),
        (op.f("ix_announcements_expires_at"), ["expires_at"]),
    ):
        if name not in existing_indexes:
            op.create_index(name, "announcements", columns, unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_announcements_expires_at"), table_name="announcements")
    op.drop_index(op.f("ix_announcements_published_at"), table_name="announcements")
    op.drop_index(op.f("ix_announcements_created_by_id"), table_name="announcements")
    op.drop_index(op.f("ix_announcements_id"), table_name="announcements")
    op.drop_table("announcements")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_muted")
        batch_op.drop_column("is_blacklisted")
