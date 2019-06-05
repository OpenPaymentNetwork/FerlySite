"""Add card_request table

Revision ID: 0008
Revises: 0007
Create Date: 2019-06-04 15:41:56.634826

"""
from alembic import op
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.schema import Sequence, CreateSequence, DropSequence
import os
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None

sequence_key_table = sa.table(
    'sequence_key',
    sa.column('seq_name', sa.String),
    sa.column('key_index', sa.Integer),
    sa.column('skip32_key', BYTEA),
)


def upgrade():
    op.bulk_insert(sequence_key_table, [{
        'seq_name': 'card_request_seq',
        'key_index': 0,
        'skip32_key': os.urandom(10),
    }])
    op.execute(CreateSequence(Sequence("card_request_seq")))
    op.create_table('card_request',
    sa.Column('id', sa.String(), server_default=sa.text("skip32_hex_seq(nextval('card_request_seq'), 'card_request_seq')"), nullable=False),
    sa.Column('customer_id', sa.String(), nullable=False),
    sa.Column('name', sa.Unicode(), nullable=False),
    sa.Column('original_line1', sa.Unicode(), nullable=False),
    sa.Column('original_line2', sa.Unicode(), nullable=True),
    sa.Column('original_city', sa.Unicode(), nullable=False),
    sa.Column('original_state', sa.Unicode(), nullable=False),
    sa.Column('original_zip_code', sa.Unicode(), nullable=False),
    sa.Column('line1', sa.Unicode(), nullable=False),
    sa.Column('line2', sa.Unicode(), nullable=True),
    sa.Column('city', sa.Unicode(), nullable=False),
    sa.Column('state', sa.Unicode(), nullable=False),
    sa.Column('zip_code', sa.Unicode(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('downloaded', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_card_request'))
    )
    op.create_index(op.f('ix_card_request_customer_id'), 'card_request', ['customer_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_card_request_customer_id'), table_name='card_request')
    op.drop_table('card_request')
    op.execute(DropSequence(Sequence("card_request_seq")))
    op.execute("DELETE FROM sequence_key WHERE seq_name = 'card_request_seq'")
