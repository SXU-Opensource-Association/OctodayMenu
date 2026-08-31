"""add email verification delivery status

Revision ID: 20260627_0004
Revises: 20260626_0003
Create Date: 2026-06-27
"""

from alembic import op
import sqlalchemy as sa


revision = "20260627_0004"
down_revision = "20260626_0003"
branch_labels = None
depends_on = None


delivery_status = sa.Enum("PENDING", "SENT", "FAILED", name="emaildeliverystatus")


def upgrade() -> None:
    bind = op.get_bind()
    delivery_status.create(bind, checkfirst=True)

    with op.batch_alter_table("email_verifications") as batch_op:
        batch_op.add_column(
            sa.Column(
                "delivery_status",
                delivery_status,
                nullable=True,
            )
        )

    op.execute("UPDATE email_verifications SET delivery_status = 'SENT'")

    with op.batch_alter_table("email_verifications") as batch_op:
        batch_op.alter_column(
            "delivery_status",
            existing_type=delivery_status,
            nullable=False,
            server_default="PENDING",
        )


def downgrade() -> None:
    with op.batch_alter_table("email_verifications") as batch_op:
        batch_op.drop_column("delivery_status")
    delivery_status.drop(op.get_bind(), checkfirst=True)
