"""add_authorized_merchant

Revision ID: 0016
Revises: 0015
Create Date: 2020-03-23 13:11:33.899530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('design', sa.Column('authorized_merchant', sa.Boolean(), server_default='False', nullable=False))


def downgrade():
    op.drop_column('design', 'authorized_merchant')
