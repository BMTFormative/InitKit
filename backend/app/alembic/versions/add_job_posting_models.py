"""Add job posting models

Revision ID: xxx
Revises: latest
Create Date: 2025-01-XX
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

def upgrade():
    # JobPostingTemplate table
    op.create_table(
        'jobpostingtemplate',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        # ... other columns
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.ForeignKeyConstraint(['created_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # JobPosting table  
    op.create_table(
        'jobposting',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        # ... other columns with tenant isolation
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.ForeignKeyConstraint(['created_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('jobposting')
    op.drop_table('jobpostingtemplate')