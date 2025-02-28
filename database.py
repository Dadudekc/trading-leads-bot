import sqlite3
from datetime import datetime

class Database:
    """Handles SQLite database operations for storing scraped data."""

    def __init__(self, db_name="scraper_data.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Creates necessary tables for storing posts and comments."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            post_id TEXT UNIQUE NOT NULL,
            author TEXT,
            content TEXT,
            url TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            post_id TEXT NOT NULL,
            comment_id TEXT UNIQUE NOT NULL,
            author TEXT,
            content TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE
        )""")

        self.conn.commit()

    def insert_post(self, platform, post_id, author, content, url):
        """Insert a new post if it doesn't already exist."""
        try:
            self.cursor.execute("""
            INSERT INTO posts (platform, post_id, author, content, url) 
            VALUES (?, ?, ?, ?, ?)""",
            (platform, post_id, author, content, url))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Post already exists

    def insert_comment(self, platform, post_id, comment_id, author, content):
        """Insert a new comment if it doesn't already exist."""
        try:
            self.cursor.execute("""
            INSERT INTO comments (platform, post_id, comment_id, author, content) 
            VALUES (?, ?, ?, ?, ?)""",
            (platform, post_id, comment_id, author, content))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Comment already exists

    def check_post_exists(self, post_id):
        """Check if a post is already in the database."""
        self.cursor.execute("SELECT 1 FROM posts WHERE post_id = ?", (post_id,))
        return self.cursor.fetchone() is not None

    def check_comment_exists(self, comment_id):
        """Check if a comment is already in the database."""
        self.cursor.execute("SELECT 1 FROM comments WHERE comment_id = ?", (comment_id,))
        return self.cursor.fetchone() is not None

    def close(self):
        """Close the database connection."""
        self.conn.close()

# Usage Example
if __name__ == "__main__":
    db = Database()
    db.insert_post("Reddit", "123abc", "TraderJoe", "This is a test post about trading!", "https://reddit.com/test")
    db.insert_comment("Reddit", "123abc", "456def", "InvestorMike", "Interesting strategy!")
    print(db.check_post_exists("123abc"))  # Should return True
    print(db.check_comment_exists("456def"))  # Should return True
    db.close()