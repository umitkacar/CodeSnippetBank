"""GraphQL Integration with FastAPI"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import strawberry
from strawberry.fastapi import GraphQLRouter

app = FastAPI()

# Models
@strawberry.type
class User:
    id: int
    username: str
    email: str
    is_active: bool

@strawberry.type
class Post:
    id: int
    title: str
    content: str
    author_id: int

# Sample data
users_data = [
    {"id": 1, "username": "john_doe", "email": "john@example.com", "is_active": True},
    {"id": 2, "username": "jane_doe", "email": "jane@example.com", "is_active": True}
]

posts_data = [
    {"id": 1, "title": "First Post", "content": "Content 1", "author_id": 1},
    {"id": 2, "title": "Second Post", "content": "Content 2", "author_id": 1},
    {"id": 3, "title": "Third Post", "content": "Content 3", "author_id": 2}
]

# Queries
@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> List[User]:
        """Get all users"""
        return [User(**user) for user in users_data]

    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """Get user by ID"""
        user_data = next((u for u in users_data if u["id"] == id), None)
        return User(**user_data) if user_data else None

    @strawberry.field
    def posts(self, author_id: Optional[int] = None) -> List[Post]:
        """Get posts, optionally filtered by author"""
        filtered_posts = posts_data
        if author_id:
            filtered_posts = [p for p in posts_data if p["author_id"] == author_id]
        return [Post(**post) for post in filtered_posts]

# Mutations
@strawberry.input
class UserInput:
    username: str
    email: str
    is_active: bool = True

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: UserInput) -> User:
        """Create a new user"""
        new_id = max(u["id"] for u in users_data) + 1
        new_user = {
            "id": new_id,
            "username": input.username,
            "email": input.email,
            "is_active": input.is_active
        }
        users_data.append(new_user)
        return User(**new_user)

# Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# GraphQL router
graphql_app = GraphQLRouter(schema)

# Mount GraphQL
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "GraphQL endpoint available at /graphql"}
