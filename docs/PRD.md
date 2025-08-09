# Product Requirements Document

## Overview
The **free-ride-investor Web Scraper & Automation Suite** collects, stores and analyzes social media discussions and job posts relevant to trading and freelance opportunities. It uses Python, Selenium and a lightweight SQLite database to aggregate potential leads and market sentiment.

## Goals
- Continuously gather posts from Twitter, Reddit, LinkedIn and Upwork.
- Generate draft replies or proposals for each lead so users can quickly respond.
- Store posts and comments in a structured database for future analysis.
- Deliver alerts via Discord when new leads or notable discussions appear.

## Core Features
1. **Automated Scraping** – Scheduled scripts extract posts from supported platforms using Selenium and BeautifulSoup.
2. **Lead Storage** – An SQLite database tracks posts, comments and generated proposals.
3. **Draft Reply Generation** – Template-driven messages help users reach out to promising leads faster.
4. **Dashboard** – A small Flask app visualizes stored leads in a web interface.
5. **Notifications** – Discord integration posts new lead alerts in real time.

## Success Metrics
- Number of unique leads captured per week.
- Response rate to drafted proposals sent from the tool.
- Uptime of scheduled scraping jobs.

## Future Work
See the [Roadmap](../README.md#-roadmap) for planned enhancements and expansion.
