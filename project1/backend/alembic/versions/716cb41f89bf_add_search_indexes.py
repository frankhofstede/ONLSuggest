"""add_search_indexes

Revision ID: 716cb41f89bf
Revises: e67c9881959b
Create Date: 2025-10-07 16:50:58.592296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '716cb41f89bf'
down_revision: Union[str, None] = 'e67c9881959b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create indexes for suggestion query performance
    # Index on services.name for ILIKE queries
    op.create_index(
        'ix_services_name_lower',
        'services',
        [sa.text('LOWER(name)')],
        postgresql_using='btree'
    )

    # Index on gemeentes.name for ILIKE queries
    op.create_index(
        'ix_gemeentes_name_lower',
        'gemeentes',
        [sa.text('LOWER(name)')],
        postgresql_using='btree'
    )

    # GIN index on services.keywords array for faster array searches
    op.create_index(
        'ix_services_keywords_gin',
        'services',
        ['keywords'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_services_keywords_gin', table_name='services')
    op.drop_index('ix_gemeentes_name_lower', table_name='gemeentes')
    op.drop_index('ix_services_name_lower', table_name='services')
