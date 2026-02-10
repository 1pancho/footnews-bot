"""News fetching service."""
import logging
import asyncio
from typing import List
from database import Database
from parsers import SportsRuParser, ChampionatParser, SoccerRuParser
from parsers.base_parser import NewsArticle
from config import FOOTBALL_CLUBS

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching and managing news."""

    def __init__(self, db: Database):
        self.db = db
        self.parsers = [
            SportsRuParser(clubs=FOOTBALL_CLUBS),
            ChampionatParser(clubs=FOOTBALL_CLUBS),
            SoccerRuParser(clubs=FOOTBALL_CLUBS),
        ]

    async def fetch_all_news(self) -> List[NewsArticle]:
        """Fetch news from all sources."""
        all_news = []

        logger.info("Starting news fetch from all sources...")

        # Run all parsers in parallel
        tasks = [parser.parse() for parser in self.parsers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Parser error: {result}")
            elif isinstance(result, list):
                all_news.extend(result)

        logger.info(f"Fetched total {len(all_news)} news articles")
        return all_news

    async def update_news(self):
        """Fetch and save new news to database."""
        try:
            news_articles = await self.fetch_all_news()

            new_count = 0
            for article in news_articles:
                # Check if news already exists
                exists = await self.db.news_exists(article.url)

                if not exists:
                    # Add new news to database
                    result = await self.db.add_news_item(
                        title=article.title,
                        url=article.url,
                        source=article.source,
                        description=article.description,
                        clubs_mentioned=article.clubs_mentioned,
                    )

                    if result:
                        new_count += 1
                        logger.info(f"Added new news: {article.title[:50]}...")

            logger.info(f"News update completed. Added {new_count} new articles")
            return new_count

        except Exception as e:
            logger.error(f"Error updating news: {e}")
            return 0
