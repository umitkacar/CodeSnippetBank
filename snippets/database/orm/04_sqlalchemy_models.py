"""
============================================================================
SQLAlchemy Models, Relationships, and Queries
============================================================================
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, Text,
    Numeric, Enum, ForeignKey, Table, Index, func, and_, or_, select
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship, sessionmaker, Session, joinedload, selectinload
)
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from typing import List, Optional
import uuid
import enum

# Database setup
engine = create_engine('postgresql://user:password@localhost/myapp', echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ============================================================================
# Models
# ============================================================================

# Snippet 1: Basic model with relationships
class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(Enum('user', 'admin', 'moderator', name='user_role'), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship('Profile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    posts = relationship('Post', back_populates='author', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

# Snippet 2: One-to-One relationship
class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bio = Column(Text, nullable=True)
    avatar = Column(String, nullable=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='profile')

# Snippet 3: Many-to-Many association table
post_categories = Table(
    'post_categories',
    Base.metadata,
    Column('post_id', String, ForeignKey('posts.id', ondelete='CASCADE')),
    Column('category_id', String, ForeignKey('categories.id', ondelete='CASCADE'))
)

post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', String, ForeignKey('posts.id', ondelete='CASCADE')),
    Column('tag_id', String, ForeignKey('tags.id', ondelete='CASCADE'))
)

# Snippet 4: Model with Many-to-One and Many-to-Many
class Post(Base):
    __tablename__ = 'posts'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=True)
    published = Column(Boolean, default=False, index=True)
    view_count = Column(Integer, default=0)
    author_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship('User', back_populates='posts')
    categories = relationship('Category', secondary=post_categories, back_populates='posts')
    tags = relationship('Tag', secondary=post_tags, back_populates='posts')

    # Hybrid property
    @hybrid_property
    def is_popular(self):
        return self.view_count > 1000

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title})>"

class Category(Base):
    __tablename__ = 'categories'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    posts = relationship('Post', secondary=post_categories, back_populates='categories')

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)

    posts = relationship('Post', secondary=post_tags, back_populates='tags')

# Snippet 5: Complex model with enums
class OrderStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class Order(Base):
    __tablename__ = 'orders'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String, unique=True, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    order_id = Column(String, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(String, ForeignKey('products.id'), nullable=False)

    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')

class Product(Base):
    __tablename__ = 'products'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = relationship('OrderItem', back_populates='product')

# ============================================================================
# Query Examples
# ============================================================================

# Snippet 6: Create records with relationships
def create_user_with_profile(email: str, name: str, bio: str = None):
    session = SessionLocal()
    try:
        user = User(email=email, name=name)
        user.profile = Profile(bio=bio)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user
    finally:
        session.close()

# Snippet 7: Query with eager loading
def get_user_with_relations(user_id: str):
    session = SessionLocal()
    try:
        user = session.query(User).options(
            joinedload(User.profile),
            selectinload(User.posts).selectinload(Post.categories),
            selectinload(User.orders)
        ).filter(User.id == user_id).first()

        return user
    finally:
        session.close()

# Snippet 8: Complex filtering
def find_active_users_with_posts():
    session = SessionLocal()
    try:
        users = session.query(User).filter(
            and_(
                User.is_active == True,
                User.role == 'user',
                User.posts.any(Post.published == True)
            )
        ).options(
            selectinload(User.posts)
        ).order_by(User.created_at.desc()).limit(50).all()

        return users
    finally:
        session.close()

# Snippet 9: Aggregation queries
def get_user_statistics():
    session = SessionLocal()
    try:
        stats = session.query(
            func.count(User.id).label('total_users'),
            func.count(User.id).filter(User.is_active == True).label('active_users'),
            func.count(User.id).filter(User.role == 'admin').label('admin_count')
        ).first()

        return {
            'total_users': stats.total_users,
            'active_users': stats.active_users,
            'admin_count': stats.admin_count
        }
    finally:
        session.close()

# Snippet 10: Group by query
def get_orders_by_status():
    session = SessionLocal()
    try:
        results = session.query(
            Order.status,
            func.count(Order.id).label('count'),
            func.sum(Order.total_amount).label('total_revenue'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).group_by(Order.status).all()

        return [
            {
                'status': row.status.value,
                'count': row.count,
                'total_revenue': float(row.total_revenue or 0),
                'avg_order_value': float(row.avg_order_value or 0)
            }
            for row in results
        ]
    finally:
        session.close()

# Snippet 11: Transaction example
def create_order_with_items(user_id: str, items: List[dict]):
    session = SessionLocal()
    try:
        order = Order(
            user_id=user_id,
            order_number=f'ORD-{uuid.uuid4().hex[:8].upper()}',
            status=OrderStatus.PENDING
        )

        session.add(order)
        session.flush()  # Get order ID

        total_amount = 0
        for item_data in items:
            product = session.query(Product).filter(
                Product.id == item_data['product_id']
            ).with_for_update().first()

            if not product or product.stock < item_data['quantity']:
                raise ValueError(f"Insufficient stock for product {item_data['product_id']}")

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data['quantity'],
                price=product.price
            )

            session.add(order_item)

            product.stock -= item_data['quantity']
            total_amount += float(product.price) * item_data['quantity']

        order.total_amount = total_amount
        session.commit()
        session.refresh(order)

        return order
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Snippet 12: Subquery
def get_users_with_recent_orders():
    session = SessionLocal()
    try:
        recent_date = datetime.utcnow()  # Set appropriate date
        recent_orders_subq = session.query(Order.user_id).filter(
            Order.created_at >= recent_date
        ).distinct().subquery()

        users = session.query(User).filter(
            User.id.in_(select(recent_orders_subq))
        ).all()

        return users
    finally:
        session.close()

# Snippet 13: Pagination
def get_paginated_posts(page: int = 1, per_page: int = 20):
    session = SessionLocal()
    try:
        total = session.query(func.count(Post.id)).filter(Post.published == True).scalar()

        posts = session.query(Post).filter(
            Post.published == True
        ).options(
            joinedload(Post.author),
            selectinload(Post.categories),
            selectinload(Post.tags)
        ).order_by(Post.created_at.desc()).limit(per_page).offset((page - 1) * per_page).all()

        return {
            'posts': posts,
            'total': total,
            'page': page,
            'total_pages': (total + per_page - 1) // per_page
        }
    finally:
        session.close()

# Snippet 14: Raw SQL query
def get_top_customers(limit: int = 10):
    session = SessionLocal()
    try:
        result = session.execute("""
            SELECT
                u.id,
                u.name,
                COUNT(o.id) as order_count,
                COALESCE(SUM(o.total_amount), 0) as lifetime_value
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name
            HAVING COUNT(o.id) > 0
            ORDER BY lifetime_value DESC
            LIMIT :limit
        """, {'limit': limit})

        return result.fetchall()
    finally:
        session.close()

# Snippet 15: Bulk operations
def bulk_update_product_prices(updates: List[dict]):
    session = SessionLocal()
    try:
        session.bulk_update_mappings(Product, updates)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Create tables
Base.metadata.create_all(engine)
