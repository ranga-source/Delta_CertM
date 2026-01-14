"""Add compliance task workflow tables

Revision ID: 20251209_add_compliance_tasks
Revises: 
Create Date: 2025-12-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '20251209_add_compliance_tasks'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('compliance_tasks'):
        op.create_table(
            'compliance_tasks',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
            sa.Column('record_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('compliance_records.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='TODO'),
            sa.Column('assignee', sa.String(length=100), nullable=True),
            sa.Column('created_by', sa.String(length=100), nullable=True),
            sa.Column('updated_by', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        )
        op.create_index('ix_compliance_tasks_record_id', 'compliance_tasks', ['record_id'])

    if not inspector.has_table('compliance_task_notes'):
        op.create_table(
            'compliance_task_notes',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
            sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('compliance_tasks.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('note', sa.Text(), nullable=False),
            sa.Column('author', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_compliance_task_notes_task_id', 'compliance_task_notes', ['task_id'])


def downgrade():
    op.drop_index('ix_compliance_task_notes_task_id', table_name='compliance_task_notes')
    op.drop_table('compliance_task_notes')
    op.drop_index('ix_compliance_tasks_record_id', table_name='compliance_tasks')
    op.drop_table('compliance_tasks')


