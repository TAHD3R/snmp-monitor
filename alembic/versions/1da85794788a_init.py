"""Init

Revision ID: 1da85794788a
Revises: 
Create Date: 2024-03-30 01:52:48.983927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1da85794788a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('location', sa.String(length=255), nullable=False, comment='数据所属传感器位置'),
    sa.Column('temperature', sa.Float(), nullable=False, comment='温度'),
    sa.Column('humidity', sa.Float(), nullable=False, comment='湿度'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
    sa.PrimaryKeyConstraint('id'),
    comment='温湿度数据表'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('log')
    # ### end Alembic commands ###
