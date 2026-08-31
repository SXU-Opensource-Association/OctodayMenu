"""initial schema

Revision ID: 20260617_0001
Revises:
Create Date: 2026-06-17
"""

from alembic import op
import sqlalchemy as sa


revision = "20260617_0001"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("USER", "ADMIN", "SUPER_ADMIN", name="userrole")
tag_category = sa.Enum("BASIC", "TASTE", name="tagcategory")


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    tag_category.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_restaurants_id"), "restaurants", ["id"], unique=False)

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("category", tag_category, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "category", name="uq_tag_name_category"),
    )
    op.create_index(op.f("ix_tags_id"), "tags", ["id"], unique=False)

    op.create_table(
        "floors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurant_id", "level", name="uq_floor_restaurant_level"),
    )
    op.create_index(op.f("ix_floors_id"), "floors", ["id"], unique=False)

    op.create_table(
        "stalls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("floor_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location_hint", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("like_count", sa.Integer(), nullable=False),
        sa.Column("comment_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["floor_id"], ["floors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stalls_id"), "stalls", ["id"], unique=False)

    op.create_table(
        "dishes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stall_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("like_count", sa.Integer(), nullable=False),
        sa.Column("comment_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["stall_id"], ["stalls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dishes_id"), "dishes", ["id"], unique=False)

    op.create_table(
        "dish_tags",
        sa.Column("dish_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dish_id"], ["dishes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dish_id", "tag_id"),
        sa.UniqueConstraint("dish_id", "tag_id", name="uq_dish_tag"),
    )

    op.create_table(
        "daily_draws",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("dish_id", sa.Integer(), nullable=False),
        sa.Column("draw_date", sa.Date(), nullable=False),
        sa.Column("filters_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dish_id"], ["dishes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "draw_date", name="uq_daily_draw_user_date"),
    )
    op.create_index(op.f("ix_daily_draws_id"), "daily_draws", ["id"], unique=False)

    op.create_table(
        "email_verifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_email_verifications_email"), "email_verifications", ["email"], unique=False)
    op.create_index(op.f("ix_email_verifications_id"), "email_verifications", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_email_verifications_id"), table_name="email_verifications")
    op.drop_index(op.f("ix_email_verifications_email"), table_name="email_verifications")
    op.drop_table("email_verifications")
    op.drop_index(op.f("ix_daily_draws_id"), table_name="daily_draws")
    op.drop_table("daily_draws")
    op.drop_table("dish_tags")
    op.drop_index(op.f("ix_dishes_id"), table_name="dishes")
    op.drop_table("dishes")
    op.drop_index(op.f("ix_stalls_id"), table_name="stalls")
    op.drop_table("stalls")
    op.drop_index(op.f("ix_floors_id"), table_name="floors")
    op.drop_table("floors")
    op.drop_index(op.f("ix_tags_id"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_restaurants_id"), table_name="restaurants")
    op.drop_table("restaurants")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    tag_category.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
