"""Initialize database

Revision ID: 0000
Revises:
Create Date: 2019-01-15 10:01:12.858779

"""
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.schema import Sequence, CreateSequence, DropSequence
import os
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0000'
down_revision = None
branch_labels = None
depends_on = None


# Create an ad-hoc table to use for the insert statement.
sequence_key_table = sa.table(
    'sequence_key',
    sa.column('seq_name', sa.String),
    sa.column('key_index', sa.Integer),
    sa.column('skip32_key', BYTEA),
)


def upgrade():
    op.execute(CreateSequence(Sequence("contact_seq")))
    op.execute(CreateSequence(Sequence("design_seq")))
    op.execute(CreateSequence(Sequence("user_seq")))
    op.execute(CreateSequence(Sequence("device_seq")))
    op.execute(CreateSequence(Sequence("invitation_seq")))

    op.create_table('sequence_key',
    sa.Column('seq_name', sa.String(), nullable=False),
    sa.Column('key_index', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('skip32_key', postgresql.BYTEA(length=10), nullable=False),
    sa.PrimaryKeyConstraint('seq_name', 'key_index', name=op.f('pk_sequence_key'))
    )
    op.bulk_insert(sequence_key_table, [{
        'seq_name': 'contact_seq',
        'key_index': 0,
        'skip32_key': os.urandom(10),
    }, {
        'seq_name': 'design_seq',
        'key_index': 0,
        'skip32_key': os.urandom(10),
    }, {
        'seq_name': 'user_seq',
        'key_index': 0,
        'skip32_key': os.urandom(10),
    }, {
        'seq_name': 'device_seq',
        'key_index': 0,
        'skip32_key': os.urandom(10),
    }, {
        'seq_name': 'invitation_seq',
        'key_index': 0,
        'skip32_key': os.urandom(10),
    }])

    op.create_table('contact',
    sa.Column('id', sa.String(), server_default=sa.text("skip32_hex_seq(nextval('contact_seq'), 'contact_seq')"), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_contact'))
    )
    op.create_table('design',
    sa.Column('id', sa.String(), server_default=sa.text("skip32_hex_seq(nextval('design_seq'), 'design_seq')"), nullable=False),
    sa.Column('distribution_id', sa.String(), nullable=True),
    sa.Column('wc_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('wallet_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_design'))
    )
    op.create_table('user',
    sa.Column('id', sa.String(), server_default=sa.text("skip32_hex_seq(nextval('user_seq'), 'user_seq')"), nullable=False),
    sa.Column('wc_id', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('username', name=op.f('uq_user_username'))
    )
    op.create_index(op.f('ix_user_wc_id'), 'user', ['wc_id'], unique=True)
    op.create_table('device',
    sa.Column('id', sa.String(), server_default=sa.text("skip32_hex_seq(nextval('device_seq'), 'device_seq')"), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('expo_token', sa.String(), nullable=True),
    sa.Column('last_used', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('os', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_device_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_device'))
    )
    op.create_index(op.f('ix_device_password'), 'device', ['password'], unique=True)
    op.create_table('invitation',
    sa.Column('id', sa.String(), server_default=sa.text("skip32_hex_seq(nextval('invitation_seq'), 'invitation_seq')"), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('recipient', sa.String(), nullable=False),
    sa.Column('status', sa.String(), server_default='pending', nullable=False),
    sa.Column('response', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_invitation_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_invitation'))
    )
    op.create_index(op.f('ix_invitation_user_id'), 'invitation', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_invitation_user_id'), table_name='invitation')
    op.drop_table('invitation')
    op.drop_index(op.f('ix_device_password'), table_name='device')
    op.drop_table('device')
    op.drop_index(op.f('ix_user_wc_id'), table_name='user')
    op.drop_table('user')
    op.drop_table('design')
    op.drop_table('contact')

    op.drop_table('sequence_key')
    op.execute(DropSequence(Sequence("contact_seq")))
    op.execute(DropSequence(Sequence("design_seq")))
    op.execute(DropSequence(Sequence("user_seq")))
    op.execute(DropSequence(Sequence("device_seq")))
    op.execute(DropSequence(Sequence("invitation_seq")))
