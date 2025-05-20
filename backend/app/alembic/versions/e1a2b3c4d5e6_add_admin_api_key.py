"""add_admin_api_key

Revision ID: e1a2b3c4d5e6
Revises: d4a76dd79f7a
Create Date: 2025-05-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision = 'e1a2b3c4d5e6'
down_revision = 'd4a76dd79f7a'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'adminapikey',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('encrypted_key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('adminapikey')