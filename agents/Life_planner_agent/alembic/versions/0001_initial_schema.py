"""Initial schema creation

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-07-28

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_type', sa.Enum('EVENT', 'FUNCTION', 'TRAVEL', name='plantype'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('number_of_people', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('budget', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.Enum('DRAFT', 'PLANNING', 'READY', 'APPROVED', 'COMPLETED', 'CANCELLED', name='planstatus'), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plans_id'), 'plans', ['id'], unique=False)

    op.create_table(
        'plan_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='taskpriority'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='taskstatus'), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plan_tasks_id'), 'plan_tasks', ['id'], unique=False)

    op.create_table(
        'budget_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('actual_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.Enum('ESTIMATED', 'PLANNED', 'PAID', name='budgetstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budget_items_id'), 'budget_items', ['id'], unique=False)

    op.create_table(
        'itinerary_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('activity', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_itinerary_items_id'), 'itinerary_items', ['id'], unique=False)

    op.create_table(
        'participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('relationship', sa.String(length=100), nullable=True),
        sa.Column('special_requirements', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_participants_id'), 'participants', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_participants_id'), table_name='participants')
    op.drop_table('participants')
    op.drop_index(op.f('ix_itinerary_items_id'), table_name='itinerary_items')
    op.drop_table('itinerary_items')
    op.drop_index(op.f('ix_budget_items_id'), table_name='budget_items')
    op.drop_table('budget_items')
    op.drop_index(op.f('ix_plan_tasks_id'), table_name='plan_tasks')
    op.drop_table('plan_tasks')
    op.drop_index(op.f('ix_plans_id'), table_name='plans')
    op.drop_table('plans')
