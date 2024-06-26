"""Users

Revision ID: 9cdb2f8716ec
Revises: 1da85794788a
Create Date: 2024-03-30 05:32:14.584758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cdb2f8716ec'
down_revision = '1da85794788a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('relative_users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('userid', sa.String(length=255), nullable=False, comment='通知人员企业微信id'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
    sa.PrimaryKeyConstraint('id'),
    comment='通知人员表'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('relative_users')
    # ### end Alembic commands ###
