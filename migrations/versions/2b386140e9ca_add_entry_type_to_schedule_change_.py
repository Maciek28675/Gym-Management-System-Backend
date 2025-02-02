"""Add entry type to schedule. Change employee_id and gym_class_id to nullable

Revision ID: 2b386140e9ca
Revises: f33747745e5e
Create Date: 2024-12-19 22:35:25.909805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b386140e9ca'
down_revision = 'f33747745e5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schedule', schema=None) as batch_op:
        batch_op.add_column(sa.Column('entry_type', sa.String(length=10), nullable=False))
        batch_op.alter_column('gymclass_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('employee_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schedule', schema=None) as batch_op:
        batch_op.alter_column('employee_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('gymclass_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('entry_type')

    # ### end Alembic commands ###
