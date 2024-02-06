"""remaned rolesusers table

Revision ID: bb659765197a
Revises: ff2f400d7df8
Create Date: 2024-02-05 16:36:16.895071

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bb659765197a'
down_revision = 'ff2f400d7df8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('RolesUsers',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['Roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], )
    )
    op.drop_table('roles_users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles_users',
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('role_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['Roles.id'], name='roles_users_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], name='roles_users_ibfk_2'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('RolesUsers')
    # ### end Alembic commands ###