"""Advanced CRUD with Relationships"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

app = FastAPI()

# Models
class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: UUID
    created_at: datetime
    books_count: int = 0

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    published_year: int = Field(..., ge=1000, le=2100)
    isbn: str = Field(..., min_length=10, max_length=13)

class BookCreate(BookBase):
    author_id: UUID

class Book(BookBase):
    id: UUID
    author_id: UUID
    created_at: datetime

class BookWithAuthor(Book):
    author: Author

# In-memory databases
authors_db: dict[UUID, Author] = {}
books_db: dict[UUID, Book] = {}

# Author CRUD
@app.post("/authors/", response_model=Author, status_code=status.HTTP_201_CREATED)
async def create_author(author: AuthorCreate):
    """Create a new author"""
    author_id = uuid4()
    new_author = Author(
        id=author_id,
        **author.model_dump(),
        created_at=datetime.now(timezone.utc),
        books_count=0
    )
    authors_db[author_id] = new_author
    return new_author

@app.get("/authors/", response_model=List[Author])
async def get_authors():
    """Get all authors"""
    return list(authors_db.values())

@app.get("/authors/{author_id}", response_model=Author)
async def get_author(author_id: UUID):
    """Get author by ID"""
    if author_id not in authors_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id {author_id} not found"
        )
    return authors_db[author_id]

# Book CRUD
@app.post("/books/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    """Create a new book"""
    # Check if author exists
    if book.author_id not in authors_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id {book.author_id} not found"
        )

    # Check ISBN uniqueness
    if any(b.isbn == book.isbn for b in books_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book with ISBN {book.isbn} already exists"
        )

    book_id = uuid4()
    new_book = Book(
        id=book_id,
        **book.model_dump(),
        created_at=datetime.now(timezone.utc)
    )
    books_db[book_id] = new_book

    # Update author's book count
    authors_db[book.author_id].books_count += 1

    return new_book

@app.get("/books/", response_model=List[BookWithAuthor])
async def get_books(author_id: Optional[UUID] = None):
    """Get all books, optionally filtered by author"""
    books = list(books_db.values())

    if author_id:
        books = [b for b in books if b.author_id == author_id]

    # Enrich with author data
    books_with_authors = []
    for book in books:
        author = authors_db.get(book.author_id)
        if author:
            books_with_authors.append(
                BookWithAuthor(**book.model_dump(), author=author)
            )

    return books_with_authors

@app.get("/books/{book_id}", response_model=BookWithAuthor)
async def get_book(book_id: UUID):
    """Get book by ID with author information"""
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    book = books_db[book_id]
    author = authors_db.get(book.author_id)

    if not author:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Author not found for this book"
        )

    return BookWithAuthor(**book.model_dump(), author=author)

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    """Delete a book"""
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    book = books_db[book_id]
    del books_db[book_id]

    # Update author's book count
    if book.author_id in authors_db:
        authors_db[book.author_id].books_count -= 1

@app.get("/authors/{author_id}/books", response_model=List[Book])
async def get_author_books(author_id: UUID):
    """Get all books by author"""
    if author_id not in authors_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id {author_id} not found"
        )

    books = [book for book in books_db.values() if book.author_id == author_id]
    return books
