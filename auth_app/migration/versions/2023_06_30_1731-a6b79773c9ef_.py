"""empty message

Revision ID: a6b79773c9ef
Revises: 
Create Date: 2023-06-30 17:31:15.670942

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6b79773c9ef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('permissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('can_create_client', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_create_manager', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_get_client', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_get_manager', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_update_client', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_update_manager', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_delete_client', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_delete_manager', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_delete_session_client', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_delete_session_manager', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_create_dress', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_get_dress', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_update_dress', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_delete_dress', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_create_review', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_get_review', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_update_review', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.Column('can_delete_review', sa.Boolean(), server_default='FALSE', nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('permissions', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permissions'], ['permissions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('unverified_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('reg_token', sa.String(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('reg_token')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('sessions',
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('token')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions')
    op.drop_table('users')
    op.drop_table('unverified_users')
    op.drop_table('role')
    op.drop_table('permissions')
    # ### end Alembic commands ###