import time
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Load environment variables and configuration
load_dotenv()
from config import config  # Ensure config.py is in your project directory

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Instead of auto applying, generate a draft reply for manual follow-up
GENERATE_REPLY_DRAFT = True

# ============================== DATABASE ==============================
DB_FILE = "leads.db"

def init_db():
    """Initialize the SQLite database for storing freelance leads."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            post_id TEXT UNIQUE,
            title TEXT,
            content TEXT,
            link TEXT,
            draft_generated INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    conn.close()

def save_lead(platform, post_id, title, content, link):
    """Save a new lead to the database if it doesn't already exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO leads (platform, post_id, title, content, link) VALUES (?, ?, ?, ?, ?)",
            (platform, post_id, title, content, link)
        )
        conn.commit()
        return True  # New lead added
    except sqlite3.IntegrityError:
        return False  # Lead already exists
    finally:
        conn.close()

def mark_draft_generated(post_id):
    """Mark a lead as having a draft reply generated."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET draft_generated=1 WHERE post_id=?", (post_id,))
    conn.commit()
    conn.close()

# ============================== DRAFT REPLY MODULE ==============================
def generate_proposal(lead_details):
    """
    Generate a dynamic proposal (draft reply) message based on lead details.
    Modify the template as needed.
    """
    proposal = (
        f"Hello,\n\n"
        f"I'm excited about your project titled '{lead_details['title']}'. "
        f"With my expertise in Python and automation, I believe I can deliver top-notch results tailored to your needs. "
        f"I would love to discuss the project further and see how we might work together.\n\n"
        f"Best regards,\n[Your Name]"
    )
    return proposal

def prepare_reply(lead_details):
    """
    Generate and print a draft reply (proposal) for manual review.
    The draft reply is not automatically sent.
    """
    proposal = generate_proposal(lead_details)
    print("\n[Draft Reply]")
    print(f"Platform: {lead_details['platform']} | Post ID: {lead_details['post_id']}")
    print("Draft Proposal:")
    print(proposal)
    print("-" * 50)
    mark_draft_generated(lead_details['post_id'])

# ============================== SELENIUM SETUP ==============================
def get_driver():
    """Setup and return a Selenium Chrome WebDriver using configuration settings."""
    options = Options()
    if config.HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    if config.CHROME_PROFILE_PATH:
        options.add_argument(f"user-data-dir={config.CHROME_PROFILE_PATH}")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# ============================== SCRAPERS ==============================
FREELANCE_KEYWORDS = [
    "looking for a developer", "hiring a python expert", "need automation help",
    "freelance programmer", "remote developer job", "AI developer wanted"
]

def scrape_twitter():
    """Scrapes Twitter for freelance job leads."""
    driver = get_driver()
    driver.get("https://twitter.com/explore")
    time.sleep(5)

    for keyword in FREELANCE_KEYWORDS:
        try:
            search_box = driver.find_element(By.XPATH, "//input[@aria-label='Search query']")
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)

            posts = driver.find_elements(By.XPATH, "//article")
            for post in posts:
                try:
                    content = post.text.strip()
                    link = post.find_element(By.TAG_NAME, "a").get_attribute("href")
                    post_id = link.split("/")[-1]

                    if save_lead("Twitter", post_id, keyword, content, link):
                        bot.loop.create_task(send_discord_alert("Twitter", keyword, content, link))
                        if GENERATE_REPLY_DRAFT:
                            prepare_reply({
                                "platform": "Twitter",
                                "post_id": post_id,
                                "title": keyword,
                                "content": content,
                                "link": link
                            })
                except Exception as inner_ex:
                    print(f"Error processing a Twitter post: {inner_ex}")
                    continue
        except Exception as ex:
            print(f"Error in Twitter scraping for keyword '{keyword}': {ex}")
            continue

    driver.quit()

def scrape_linkedin():
    """Scrapes LinkedIn for freelance job leads."""
    driver = get_driver()
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(5)

    for keyword in FREELANCE_KEYWORDS:
        try:
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={keyword.replace(' ', '%20')}"
            driver.get(search_url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            posts = soup.find_all("div", class_="update")

            for post in posts:
                try:
                    content = post.get_text(strip=True)
                    link = post.find("a")["href"]
                    post_id = link.split("/")[-1]

                    if save_lead("LinkedIn", post_id, keyword, content, link):
                        bot.loop.create_task(send_discord_alert("LinkedIn", keyword, content, link))
                        if GENERATE_REPLY_DRAFT:
                            prepare_reply({
                                "platform": "LinkedIn",
                                "post_id": post_id,
                                "title": keyword,
                                "content": content,
                                "link": link
                            })
                except Exception as inner_ex:
                    print(f"Error processing a LinkedIn post: {inner_ex}")
                    continue
        except Exception as ex:
            print(f"Error in LinkedIn scraping for keyword '{keyword}': {ex}")
            continue

    driver.quit()

def scrape_reddit():
    """Scrapes Reddit for freelance job leads."""
    driver = get_driver()
    driver.get("https://www.reddit.com/")
    time.sleep(5)

    for keyword in FREELANCE_KEYWORDS:
        try:
            search_url = f"https://www.reddit.com/search/?q={keyword.replace(' ', '%20')}&type=link"
            driver.get(search_url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            posts = soup.find_all("a", {"data-click-id": "body"})

            for post in posts:
                try:
                    content = post.get_text(strip=True)
                    link = post["href"]
                    post_id = link.split("/")[-2]

                    if save_lead("Reddit", post_id, keyword, content, link):
                        bot.loop.create_task(send_discord_alert("Reddit", keyword, content, link))
                        if GENERATE_REPLY_DRAFT:
                            prepare_reply({
                                "platform": "Reddit",
                                "post_id": post_id,
                                "title": keyword,
                                "content": content,
                                "link": link
                            })
                except Exception as inner_ex:
                    print(f"Error processing a Reddit post: {inner_ex}")
                    continue
        except Exception as ex:
            print(f"Error in Reddit scraping for keyword '{keyword}': {ex}")
            continue

    driver.quit()

def scrape_upwork():
    """Scrapes Upwork for freelance job listings."""
    driver = get_driver()
    driver.get("https://www.upwork.com/nx/jobs/search/?q=python")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    jobs = soup.find_all("section", class_="air-card")

    for job in jobs:
        try:
            title = job.find("h4").get_text(strip=True)
            content = job.find("div", class_="job-description").get_text(strip=True)
            link = job.find("a")["href"]
            post_id = link.split("/")[-1]

            if save_lead("Upwork", post_id, title, content, link):
                bot.loop.create_task(send_discord_alert("Upwork", title, content, link))
                if GENERATE_REPLY_DRAFT:
                    prepare_reply({
                        "platform": "Upwork",
                        "post_id": post_id,
                        "title": title,
                        "content": content,
                        "link": link
                    })
        except Exception as ex:
            print(f"Error processing an Upwork job: {ex}")
            continue

    driver.quit()

# ============================== DISCORD ALERT ==============================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def send_discord_alert(platform, title, content, link):
    """Sends a Discord alert when a new freelance job is found."""
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        channel = await bot.fetch_channel(DISCORD_CHANNEL_ID)

    embed = discord.Embed(title=f"🚀 New Freelance Lead ({platform})", color=discord.Color.blue())
    embed.add_field(name="Title", value=title, inline=False)
    embed.add_field(name="Description", value=content[:300] + "..." if len(content) > 300 else content, inline=False)
    embed.add_field(name="Link", value=f"[View Post]({link})", inline=False)
    embed.set_footer(text="Freelancer Lead Finder Bot")

    await channel.send(embed=embed)

# ============================== MAIN FUNCTION ==============================
def run_scrapers():
    """Runs all the scrapers sequentially."""
    print("\n🚀 Searching for freelance jobs...")
    
    scrape_twitter()
    scrape_linkedin()
    scrape_reddit()
    scrape_upwork()

    print("✅ Search complete. Waiting for next cycle...")
    # Use the interval from config (minutes to seconds)
    time.sleep(config.SCRAPE_INTERVAL * 60)

# ============================== EXECUTION ==============================
if __name__ == "__main__":
    init_db()
    bot.loop.create_task(run_scrapers())
    bot.run(DISCORD_TOKEN)
