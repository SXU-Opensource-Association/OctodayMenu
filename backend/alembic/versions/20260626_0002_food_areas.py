"""food area hierarchy

Revision ID: 20260626_0002
Revises: 20260617_0001
Create Date: 2026-06-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260626_0002"
down_revision = "20260617_0001"
branch_labels = None
depends_on = None


area_type = sa.Enum("CANTEEN", "SNACK_STREET", "CUSTOM_AREA", name="areatype")


def upgrade() -> None:
    bind = op.get_bind()
    area_type.create(bind, checkfirst=True)

    op.create_table(
        "food_areas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_type", area_type, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("area_type", "name", name="uq_food_area_type_name"),
    )
    op.create_index(op.f("ix_food_areas_id"), "food_areas", ["id"], unique=False)

    op.create_table(
        "food_sections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["food_areas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("area_id", "level", name="uq_food_section_area_level"),
    )
    op.create_index(op.f("ix_food_sections_id"), "food_sections", ["id"], unique=False)

    op.create_table(
        "food_vendors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location_hint", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comment_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["food_areas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["section_id"], ["food_sections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("area_id", "section_id", "name", name="uq_food_vendor_area_section_name"),
    )
    op.create_index(op.f("ix_food_vendors_id"), "food_vendors", ["id"], unique=False)

    op.execute(
        """
        INSERT INTO food_areas (id, area_type, name, description, location, is_active, created_at, updated_at)
        SELECT id, 'CANTEEN', name, description, address, is_active, created_at, updated_at
        FROM restaurants
        """
    )
    op.execute(
        """
        INSERT INTO food_sections (id, area_id, name, level, description, is_active, created_at, updated_at)
        SELECT id, restaurant_id, name, level, description, is_active, created_at, updated_at
        FROM floors
        """
    )
    op.execute(
        """
        INSERT INTO food_vendors (id, area_id, section_id, name, description, location_hint, is_active, like_count, comment_count, created_at, updated_at)
        SELECT stalls.id, floors.restaurant_id, stalls.floor_id, stalls.name, stalls.description, stalls.location_hint,
               stalls.is_active, stalls.like_count, stalls.comment_count, stalls.created_at, stalls.updated_at
        FROM stalls
        JOIN floors ON floors.id = stalls.floor_id
        """
    )

    with op.batch_alter_table("dishes") as batch_op:
        batch_op.add_column(sa.Column("vendor_id", sa.Integer(), nullable=True))
    op.execute("UPDATE dishes SET vendor_id = stall_id")
    with op.batch_alter_table("dishes") as batch_op:
        batch_op.alter_column("vendor_id", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("stall_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("dishes") as batch_op:
        batch_op.alter_column("stall_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column("vendor_id")
    op.drop_index(op.f("ix_food_vendors_id"), table_name="food_vendors")
    op.drop_table("food_vendors")
    op.drop_index(op.f("ix_food_sections_id"), table_name="food_sections")
    op.drop_table("food_sections")
    op.drop_index(op.f("ix_food_areas_id"), table_name="food_areas")
    op.drop_table("food_areas")
    area_type.drop(op.get_bind(), checkfirst=True)
