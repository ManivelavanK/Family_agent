"""add_family_routines

Revision ID: 0005_add_family_routines
Revises: 0004_add_guests_table
Create Date: 2026-07-28 22:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0005_add_family_routines'
down_revision = '0004_add_guests_table'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'family_routines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.String(length=100), nullable=False),
        sa.Column('member_name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='routinepriority'), nullable=False),
        sa.Column('status', sa.Enum('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', name='routinestatus'), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_family_routines_id'), 'family_routines', ['id'], unique=False)
    op.create_index(op.f('ix_family_routines_family_id'), 'family_routines', ['family_id'], unique=False)
    op.create_index(op.f('ix_family_routines_member_name'), 'family_routines', ['member_name'], unique=False)
    op.create_index(op.f('ix_family_routines_scheduled_start'), 'family_routines', ['scheduled_start'], unique=False)
    op.create_index(op.f('ix_family_routines_scheduled_end'), 'family_routines', ['scheduled_end'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_family_routines_scheduled_end'), table_name='family_routines')
    op.drop_index(op.f('ix_family_routines_scheduled_start'), table_name='family_routines')
    op.drop_index(op.f('ix_family_routines_member_name'), table_name='family_routines')
    op.drop_index(op.f('ix_family_routines_family_id'), table_name='family_routines')
    op.drop_index(op.f('ix_family_routines_id'), table_name='family_routines')
    op.drop_table('family_routines')
