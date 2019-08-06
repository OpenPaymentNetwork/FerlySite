"""add staff tokens

Revision ID: 0010
Revises: 0009
Create Date: 2019-08-06 13:12:20.724342

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'staff_token',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('secret_sha256', sa.String(), nullable=False),
        sa.Column('tokens_fernet', sa.String(), nullable=False),
        sa.Column('created', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column('update_ts', sa.DateTime(), nullable=False),
        sa.Column('expires', sa.DateTime(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=False),
        sa.Column('remote_addr', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('groups', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('id_claims', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_staff_token'))
    )


def downgrade():
    op.drop_table('staff_token')
