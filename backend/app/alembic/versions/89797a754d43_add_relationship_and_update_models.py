"""Add relationship and update models

Revision ID: 89797a754d43
Revises: 918534d35f42
Create Date: 2025-02-15 17:06:24.701170

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '89797a754d43'
down_revision = '918534d35f42'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('department', sa.Column('organization_id', sa.Uuid(), nullable=False))
    op.create_foreign_key(None, 'department', 'organization', ['organization_id'], ['id'])
    op.add_column('specialist', sa.Column('department_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'specialist', 'department', ['department_id'], ['id'])
    op.add_column('task', sa.Column('user_id', sa.Uuid(), nullable=False))
    op.add_column('task', sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.alter_column('task', 'appeal_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_constraint('task_responsible_user_id_fkey', 'task', type_='foreignkey')
    op.create_foreign_key(None, 'task', 'user', ['user_id'], ['id'])
    op.drop_column('task', 'responsible_user_id')
    op.add_column('user', sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'full_name')
    op.add_column('task', sa.Column('responsible_user_id', sa.UUID(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.create_foreign_key('task_responsible_user_id_fkey', 'task', 'user', ['responsible_user_id'], ['id'])
    op.alter_column('task', 'appeal_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('task', 'description')
    op.drop_column('task', 'user_id')
    op.drop_constraint(None, 'specialist', type_='foreignkey')
    op.drop_column('specialist', 'department_id')
    op.drop_constraint(None, 'department', type_='foreignkey')
    op.drop_column('department', 'organization_id')
    # ### end Alembic commands ###
