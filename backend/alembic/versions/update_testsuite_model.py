"""Update TestSuite model

Revision ID: update_testsuite_model
Revises: add_case_id_to_testcase
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'update_testsuite_model'
down_revision = 'add_case_id_to_testcase'
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('testsuite')]
    
    # Only perform the rename if 'id' exists and 'db_id' doesn't
    if 'id' in columns and 'db_id' not in columns:
        # Rename id column to db_id
        op.alter_column('testsuite', 'id', new_column_name='db_id')
        
        # Add new id column for string identifier
        op.add_column('testsuite', sa.Column('id', sa.String(), nullable=True))
        
        # Set default values for existing rows - use the db_id as the id
        op.execute("UPDATE testsuite SET id = CAST(db_id AS TEXT)")
        
        # Make id not nullable after setting values
        op.alter_column('testsuite', 'id', nullable=False)


def downgrade():
    # Drop the new id column
    op.drop_column('testsuite', 'id')
    
    # Rename db_id back to id
    op.alter_column('testsuite', 'db_id', new_column_name='id')
