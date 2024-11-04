"""Rename password to password_hash in User model

Revision ID: 6227be77874a
Revises: 5c71366aec58
Create Date: 2024-11-04 00:01:15.469180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6227be77874a'
down_revision = '5c71366aec58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=150), nullable=False))
        batch_op.drop_column('password')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', mysql.VARCHAR(length=150), nullable=False))
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###