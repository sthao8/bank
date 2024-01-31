"""initial migration

Revision ID: 7babadd039e4
Revises: 
Create Date: 2024-01-30 20:00:20.982944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7babadd039e4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Countries',
    sa.Column('country_code', sa.String(length=2), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('telephone_country_code', sa.String(length=5), nullable=False),
    sa.PrimaryKeyConstraint('country_code')
    )
    op.create_table('Users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('role', sa.String(length=7), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('address', sa.String(length=50), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('postal_code', sa.String(length=10), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('national_id', sa.String(length=20), nullable=False),
    sa.Column('telephone', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('country', sa.String(length=2), nullable=False),
    sa.ForeignKeyConstraint(['country'], ['Countries.country_code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_type', sa.String(length=10), nullable=False),
    sa.Column('created', sa.Date(), nullable=False),
    sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['Customers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('operation', sa.String(length=50), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('new_balance', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['Accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Transactions')
    op.drop_table('Accounts')
    op.drop_table('Customers')
    op.drop_table('Users')
    op.drop_table('Countries')
    # ### end Alembic commands ###