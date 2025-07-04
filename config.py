import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the Social Media Lead Generation tool."""

    # Social Media Credentials (For automation & scraping)
    SOCIAL_MEDIA_CREDENTIALS = {
        "linkedin": {
            "email": os.getenv("LINKEDIN_EMAIL", ""),
            "password": os.getenv("LINKEDIN_PASSWORD", ""),
        },
        "reddit": {
            "email": os.getenv("REDDIT_USERNAME", ""),
            "password": os.getenv("REDDIT_PASSWORD", ""),
        },
        "facebook": {
            "email": os.getenv("FACEBOOK_EMAIL", ""),
            "password": os.getenv("FACEBOOK_PASSWORD", ""),
        },
        "tiktok": {
            "email": os.getenv("TIKTOK_EMAIL", ""),
            "password": os.getenv("TIKTOK_PASSWORD", ""),
        },
        "quora": {
            "email": os.getenv("QUORA_EMAIL", ""),
            "password": os.getenv("QUORA_PASSWORD", ""),
        },
        "stocktwits": {
            "email": os.getenv("STOCKTWITS_EMAIL", ""),
            "password": os.getenv("STOCKTWITS_PASSWORD", ""),
        },
        "tradingview": {
            "email": os.getenv("TRADINGVIEW_EMAIL", ""),
            "password": os.getenv("TRADINGVIEW_PASSWORD", ""),
        },
        "discord": {
            "email": os.getenv("DISCORD_EMAIL", ""),
            "password": os.getenv("DISCORD_PASSWORD", ""),
        },
        "seekingalpha": {
            "email": os.getenv("SEEKINGALPHA_EMAIL", ""),
            "password": os.getenv("SEEKINGALPHA_PASSWORD", ""),
        },
    }

    # Scraper & Lead Gen Settings
    SEARCH_QUERIES = [
        "best trading strategy",
        "how to automate trading",
        "day trading mistakes",
        "best stock trading bots",
        "does trading with AI work?",
        "seekingalpha trading bot reviews",
    ]
    MAX_SCRAPE_DAYS = int(os.getenv("MAX_SCRAPE_DAYS", 90))  # Extended tracking period
    SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 60))  # Check every 60 minutes
    MAX_RESULTS_PER_QUERY = int(os.getenv("MAX_RESULTS_PER_QUERY", 50))

    # Chrome WebDriver Settings
    CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH", "chrome_profile")
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"

    # General Settings
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    STARTING_CASH = float(os.getenv("STARTING_CASH", 10000))  # Reserved for potential monetization tracking

    @staticmethod
    def get_env(var_name, default_value=None):
        """Helper function to get environment variables safely."""
        return os.getenv(var_name, default_value)

# Create a single config instance
config = Config()