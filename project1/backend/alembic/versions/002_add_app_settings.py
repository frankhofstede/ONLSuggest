"""Add app_settings table for Epic 3 Story 3.1

Revision ID: 002
Revises: 001
Create Date: 2025-10-11 00:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create app_settings table
    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # Insert default setting: suggestion_engine = 'template'
    op.execute("""
        INSERT INTO app_settings (key, value, description) VALUES
        ('suggestion_engine', 'template', 'Active suggestion engine: template or koop');
    """)


def downgrade():
    op.drop_table('app_settings')
