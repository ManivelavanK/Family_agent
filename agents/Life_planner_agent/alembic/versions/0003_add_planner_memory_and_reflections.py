"""Add planner_memories and plan_reflections tables

Revision ID: 0003_add_planner_memory_and_reflections
Revises: 0002_add_calendar_events
Create Date: 2026-07-28

"""
from alembic import op
import sqlalchemy as sa

revision = '0003_memories_reflections'
down_revision = '0002_add_calendar_events'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'planner_memories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.String(length=100), nullable=False, server_default='default_family'),
        sa.Column('memory_type', sa.Enum('PREFERENCE', 'PAST_EVENT', 'PAST_TRIP', 'PAST_FUNCTION', 'GUEST_PATTERN', 'BUDGET_PATTERN', 'FOOD_PREFERENCE', 'DESTINATION_PREFERENCE', 'ACTIVITY_PREFERENCE', 'FEEDBACK', 'LESSON_LEARNED', 'PLANNING_CORRECTION', name='memorytype'), nullable=False, server_default='PREFERENCE'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(length=100), nullable=True, server_default='USER'),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('importance', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_planner_memories_id'), 'planner_memories', ['id'], unique=False)
    op.create_index(op.f('ix_planner_memories_family_id'), 'planner_memories', ['family_id'], unique=False)
    op.create_index(op.f('ix_planner_memories_memory_type'), 'planner_memories', ['memory_type'], unique=False)

    op.create_table(
        'plan_reflections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('what_went_well', sa.Text(), nullable=True),
        sa.Column('what_went_wrong', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('future_suggestions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plan_reflections_id'), 'plan_reflections', ['id'], unique=False)
    op.create_index(op.f('ix_plan_reflections_plan_id'), 'plan_reflections', ['plan_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_plan_reflections_plan_id'), table_name='plan_reflections')
    op.drop_index(op.f('ix_plan_reflections_id'), table_name='plan_reflections')
    op.drop_table('plan_reflections')
    op.drop_index(op.f('ix_planner_memories_memory_type'), table_name='planner_memories')
    op.drop_index(op.f('ix_planner_memories_family_id'), table_name='planner_memories')
    op.drop_index(op.f('ix_planner_memories_id'), table_name='planner_memories')
    op.drop_table('planner_memories')
