"""Add field_color column

Revision ID: 0011
Revises: 0010
Create Date: 2019-08-06 16:36:47.037186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('design', sa.Column('field_color', sa.String(), nullable=True))
    op.add_column('design', sa.Column('field_dark', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('design', 'field_color')
    op.drop_column('design', 'field_dark')
