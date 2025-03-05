"""Fix testsuite db_id column

Revision ID: fix_testsuite_db_id
Revises: add_db_id_to_testsuite
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'fix_testsuite_db_id'
down_revision = 'add_db_id_to_testsuite'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('testsuite')]
    
    # If db_id doesn't exist, add it
    if 'db_id' not in columns:
        # Add db_id column
        op.add_column('testsuite', sa.Column('db_id', sa.Integer(), nullable=True))
        
        # Set default values using ROWID
        op.execute("UPDATE testsuite SET db_id = ROWID")
        
        # Make db_id not nullable
        op.alter_column('testsuite', 'db_id', nullable=False)
        
        # Try to make db_id the primary key
        try:
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
