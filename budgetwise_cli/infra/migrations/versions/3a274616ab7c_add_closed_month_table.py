"""Add closed month table

Revision ID: [system-generated]
Create Date: [system-generated]
"""

from alembic import op
import sqlalchemy as sa


revision = "[system-generated]"
down_revision = "[system-generated]"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "closed_months",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "month", name="uq_closed_month"),
    )


def downgrade() -> None:
    op.drop_table("closed_months")
