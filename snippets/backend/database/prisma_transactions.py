"""
Prisma-style Transactions in Python (using SQLAlchemy)
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

@contextmanager
def transaction(session: Session):
    """
    Transaction context manager
    """
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()

def create_user_with_profile(session: Session, user_data: dict, profile_data: dict):
    """
    Create user with profile in a transaction
    """
    with transaction(session):
        # Create user
        user = User(**user_data)
        session.add(user)
        session.flush()  # Get user.id

        # Create profile
        profile = Profile(**profile_data, user_id=user.id)
        session.add(profile)

        return user, profile

def transfer_funds(session: Session, from_account_id: int, to_account_id: int, amount: float):
    """
    Transfer funds between accounts atomically
    """
    with transaction(session):
        # Debit from source
        from_account = session.query(Account).filter_by(id=from_account_id).with_for_update().first()
        if not from_account or from_account.balance < amount:
            raise ValueError("Insufficient funds")

        from_account.balance -= amount

        # Credit to destination
        to_account = session.query(Account).filter_by(id=to_account_id).with_for_update().first()
        if not to_account:
            raise ValueError("Destination account not found")

        to_account.balance += amount

        # Create transaction record
        transaction_record = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount
        )
        session.add(transaction_record)

        return transaction_record

def batch_create_items(session: Session, items_data: list):
    """
    Batch create items in a transaction
    """
    with transaction(session):
        items = [Item(**data) for data in items_data]
        session.bulk_save_objects(items)
        return items

# Nested Transactions using Savepoints
def nested_transaction_example(session: Session):
    """
    Example of nested transactions using savepoints
    """
    try:
        # Start main transaction
        user = User(name="John", email="john@example.com")
        session.add(user)
        session.flush()

        # Create savepoint
        savepoint = session.begin_nested()

        try:
            # This might fail
            profile = Profile(user_id=user.id, bio="Bio")
            session.add(profile)
            session.flush()
        except Exception:
            # Rollback to savepoint
            savepoint.rollback()
            # Continue with main transaction

        session.commit()
    except Exception:
        session.rollback()
        raise
