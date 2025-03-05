"""add indexes to testsuite

Revision ID: add_indexes_to_testsuite
Revises: update_testsuite_model
Create Date: 2024-03-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_indexes_to_testsuite'
down_revision = 'update_testsuite_model'
branch_labels = None
depends_on = None

def upgrade():
    # Add indexes for commonly queried fields
    op.create_index(
        'ix_testsuite_name',
        'testsuite',
        ['name'],
        unique=False
    )
    op.create_index(
        'ix_testsuite_format',
        'testsuite',
        ['format'],
        unique=False
    )
    op.create_index(
        'ix_testsuite_version',
        'testsuite',
        ['version'],
        unique=False
    )
    op.create_index(
        'ix_testsuite_is_final',
        'testsuite',
        ['is_final'],
        unique=False
    )

def downgrade():
    # Remove indexes
    op.drop_index('ix_testsuite_name', table_name='testsuite')
    op.drop_index('ix_testsuite_format', table_name='testsuite')
    op.drop_index('ix_testsuite_version', table_name='testsuite')
    op.drop_index('ix_testsuite_is_final', table_name='testsuite')