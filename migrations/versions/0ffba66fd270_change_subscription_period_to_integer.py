"""Change Subscription period to Integer

Revision ID: 0ffba66fd270
Revises: d53867a1fc40
Create Date: 2024-12-19 19:16:07.197893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ffba66fd270'
down_revision = 'd53867a1fc40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscription', schema=None) as batch_op:
        batch_op.alter_column('period',
               existing_type=sa.DATE(),
               type_=sa.Integer(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscription', schema=None) as batch_op:
        batch_op.alter_column('period',
               existing_type=sa.Integer(),
               type_=sa.DATE(),
               existing_nullable=False)

    # ### end Alembic commands ###
