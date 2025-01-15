from html import unescape
import re
import os
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from typing import Type
import feedparser
from pydantic import BaseModel, Field
import requests
import tqdm    
from dotenv import load_dotenv

load_dotenv()

HOW_MANY_NEWS_TO_FETCH = int(os.getenv("HOW_MANY_NEWS_TO_FETCH"))
HOW_MANY_PARAGRAPHS_TO_FETCH = int(os.getenv("HOW_MANY_PARAGRAPHS_TO_FETCH"))

class NewsParserToolInput(BaseModel):
    """Input schema for NewsParserTool."""
    rss_url: str = Field(..., description="URL of the RSS feed to parse.")

class NewsParserTool(BaseTool):
    name: str = "News Parsing Tool"
    description: str = (
        "Fetches and cleans news articles from an RSS feed, removing HTML tags and enriching descriptions."
    )
    args_schema: Type[BaseModel] = NewsParserToolInput


    def _run(self, rss_url: str) -> list:
        """
        Fetch and clean news articles from the RSS feed.
        """
        feed = feedparser.parse(rss_url)
        articles = []

        for entry in tqdm.tqdm(feed.entries[:HOW_MANY_NEWS_TO_FETCH], desc="Fetching News"):
            title = self.clean_html(entry.title)
            description = self.clean_html(entry.description)
            link = entry.link
            pub_date = entry.published

            combined_text = self.enrich_description_with_details(link, description) if link else description

            articles.append({
                'title': title,
                'description': combined_text,
                'link': link,
                'publication_date': pub_date,
            })

        return articles

    def clean_html(self, raw_html: str) -> str:
        """Removes HTML tags, whitespace, and decodes entities."""
        print("🧹 Cleaning HTML...")
        clean_text = re.sub(r'<[^>]+>', '', raw_html)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return unescape(clean_text)

    def enrich_description_with_details(self, url: str, description: str) -> str:
        """Fetches article details from the main webpage and appends to description."""
        print(f"🔎 Enriching description with details from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            additional_details = []
            for paragraph in soup.find_all('p', limit=HOW_MANY_PARAGRAPHS_TO_FETCH):
                text = paragraph.get_text(strip=True)
                if text:
                    additional_details.append(text)

            print(f"📡 Additional details: {additional_details}")
            return f"{description}\n\n" + "\n".join(additional_details)
        except requests.RequestException as e:
            print(f"⚠️ Error fetching article details: {e}")
            return description