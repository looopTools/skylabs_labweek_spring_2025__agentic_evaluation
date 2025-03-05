"""Add timestamps to testrun table

Revision ID: add_timestamps_to_testrun
Revises: 
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_timestamps_to_testrun'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns already exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('testrun')]
    
    # Add created_at column if it doesn't exist
    if 'created_at' not in columns:
        op.add_column('testrun', sa.Column('created_at', sa.DateTime(), nullable=True))
    
    # Add updated_at column if it doesn't exist
    if 'updated_at' not in columns:
        op.add_column('testrun', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE testrun SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP")


def downgrade():
    # Remove the columns
    op.drop_column('testrun', 'updated_at')
    op.drop_column('testrun', 'created_at')
