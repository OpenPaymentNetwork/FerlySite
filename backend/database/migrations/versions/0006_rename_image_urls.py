"""Rename image urls

Revision ID: 0006
Revises: 0005
Create Date: 2019-04-09 10:39:20.099531

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('customer', 'image_url', new_column_name='profile_image_url')
    op.alter_column('design', 'wallet_url', new_column_name='wallet_image_url')
    op.alter_column('design', 'image_url', new_column_name='logo_image_url')


def downgrade():
    op.alter_column('customer', 'profile_image_url', new_column_name='image_url')
    op.alter_column('design', 'wallet_image_url', new_column_name='wallet_url')
    op.alter_column('design', 'logo_image_url', new_column_name='image_url')
