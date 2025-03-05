"""Add template_id column to testruntemplate table

Revision ID: add_template_id_to_testruntemplate
Revises: fix_testsuite_db_id
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_template_id_to_testruntemplate'
down_revision = 'fix_testsuite_db_id'
branch_labels = None
depends_on = None


def upgrade():
    # Check if the column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('testruntemplate')]
    
    if 'template_id' not in columns:
        # Add template_id column to testruntemplate table
        op.add_column('testruntemplate', sa.Column('template_id', sa.String(), nullable=True))
        
        # Set default values for existing rows - use the id as the template_id
        op.execute("UPDATE testruntemplate SET template_id = CAST(id AS TEXT)")
        
        # Make template_id not nullable after setting values
        op.alter_column('testruntemplate', 'template_id', nullable=False)


def downgrade():
    # Remove the column
    op.drop_column('testruntemplate', 'template_id')
