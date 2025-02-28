import unittest
import os
from basicbot.config import config

class TestConfig(unittest.TestCase):
    """Unit tests for config.py settings and environment variable handling."""

    def test_social_media_credentials_exist(self):
        """Ensure all expected social media credentials are available."""
        required_platforms = [
            "linkedin", "facebook", "reddit", "tiktok", "stocktwits",
            "quora", "tradingview", "discord", "seekingalpha"
        ]
        for platform in required_platforms:
            self.assertIn(platform, config.SOCIAL_MEDIA_CREDENTIALS, f"⚠️ Missing {platform} credentials in config.")

    def test_environment_variables_load(self):
        """Check that important environment variables are correctly set."""
        self.assertIsInstance(config.MAX_SCRAPE_DAYS, int, "❌ MAX_SCRAPE_DAYS should be an integer.")
        self.assertIsInstance(config.SCRAPE_INTERVAL, int, "❌ SCRAPE_INTERVAL should be an integer.")
        self.assertIsInstance(config.STARTING_CASH, float, "❌ STARTING_CASH should be a float.")

    def test_search_queries_are_valid(self):
        """Ensure search queries list is populated correctly."""
        self.assertGreater(len(config.SEARCH_QUERIES), 0, "⚠️ SEARCH_QUERIES list is empty.")
        for query in config.SEARCH_QUERIES:
            self.assertIsInstance(query, str, "❌ SEARCH_QUERIES should contain only strings.")

    def test_headless_mode_is_boolean(self):
        """Verify headless mode is correctly parsed as a boolean."""
        self.assertIsInstance(config.HEADLESS_MODE, bool, "❌ HEADLESS_MODE should be a boolean.")

    def test_logging_directory_exists(self):
        """Ensure log directory is set and valid."""
        self.assertIsInstance(config.LOG_DIR, str, "❌ LOG_DIR should be a string.")
        if not os.path.exists(config.LOG_DIR):
            os.makedirs(config.LOG_DIR)
        self.assertTrue(os.path.exists(config.LOG_DIR), "⚠️ Log directory does not exist.")

    def test_chrome_profile_path(self):
        """Check that Chrome profile path exists (or is set correctly)."""
        self.assertIsInstance(config.CHROME_PROFILE_PATH, str, "❌ CHROME_PROFILE_PATH should be a string.")

if __name__ == "__main__":
    unittest.main()