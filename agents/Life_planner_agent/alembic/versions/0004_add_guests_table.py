"""Add guests table

Revision ID: 0004_add_guests_table
Revises: 0003_memories_reflections
Create Date: 2026-07-28

"""
from alembic import op
import sqlalchemy as sa

revision = '0004_add_guests_table'
down_revision = '0003_memories_reflections'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'guests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.String(length=100), nullable=False, server_default='default_family'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('relationship', sa.String(length=100), nullable=True),
        sa.Column('group_name', sa.String(length=100), nullable=True),
        sa.Column('adults', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('children', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('arrival_datetime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('departure_datetime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accommodation_info', sa.Text(), nullable=True),
        sa.Column('food_preferences', sa.Text(), nullable=True),
        sa.Column('dietary_restrictions', sa.Text(), nullable=True),
        sa.Column('special_requirements', sa.Text(), nullable=True),
        sa.Column('transport_info', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_guests_id'), 'guests', ['id'], unique=False)
    op.create_index(op.f('ix_guests_family_id'), 'guests', ['family_id'], unique=False)
    op.create_index(op.f('ix_guests_group_name'), 'guests', ['group_name'], unique=False)
    op.create_index(op.f('ix_guests_arrival_datetime'), 'guests', ['arrival_datetime'], unique=False)
    op.create_index(op.f('ix_guests_departure_datetime'), 'guests', ['departure_datetime'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_guests_departure_datetime'), table_name='guests')
    op.drop_index(op.f('ix_guests_arrival_datetime'), table_name='guests')
    op.drop_index(op.f('ix_guests_group_name'), table_name='guests')
    op.drop_index(op.f('ix_guests_family_id'), table_name='guests')
    op.drop_index(op.f('ix_guests_id'), table_name='guests')
    op.drop_table('guests')
