"""Change User to Customer

Revision ID: 0005
Revises: 0004
Create Date: 2019-04-08 14:02:43.421604

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('user', 'customer')
    op.execute("UPDATE sequence_key SET seq_name='customer_seq' WHERE seq_name='user_seq'")
    op.execute('ALTER SEQUENCE user_seq RENAME TO customer_seq')
    op.alter_column('customer', 'id', server_default=sa.text("skip32_hex_seq(nextval('customer_seq'), 'customer_seq')"))
    op.execute('ALTER INDEX pk_user RENAME TO pk_customer')
    op.execute('ALTER INDEX ix_user_wc_id RENAME TO ix_customer_wc_id')
    op.execute('ALTER INDEX uq_user_username RENAME TO uq_customer_username')
    op.alter_column('device', 'user_id', new_column_name='customer_id')
    op.drop_constraint('fk_device_user_id_user', 'device', type_='foreignkey')
    op.create_foreign_key(op.f('fk_device_customer_id_customer'), 'device', 'customer', ['customer_id'], ['id'])
    op.alter_column('invitation', 'user_id', new_column_name='customer_id')
    op.drop_constraint('fk_invitation_user_id_user', 'invitation', type_='foreignkey')
    op.create_foreign_key(op.f('fk_invitation_customer_id_customer'), 'invitation', 'customer', ['customer_id'], ['id'])
    op.create_index(op.f('ix_invitation_customer_id'), 'invitation', ['customer_id'], unique=False)
    op.drop_index('ix_invitation_user_id', table_name='invitation')

def downgrade():
    op.rename_table('customer', 'user')
    op.execute("UPDATE sequence_key SET seq_name='user_seq' WHERE seq_name='customer_seq'")
    op.execute('ALTER SEQUENCE customer_seq RENAME TO user_seq')
    op.alter_column('user', 'id', server_default=sa.text("skip32_hex_seq(nextval('user_seq'), 'user_seq')"))
    op.execute('ALTER INDEX pk_customer RENAME TO pk_user')
    op.execute('ALTER INDEX ix_customer_wc_id RENAME TO ix_user_wc_id')
    op.execute('ALTER INDEX uq_customer_username RENAME TO uq_user_username')
    op.alter_column('device', 'customer_id', new_column_name='user_id')
    op.drop_constraint('fk_device_customer_id_customer', 'device', type_='foreignkey')
    op.create_foreign_key(op.f('fk_device_user_id_user'), 'device', 'user', ['user_id'], ['id'])
    op.alter_column('invitation', 'customer_id', new_column_name='user_id')
    op.drop_constraint('fk_invitation_customer_id_customer', 'invitation', type_='foreignkey')
    op.create_foreign_key(op.f('fk_invitation_user_id_user'), 'invitation', 'user', ['user_id'], ['id'])
    op.create_index(op.f('ix_invitation_user_id'), 'invitation', ['user_id'], unique=False)
    op.drop_index('ix_invitation_customer_id', table_name='invitation')
