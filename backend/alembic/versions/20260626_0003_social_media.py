"""social media and vendor images

Revision ID: 20260626_0003
Revises: 20260626_0002
Create Date: 2026-06-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260626_0003"
down_revision = "20260626_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("food_vendors") as batch_op:
        batch_op.add_column(sa.Column("image_url", sa.String(length=500), nullable=True))

    op.create_table(
        "vendor_likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vendor_id"], ["food_vendors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vendor_id", "user_id", name="uq_vendor_like_vendor_user"),
    )
    op.create_index(op.f("ix_vendor_likes_id"), "vendor_likes", ["id"], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reply_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vendor_id"], ["food_vendors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_id"), "comments", ["id"], unique=False)

    op.create_table(
        "comment_likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("comment_id", "user_id", name="uq_comment_like_comment_user"),
    )
    op.create_index(op.f("ix_comment_likes_id"), "comment_likes", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_comment_likes_id"), table_name="comment_likes")
    op.drop_table("comment_likes")
    op.drop_index(op.f("ix_comments_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index(op.f("ix_vendor_likes_id"), table_name="vendor_likes")
    op.drop_table("vendor_likes")
    with op.batch_alter_table("food_vendors") as batch_op:
        batch_op.drop_column("image_url")
