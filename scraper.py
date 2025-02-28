import time
import sqlite3
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from database import Database
from config import config

# Initialize Database
db = Database()

# Selenium WebDriver Setup
def get_driver():
    """Setup and return a Selenium Chrome WebDriver with profile persistence."""
    options = Options()
    options.add_argument("--headless") if config.HEADLESS_MODE else None
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# 🔹 LinkedIn Scraper
def scrape_linkedin():
    """Scrapes LinkedIn for relevant posts based on search queries."""
    driver = get_driver()
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(5)

    # Ensure logged in
    if "login" in driver.current_url:
        print("❌ Not logged into LinkedIn. Please log in first.")
        driver.quit()
        return

    for query in config.SEARCH_QUERIES:
        search_url = f"https://www.linkedin.com/search/results/content/?keywords={query.replace(' ', '%20')}"
        driver.get(search_url)
        time.sleep(5)

        posts = driver.find_elements(By.XPATH, "//div[contains(@class, 'update')]")
        for post in posts:
            try:
                content = post.text.strip()
                link = post.find_element(By.TAG_NAME, "a").get_attribute("href")
                post_id = link.split("/")[-1]

                if not db.check_post_exists(post_id):
                    db.insert_post("LinkedIn", post_id, "Unknown", content, link)
                    print(f"✅ Saved LinkedIn Post: {content[:50]}...")
            except Exception:
                continue

    driver.quit()

# 🔹 Reddit Scraper
def scrape_reddit():
    """Scrapes Reddit for posts related to trading queries."""
    driver = get_driver()
    driver.get("https://www.reddit.com/")
    time.sleep(5)

    for query in config.SEARCH_QUERIES:
        search_url = f"https://www.reddit.com/search/?q={query.replace(' ', '%20')}&type=link"
        driver.get(search_url)
        time.sleep(5)

        posts = driver.find_elements(By.XPATH, "//a[contains(@data-click-id, 'body')]")
        for post in posts:
            try:
                content = post.text.strip()
                link = post.get_attribute("href")
                post_id = link.split("/")[-2]

                if not db.check_post_exists(post_id):
                    db.insert_post("Reddit", post_id, "Unknown", content, link)
                    print(f"✅ Saved Reddit Post: {content[:50]}...")
            except Exception:
                continue

    driver.quit()

# 🔹 Twitter Scraper (Web Scraping, Not API)
def scrape_twitter():
    """Scrapes Twitter for relevant posts using search queries."""
    driver = get_driver()
    driver.get("https://twitter.com/explore")
    time.sleep(5)

    for query in config.SEARCH_QUERIES:
        search_box = driver.find_element(By.XPATH, "//input[@aria-label='Search query']")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        posts = driver.find_elements(By.XPATH, "//article")
        for post in posts:
            try:
                content = post.text.strip()
                link = post.find_element(By.TAG_NAME, "a").get_attribute("href")
                post_id = link.split("/")[-1]

                if not db.check_post_exists(post_id):
                    db.insert_post("Twitter", post_id, "Unknown", content, link)
                    print(f"✅ Saved Twitter Post: {content[:50]}...")
            except Exception:
                continue

    driver.quit()

# 🔹 SeekingAlpha Scraper
def scrape_seekingalpha():
    """Scrapes SeekingAlpha for relevant articles."""
    driver = get_driver()
    driver.get("https://seekingalpha.com/")
    time.sleep(5)

    for query in config.SEARCH_QUERIES:
        search_url = f"https://seekingalpha.com/symbol/{query.replace(' ', '%20')}"
        driver.get(search_url)
        time.sleep(5)

        articles = driver.find_elements(By.XPATH, "//article")
        for article in articles:
            try:
                content = article.text.strip()
                link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                post_id = link.split("/")[-1]

                if not db.check_post_exists(post_id):
                    db.insert_post("SeekingAlpha", post_id, "Unknown", content, link)
                    print(f"✅ Saved SeekingAlpha Article: {content[:50]}...")
            except Exception:
                continue

    driver.quit()

# 🔹 Master Function to Run All Scrapers
def run_scrapers():
    """Runs all the scrapers sequentially."""
    print("\n🚀 Running Social Media Scraper...")
    
    scrape_linkedin()
    scrape_reddit()
    scrape_twitter()
    scrape_seekingalpha()

    print("✅ Scraping complete. Waiting for next cycle...")
    time.sleep(config.SCRAPE_INTERVAL * 60)

# Run the scraper on an hourly loop
if __name__ == "__main__":
    while True:
        run_scrapers()