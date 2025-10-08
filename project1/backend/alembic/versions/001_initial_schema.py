"""Initial schema for ONLSuggest admin

Revision ID: 001
Revises:
Create Date: 2025-10-07 23:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create gemeentes table
    op.create_table(
        'gemeentes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create services table
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('keywords', postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create associations table
    op.create_table(
        'associations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('gemeente_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['gemeente_id'], ['gemeentes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gemeente_id', 'service_id', name='unique_gemeente_service')
    )

    # Insert demo data
    op.execute("""
        INSERT INTO gemeentes (name, metadata) VALUES
        ('Amsterdam', '{"province": "Noord-Holland"}'),
        ('Rotterdam', '{"province": "Zuid-Holland"}'),
        ('Utrecht', '{"province": "Utrecht"}');
    """)

    op.execute("""
        INSERT INTO services (name, description, category, keywords) VALUES
        ('Parkeervergunning', 'Vraag een parkeervergunning aan voor uw auto', 'Verkeer',
         ARRAY['parkeer', 'parkeren', 'auto', 'vergunning']),
        ('Paspoort aanvragen', 'Vraag een nieuw paspoort aan', 'Identiteit',
         ARRAY['paspoort', 'reisdocument', 'identiteitsbewijs']),
        ('Verhuizing doorgeven', 'Geef uw verhuizing door aan de gemeente', 'Burgerzaken',
         ARRAY['verhuizen', 'verhuizing', 'adreswijziging', 'inschrijven']),
        ('Trouwen', 'Informatie over trouwen bij de gemeente', 'Burgerzaken',
         ARRAY['trouwen', 'huwelijk', 'trouwakte']);
    """)

    # Create all associations (all services available in all gemeentes)
    op.execute("""
        INSERT INTO associations (gemeente_id, service_id)
        SELECT g.id, s.id
        FROM gemeentes g CROSS JOIN services s;
    """)


def downgrade():
    op.drop_table('associations')
    op.drop_table('services')
    op.drop_table('gemeentes')
