"""Add recents to user table

Revision ID: 0003
Revises: 0002
Create Date: 2019-02-08 15:26:05.610240

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('recents', postgresql.ARRAY(sa.String()), nullable=True))
    op.execute("UPDATE public.user SET recents='{}'")
    op.alter_column('user', 'recents', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'recents')
    # ### end Alembic commands ###
