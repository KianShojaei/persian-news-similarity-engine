"""Eitaa public channel scraper."""

from typing import List
from bs4 import BeautifulSoup

import config
from src.scrapers.base import BaseScraper, ScraperError


class EitaaScraper(BaseScraper):
    """Asynchronous scraper for public Eitaa (eitaa.com) channel web preview pages."""

    async def fetch_posts(self, channel: str, limit: int = 10) -> List[str]:
        clean_channel = self.sanitize_channel(channel)
        if not clean_channel:
            raise ScraperError("Eitaa channel ID cannot be empty.")

        url = f"{config.EITAA_BASE_URL}/{clean_channel}"
        html_content = await self.get_html(url)
        return self.parse_posts(html_content, limit=limit)

    def parse_posts(self, html_content: str, limit: int = 10) -> List[str]:
        soup = BeautifulSoup(html_content, "html.parser")

        SELECTORS = [
            "div.etme_widget_message_text",
            "div.js-message_text",
            "div.eitaa_message_text",
        ]

        message_nodes = []
        for selector in SELECTORS:
            nodes = soup.select(selector)
            if nodes:
                message_nodes = nodes
                break

        posts: List[str] = []
        for node in reversed(message_nodes):
            for br in node.find_all("br"):
                br.replace_with(" ")

            text = node.get_text(separator=" ", strip=True)
            if len(text) >= config.MIN_POST_LENGTH and text not in posts:
                posts.append(text)
                if len(posts) >= limit:
                    break

        return posts
