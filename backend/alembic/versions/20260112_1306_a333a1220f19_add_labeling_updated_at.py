"""add_labeling_updated_at

Revision ID: a333a1220f19
Revises: a9dfebb3e3c0
Create Date: 2026-01-12 13:06:12.565651+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a333a1220f19'
down_revision = 'a9dfebb3e3c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Only keep the necessary column addition
    op.add_column('compliance_records', sa.Column('labeling_updated_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when labeling_status was last changed'))


def downgrade() -> None:
    # Only keep the necessary column removal
    op.drop_column('compliance_records', 'labeling_updated_at')
