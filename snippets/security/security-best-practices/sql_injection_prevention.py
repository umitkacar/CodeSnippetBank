"""SQL Injection Prevention"""
import sqlite3
from typing import Any, List

class SafeDatabase:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def execute_safe(self, query: str, params: tuple = ()) -> List:
        """Always use parameterized queries"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def insert_user(self, username: str, email: str):
        """Safe INSERT with parameters"""
        query = "INSERT INTO users (username, email) VALUES (?, ?)"
        self.execute_safe(query, (username, email))
        self.conn.commit()
    
    def get_user(self, user_id: int):
        """Safe SELECT with parameters"""
        query = "SELECT * FROM users WHERE id = ?"
        return self.execute_safe(query, (user_id,))

if __name__ == "__main__":
    db = SafeDatabase()
    db.cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)")
    db.insert_user("john", "john@example.com")
    print("✓ SQL injection prevention implemented")
