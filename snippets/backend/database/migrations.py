"""Database Migrations with Alembic"""
from alembic import op
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone


def upgrade_create_users_table() -> None:
    """Create users table"""
    try:
        op.create_table(
            'users',
            Column('id', Integer, primary_key=True),
            Column('email', String(255), unique=True, nullable=False),
            Column('username', String(100), unique=True, nullable=False),
            Column('password_hash', String(255), nullable=False),
            Column('is_active', Boolean, default=True),
            Column('is_admin', Boolean, default=False),
            Column('created_at', DateTime, default=lambda: datetime.now(timezone.utc)),
            Column('updated_at', DateTime, onupdate=lambda: datetime.now(timezone.utc))
        )
        op.create_index('idx_users_email', 'users', ['email'])
        op.create_index('idx_users_username', 'users', ['username'])
    except Exception as e:
        raise Exception(f"Failed to create users table: {str(e)}")


def downgrade_drop_users_table() -> None:
    """Drop users table"""
    try:
        op.drop_index('idx_users_username', 'users')
        op.drop_index('idx_users_email', 'users')
        op.drop_table('users')
    except Exception as e:
        raise Exception(f"Failed to drop users table: {str(e)}")


def upgrade_add_column(table_name: str, column_name: str, column_type: Any) -> None:
    """Add a column to existing table"""
    try:
        op.add_column(table_name, Column(column_name, column_type))
    except Exception as e:
        raise Exception(f"Failed to add column: {str(e)}")


def downgrade_drop_column(table_name: str, column_name: str) -> None:
    """Remove a column from table"""
    try:
        op.drop_column(table_name, column_name)
    except Exception as e:
        raise Exception(f"Failed to drop column: {str(e)}")


def upgrade_create_index(index_name: str, table_name: str, columns: list) -> None:
    """Create an index"""
    try:
        op.create_index(index_name, table_name, columns)
    except Exception as e:
        raise Exception(f"Failed to create index: {str(e)}")


def downgrade_drop_index(index_name: str, table_name: str) -> None:
    """Drop an index"""
    try:
        op.drop_index(index_name, table_name)
    except Exception as e:
        raise Exception(f"Failed to drop index: {str(e)}")
