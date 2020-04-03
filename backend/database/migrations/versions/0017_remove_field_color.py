"""remove field_color

Revision ID: 0017
Revises: 0016
Create Date: 2020-04-03 09:39:50.937780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0017'
down_revision = '0016'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('design', 'field_color')
    op.drop_column('design', 'field_dark')


def downgrade():
    op.add_column('design', sa.Column('field_color', sa.String(), nullable=True))
    op.add_column('design', sa.Column('field_dark', sa.Boolean(), nullable=True))