"""Add case_id column to testcase table

Revision ID: add_case_id_to_testcase
Revises: add_timestamps_to_testrun
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_case_id_to_testcase'
down_revision = 'add_timestamps_to_testrun'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('testcase')]
    
    if 'case_id' not in columns:
        # Add case_id column to testcase table
        op.add_column('testcase', sa.Column('case_id', sa.String(), nullable=True))
        
        # Set default values for existing rows - use the id as the case_id
        op.execute("UPDATE testcase SET case_id = CAST(id AS TEXT)")
        
        # Make case_id not nullable after setting values
        op.alter_column('testcase', 'case_id', nullable=False)


def downgrade():
    # Remove the column
    op.drop_column('testcase', 'case_id')
