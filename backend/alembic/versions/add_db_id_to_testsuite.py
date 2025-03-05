"""Add db_id column to testsuite table

Revision ID: add_db_id_to_testsuite
Revises: update_testsuite_model
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_db_id_to_testsuite'
down_revision = 'update_testsuite_model'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('testsuite')]
    
    if 'db_id' not in columns:
        # Add db_id column to testsuite table
        op.add_column('testsuite', sa.Column('db_id', sa.Integer(), nullable=True))
        
        # Set default values for existing rows - use the ROWID as the db_id
        op.execute("UPDATE testsuite SET db_id = ROWID")
        
        # Make db_id not nullable
        op.alter_column('testsuite', 'db_id', nullable=False)
        
        # Check if primary key constraint exists
        try:
            # Make db_id the primary key
            op.create_primary_key('pk_testsuite', 'testsuite', ['db_id'])
        except Exception as e:
            print(f"Note: Could not create primary key: {e}")


def downgrade():
    # Check if the column exists before trying to remove it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('testsuite')]
    
    if 'db_id' in columns:
        # Remove the primary key constraint
        op.drop_constraint('pk_testsuite', 'testsuite', type_='primary')
        
        # Remove the column
        op.drop_column('testsuite', 'db_id')
