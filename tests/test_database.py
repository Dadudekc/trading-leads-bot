import unittest
import sqlite3
from database import Database

class TestDatabase(unittest.TestCase):
    """Unit tests for Database functionality."""

    @classmethod
    def setUpClass(cls):
        """Initialize test database instance."""
        cls.db = Database(db_name="test_scraper_data.db")  # Use a test database

    def setUp(self):
        """Clear tables before each test to ensure clean state."""
        self.db.cursor.execute("DELETE FROM posts")
        self.db.cursor.execute("DELETE FROM comments")
        self.db.conn.commit()

    def test_create_tables(self):
        """Ensure the tables exist in the database."""
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
        self.assertIsNotNone(self.db.cursor.fetchone(), "Posts table was not created.")
        
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
        self.assertIsNotNone(self.db.cursor.fetchone(), "Comments table was not created.")

    def test_insert_post(self):
        """Test inserting a post into the database."""
        self.db.insert_post("Reddit", "123abc", "TraderJoe", "This is a test post!", "https://reddit.com/test")
        self.db.cursor.execute("SELECT * FROM posts WHERE post_id = '123abc'")
        post = self.db.cursor.fetchone()
        self.assertIsNotNone(post, "Post was not inserted correctly.")

    def test_insert_duplicate_post(self):
        """Ensure duplicate posts are not inserted."""
        self.db.insert_post("Reddit", "123abc", "TraderJoe", "This is a test post!", "https://reddit.com/test")
        self.db.insert_post("Reddit", "123abc", "TraderJoe", "This is a duplicate!", "https://reddit.com/duplicate")

        self.db.cursor.execute("SELECT COUNT(*) FROM posts WHERE post_id = '123abc'")
        count = self.db.cursor.fetchone()[0]
        self.assertEqual(count, 1, "Duplicate post was inserted.")

    def test_insert_comment(self):
        """Test inserting a comment into the database."""
        self.db.insert_post("Reddit", "123abc", "TraderJoe", "This is a test post!", "https://reddit.com/test")
        self.db.insert_comment("Reddit", "123abc", "456def", "InvestorMike", "Interesting insight!")

        self.db.cursor.execute("SELECT * FROM comments WHERE comment_id = '456def'")
        comment = self.db.cursor.fetchone()
        self.assertIsNotNone(comment, "Comment was not inserted correctly.")

    def test_insert_duplicate_comment(self):
        """Ensure duplicate comments are not inserted."""
        self.db.insert_post("Reddit", "123abc", "TraderJoe", "This is a test post!", "https://reddit.com/test")
        self.db.insert_comment("Reddit", "123abc", "456def", "InvestorMike", "Interesting insight!")
        self.db.insert_comment("Reddit", "123abc", "456def", "InvestorMike", "Duplicate insight!")

        self.db.cursor.execute("SELECT COUNT(*) FROM comments WHERE comment_id = '456def'")
        count = self.db.cursor.fetchone()[0]
        self.assertEqual(count, 1, "Duplicate comment was inserted.")

    def test_check_post_exists(self):
        """Test if the function correctly identifies existing posts."""
        self.db.insert_post("Reddit", "123abc", "TraderJoe", "This is a test post!", "https://reddit.com/test")
        self.assertTrue(self.db.check_post_exists("123abc"), "check_post_exists returned False for an existing post.")
        self.assertFalse(self.db.check_post_exists("999xyz"), "check_post_exists returned True for a non-existent post.")

    def test_check_comment_exists(self):
        """Test if the function correctly identifies existing comments."""
        self.db.insert_post("Reddit", "123abc", "TraderJoe", "This is a test post!", "https://reddit.com/test")
        self.db.insert_comment("Reddit", "123abc", "456def", "InvestorMike", "Interesting insight!")

        self.assertTrue(self.db.check_comment_exists("456def"), "check_comment_exists returned False for an existing comment.")
        self.assertFalse(self.db.check_comment_exists("999xyz"), "check_comment_exists returned True for a non-existent comment.")

    @classmethod
    def tearDownClass(cls):
        """Clean up test database after tests are complete."""
        cls.db.conn.close()
        import os
        os.remove("test_scraper_data.db")  # Remove test database file after tests complete

if __name__ == "__main__":
    unittest.main()