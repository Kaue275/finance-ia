"""create first table

Revision ID: 388083f5571d
Revises: 
Create Date: 2026-10-23 09:57:51.339142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '388083f5571d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), unique=True, nullable=False),
        sa.Column('password', sa.String(length=100), nullable=False)
    )

    op.create_table(
        'groups',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('user_id', sa.Uuid(as_uuid=True), 
        sa.ForeignKey('users.id'), nullable=False)
    )

    op.create_table(
        'sheet',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('group_id', sa.Uuid(as_uuid=True), sa.ForeignKey('groups.id'), nullable=False)
    )

    op.create_table(
        'cell',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('sheet_id', sa.Uuid(as_uuid=True), 
        sa.ForeignKey('sheet.id'), nullable=False) 
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('cell')
    op.drop_table('sheet')
    op.drop_table('groups')
    op.drop_table('users')
