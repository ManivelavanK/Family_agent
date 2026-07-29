"""Add calendar_events table

Revision ID: 0002_add_calendar_events
Revises: 0001_initial_schema
Create Date: 2026-07-28

"""
from alembic import op
import sqlalchemy as sa

revision = '0002_add_calendar_events'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.Enum('FAMILY_EVENT', 'BIRTHDAY', 'ANNIVERSARY', 'FUNCTION', 'TRAVEL', 'APPOINTMENT', 'STUDY_EXAM', 'GUEST_VISIT', 'PERSONAL', 'REMINDER', 'OTHER', name='eventtype'), nullable=False, server_default='OTHER'),
        sa.Column('start_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('all_day', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', name='eventstatus'), nullable=False, server_default='SCHEDULED'),
        sa.Column('priority', sa.String(length=50), nullable=True, server_default='MEDIUM'),
        sa.Column('source', sa.String(length=100), nullable=True, server_default='USER'),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calendar_events_id'), 'calendar_events', ['id'], unique=False)
    op.create_index(op.f('ix_calendar_events_start_datetime'), 'calendar_events', ['start_datetime'], unique=False)
    op.create_index(op.f('ix_calendar_events_end_datetime'), 'calendar_events', ['end_datetime'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_calendar_events_end_datetime'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_start_datetime'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_id'), table_name='calendar_events')
    op.drop_table('calendar_events')
