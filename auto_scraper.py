import time
import os
import sqlite3
import random
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

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Set Auto-Apply flag
AUTO_APPLY_ENABLED = True  # Set to False to disable auto-applying

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
            applied INTEGER DEFAULT 0,
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

def mark_lead_as_applied(post_id):
    """Mark a lead as auto-applied in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET applied=1 WHERE post_id=?", (post_id,))
    conn.commit()
    conn.close()

# ============================== AUTO-APPLY MODULE ==============================
def generate_proposal(lead_details):
    """
    Generate a dynamic proposal message based on lead details.
    For a real-world scenario, you might use more sophisticated templating or NLP.
    """
    proposal = (
        f"Hello,\n\n"
        f"I'm excited about your project titled '{lead_details['title']}'. "
        f"With my expertise in Python and automation, I can deliver top-notch results tailored to your needs. "
        f"I'd love to discuss your project further and see how we can work together.\n\n"
        f"Best regards,\n[Your Name]"
    )
    return proposal

def auto_apply(lead_details):
    """
    Simulate an auto-application by generating a proposal and marking the lead as applied.
    In a full implementation, this would interact with the platform's application API or use Selenium to submit the proposal.
    """
    proposal = generate_proposal(lead_details)
    print(f"\n[Auto-Apply] Applying to {lead_details['platform']} post {lead_details['post_id']}:")
    print(proposal)
    mark_lead_as_applied(lead_details['post_id'])
    
# ============================== SELENIUM SETUP ==============================
def get_driver():
    """Setup and return a Selenium Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--start-maximized")
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
                    # Send Discord alert
                    bot.loop.create_task(send_discord_alert("Twitter", keyword, content, link))
                    # Auto-apply if enabled
                    if AUTO_APPLY_ENABLED:
                        auto_apply({
                            "platform": "Twitter",
                            "post_id": post_id,
                            "title": keyword,
                            "content": content,
                            "link": link
                        })
            except Exception:
                continue

    driver.quit()

def scrape_linkedin():
    """Scrapes LinkedIn for freelance job leads."""
    driver = get_driver()
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(5)

    for keyword in FREELANCE_KEYWORDS:
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
                    if AUTO_APPLY_ENABLED:
                        auto_apply({
                            "platform": "LinkedIn",
                            "post_id": post_id,
                            "title": keyword,
                            "content": content,
                            "link": link
                        })
            except Exception:
                continue

    driver.quit()

def scrape_reddit():
    """Scrapes Reddit for freelance job leads."""
    driver = get_driver()
    driver.get("https://www.reddit.com/")
    time.sleep(5)

    for keyword in FREELANCE_KEYWORDS:
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
                    if AUTO_APPLY_ENABLED:
                        auto_apply({
                            "platform": "Reddit",
                            "post_id": post_id,
                            "title": keyword,
                            "content": content,
                            "link": link
                        })
            except Exception:
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
                if AUTO_APPLY_ENABLED:
                    auto_apply({
                        "platform": "Upwork",
                        "post_id": post_id,
                        "title": title,
                        "content": content,
                        "link": link
                    })
        except Exception:
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
    time.sleep(1800)  # Runs every 30 minutes

# ============================== EXECUTION ==============================
if __name__ == "__main__":
    init_db()
    bot.loop.create_task(run_scrapers())
    bot.run(DISCORD_TOKEN)
