"""Base parser class for news sources."""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NewsArticle:
    """News article data structure."""

    def __init__(
        self,
        title: str,
        url: str,
        source: str,
        description: Optional[str] = None,
        clubs_mentioned: Optional[List[str]] = None,
    ):
        self.title = title
        self.url = url
        self.source = source
        self.description = description
        self.clubs_mentioned = clubs_mentioned or []

    def __repr__(self):
        return f"<NewsArticle(title={self.title[:50]}, source={self.source})>"


class BaseParser(ABC):
    """Base class for news parsers."""

    def __init__(self, source_name: str, base_url: str, clubs: List[str]):
        self.source_name = source_name
        self.base_url = base_url
        self.clubs = clubs

    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(
                            f"Failed to fetch {url}: status {response.status}"
                        )
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def find_mentioned_clubs(self, text: str) -> List[str]:
        """Find clubs mentioned in text."""
        mentioned = []
        text_lower = text.lower()

        for club in self.clubs:
            if club.lower() in text_lower:
                mentioned.append(club)

        return mentioned

    @abstractmethod
    async def parse(self) -> List[NewsArticle]:
        """Parse news from the source."""
        pass

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML with BeautifulSoup."""
        return BeautifulSoup(html, "lxml")
