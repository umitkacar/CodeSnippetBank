"""
Prisma-style Transactions in Python (using SQLAlchemy)
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.orm import Session, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Dict, List, Any, Tuple, Optional

Base = declarative_base()

# Example Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    profiles = relationship('Profile', back_populates='user')

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bio = Column(String)
    user = relationship('User', back_populates='profiles')

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    from_account_id = Column(Integer, ForeignKey('accounts.id'))
    to_account_id = Column(Integer, ForeignKey('accounts.id'))
    amount = Column(Float, nullable=False)

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

@contextmanager
def transaction(session: Session):
    """
    Transaction context manager
    """
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def create_user_with_profile(session: Session, user_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Tuple[User, Profile]:
    """
    Create user with profile in a transaction
    """
    try:
        with transaction(session):
            # Create user
            user = User(**user_data)
            session.add(user)
            session.flush()  # Get user.id

            # Create profile
            profile = Profile(**profile_data, user_id=user.id)
            session.add(profile)

            return user, profile
    except Exception as e:
        raise Exception(f"Failed to create user with profile: {str(e)}")

def transfer_funds(session: Session, from_account_id: int, to_account_id: int, amount: float) -> Transaction:
    """
    Transfer funds between accounts atomically
    """
    try:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with transaction(session):
            # Debit from source
            from_account = session.query(Account).filter_by(id=from_account_id).with_for_update().first()
            if not from_account:
                raise ValueError("Source account not found")
            if from_account.balance < amount:
                raise ValueError(f"Insufficient funds. Available: {from_account.balance}, Required: {amount}")

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
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to transfer funds: {str(e)}")

def batch_create_items(session: Session, items_data: List[Dict[str, Any]]) -> List[Item]:
    """
    Batch create items in a transaction
    """
    try:
        with transaction(session):
            items = [Item(**data) for data in items_data]
            session.bulk_save_objects(items)
            return items
    except Exception as e:
        raise Exception(f"Failed to batch create items: {str(e)}")

# Nested Transactions using Savepoints
def nested_transaction_example(session: Session, user_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Optional[User]:
    """
    Example of nested transactions using savepoints
    """
    try:
        # Start main transaction
        user = User(**user_data)
        session.add(user)
        session.flush()

        # Create savepoint
        savepoint = session.begin_nested()

        try:
            # This might fail
            profile = Profile(**profile_data, user_id=user.id)
            session.add(profile)
            session.flush()
        except Exception as e:
            # Rollback to savepoint
            savepoint.rollback()
            # Continue with main transaction without profile
            print(f"Profile creation failed: {e}, but user will be created")

        session.commit()
        return user
    except Exception as e:
        session.rollback()
        raise Exception(f"Failed to create user: {str(e)}")

def safe_update_account(session: Session, account_id: int, new_balance: float) -> Account:
    """
    Safely update account balance with error handling
    """
    try:
        with transaction(session):
            account = session.query(Account).filter_by(id=account_id).with_for_update().first()
            if not account:
                raise ValueError(f"Account with id {account_id} not found")

            if new_balance < 0:
                raise ValueError("Balance cannot be negative")

            account.balance = new_balance
            return account
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to update account: {str(e)}")
