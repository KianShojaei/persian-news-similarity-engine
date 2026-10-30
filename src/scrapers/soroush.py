"""Soroush Plus (splus.ir / vitrin.splus.ir) Signed JSON API & HTML Scraper."""

import hashlib
import json
import re
from typing import Any, Dict, List, Set
from bs4 import BeautifulSoup, Tag
import httpx

import config
from src.scrapers.base import BaseScraper, ScraperError


class SoroushScraper(BaseScraper):
    """Asynchronous scraper for public Soroush Plus channels using Soroush's Signed MD5 API + HTML fallback."""

    VITRIN_API_BASE = "https://vitrin.splus.ir"
    APP_SECRET = "95d58639-24c0-4b72-80a5-e124f41d7af9v1"
    APP_FORMAT = "json"
    APP_ID = "7743461522282941752"

    PRIMARY_SELECTORS = [
        "div.message-text",
        "div.post-text",
        "div.post_content",
        "div.message_text",
        "div[class*='message-content']",
        "div[class*='message_content']",
        "div[class*='message-body']",
        "div[class*='post-body']",
        "div[class*='text-content']",
        "div[class*='Message_text']",
        "div[class*='messageText']",
        "p[class*='message']",
        "article",
    ]

    IGNORED_PATTERNS = [
        "مشاهده در نسخه وب",
        "مشاهده در نسخه اندروید",
        "دریافت سروش+",
        "پیام‌رسان سروش+",
        "پیامرسان سروش+",
        "دنبال کردن",
        "You need to enable JavaScript",
    ]

    @classmethod
    def _build_signed_api_url(cls, endpoint: str, payload_str: str) -> str:
        """Generate the MD5-signed Soroush Vitrin API URL."""
        raw_to_sign = f"{cls.APP_SECRET}{cls.APP_FORMAT}{cls.APP_ID}{endpoint}{payload_str}"
        signature = hashlib.md5(raw_to_sign.encode("utf-8")).hexdigest()
        return f"{cls.VITRIN_API_BASE}/srvcs-app/v1/{cls.APP_FORMAT}/{cls.APP_ID}/{signature}/{endpoint}"

    async def _post_signed_api(self, client: httpx.AsyncClient, endpoint: str, payload: Dict[str, Any]) -> Any:
        """Send a signed POST request to Soroush Plus Vitrin API."""
        payload_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        url = self._build_signed_api_url(endpoint, payload_str)
        headers = {
            **self.headers,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://splus.ir",
            "Referer": "https://splus.ir/",
        }
        resp = await client.post(url, content=payload_str.encode("utf-8"), headers=headers)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _extract_text_from_msg_obj(msg: Dict[str, Any]) -> str:
        """Extract clean text from a Soroush API message object."""
        for key in ("text", "caption", "body", "content", "message", "description", "title"):
            val = msg.get(key)
            if isinstance(val, str) and val.strip():
                return re.sub(r"\s+", " ", val).strip()
        return ""

    @staticmethod
    def _extract_messages_list(archive_data: Any) -> List[Dict[str, Any]]:
        if isinstance(archive_data, list):
            return [m for m in archive_data if isinstance(m, dict)]
        if isinstance(archive_data, dict):
            for k in ("messages", "data", "items", "result"):
                if isinstance(archive_data.get(k), list):
                    return [m for m in archive_data[k] if isinstance(m, dict)]
        return []

    async def fetch_posts(self, channel: str, limit: int = 10) -> List[str]:
        """Fetch latest posts from public Soroush Plus channel (Newest First, matching Eitaa)."""
        clean_channel = self.sanitize_channel(channel)
        if not clean_channel:
            raise ScraperError("شناسه کانال سروش‌پلاس نمی‌تواند خالی باشد.")

        # 1. Primary Method: Soroush Plus Signed JSON API
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                meta_data = await self._post_signed_api(client, "meta/get", {"lookup": clean_channel})

                channel_internal_id = None
                if isinstance(meta_data, list) and len(meta_data) > 0 and isinstance(meta_data[0], dict):
                    channel_internal_id = meta_data[0].get("id")
                elif isinstance(meta_data, dict):
                    if "id" in meta_data:
                        channel_internal_id = meta_data["id"]
                    elif isinstance(meta_data.get("data"), list) and meta_data["data"]:
                        channel_internal_id = meta_data["data"][0].get("id")

                if channel_internal_id:
                    posts: List[str] = []
                    seen: Set[str] = set()
                    last_message_id = None

                    # Fetch up to 2 pages if needed so we always reach `limit` (e.g., 25 posts)
                    for _ in range(2):
                        req_payload: Dict[str, Any] = {"channel_id": channel_internal_id}
                        if last_message_id is not None:
                            req_payload["limit"] = 25
                            req_payload["message_id"] = last_message_id

                        archive_data = await self._post_signed_api(client, "channel/archive", req_payload)
                        messages_list = self._extract_messages_list(archive_data)
                        if not messages_list:
                            break

                        # Ensure messages are sorted from NEWEST to OLDEST
                        # In Soroush API, messages have an 'id' or 'time'/'date' — larger is newer.
                        # If the first item is older than the last item, sort descending; otherwise keep order.
                        if len(messages_list) >= 2:
                            first_id = str(messages_list[0].get("id", ""))
                            last_id = str(messages_list[-1].get("id", ""))
                            if first_id.isdigit() and last_id.isdigit() and int(first_id) < int(last_id):
                                messages_list = list(reversed(messages_list))

                        for msg in messages_list:
                            txt = self._extract_text_from_msg_obj(msg)
                            if len(txt) >= config.MIN_POST_LENGTH and txt not in seen:
                                seen.add(txt)
                                posts.append(txt)
                                if len(posts) >= limit:
                                    return posts

                        last_message_id = messages_list[-1].get("id")
                        if not last_message_id:
                            break

                    if posts:
                        return posts
        except Exception:
            pass

        # 2. Fallback Method: HTML parsing (used by unit tests or static pages)
        url = f"{config.SOROUSH_BASE_URL}/{clean_channel}"
        html_content = await self.get_html(url)
        return self.parse_posts(html_content, limit=limit)

    def parse_posts(self, html_content: str, limit: int = 10) -> List[str]:
        """Parse Soroush Plus HTML content (used for static HTML & unit tests)."""
        soup = BeautifulSoup(html_content, "html.parser")

        for unwanted in soup.find_all(["script", "style", "nav", "header", "footer", "button", "noscript"]):
            unwanted.decompose()

        posts: List[str] = []
        seen_texts: Set[str] = set()

        candidate_nodes: List[Tag] = []
        for selector in self.PRIMARY_SELECTORS:
            nodes = soup.select(selector)
            if nodes:
                candidate_nodes.extend(nodes)

        if candidate_nodes:
            for node in reversed(candidate_nodes):
                for br in node.find_all("br"):
                    br.replace_with(" ")
                text = node.get_text(separator=" ", strip=True)
                if any(ign in text for ign in self.IGNORED_PATTERNS):
                    continue
                if len(text) >= config.MIN_POST_LENGTH and text not in seen_texts:
                    seen_texts.add(text)
                    posts.append(text)
                    if len(posts) >= limit:
                        return posts

        if not posts:
            for node in reversed(soup.find_all(["p", "div"])):
                if node.name == "div" and len(node.find_all("div")) > 2:
                    continue
                for br in node.find_all("br"):
                    br.replace_with(" ")
                text = node.get_text(separator=" ", strip=True)
                if any(ign in text for ign in self.IGNORED_PATTERNS):
                    continue
                if len(text) >= config.MIN_POST_LENGTH and text not in seen_texts:
                    seen_texts.add(text)
                    posts.append(text)
                    if len(posts) >= limit:
                        return posts

        return posts
