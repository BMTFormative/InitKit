"""add_credit_limit_to_subscriptionplan

Revision ID: f2b3c4d5e6f7
Revises: e1a2b3c4d5e6
Create Date: 2025-05-21 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f2b3c4d5e6f7'
down_revision = 'e1a2b3c4d5e6'
branch_labels = None
depends_on = None

def upgrade():
    # Add credit_limit column to subscriptionplan
    op.add_column(
        'subscriptionplan',
        sa.Column(
            'credit_limit',
            sa.Float(),
            nullable=False,
            server_default='0'
        )
    )

def downgrade():
    # Remove credit_limit column
    op.drop_column('subscriptionplan', 'credit_limit')