"""Parser for Championat.com news."""
import logging
from typing import List
from .base_parser import BaseParser, NewsArticle

logger = logging.getLogger(__name__)


class ChampionatParser(BaseParser):
    """Parser for Championat.com football news."""

    def __init__(self, clubs: List[str]):
        super().__init__(
            source_name="Championat.com",
            base_url="https://www.championat.com",
            clubs=clubs,
        )

    async def parse(self) -> List[NewsArticle]:
        """Parse latest football news from Championat.com."""
        articles = []
        url = f"{self.base_url}/football/"

        try:
            html = await self.fetch_html(url)
            if not html:
                return articles

            soup = self.parse_html(html)

            # Find news items
            news_items = soup.select(".article, .news-item, ._item, [class*='article']")

            for item in news_items[:20]:
                try:
                    # Ищем заголовок
                    title_elem = item.select_one(
                        "._title, .article-title, .title, h3, h2, a"
                    )
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Ищем ссылку
                    link_elem = item.select_one("a[href]")
                    if not link_elem:
                        link_elem = title_elem if title_elem.name == "a" else None

                    if not link_elem:
                        continue

                    link = link_elem.get("href", "")
                    if link.startswith("/"):
                        link = f"{self.base_url}{link}"

                    # Ищем описание
                    desc_elem = item.select_one("._text, .article-text, .description, p")
                    description = desc_elem.get_text(strip=True) if desc_elem else None

                    # Проверяем упоминания клубов
                    full_text = f"{title} {description or ''}"
                    clubs_mentioned = self.find_mentioned_clubs(full_text)

                    if clubs_mentioned:
                        article = NewsArticle(
                            title=title,
                            url=link,
                            source=self.source_name,
                            description=description,
                            clubs_mentioned=clubs_mentioned,
                        )
                        articles.append(article)

                except Exception as e:
                    logger.error(f"Error parsing Championat news item: {e}")
                    continue

            logger.info(f"Parsed {len(articles)} articles from Championat.com")

        except Exception as e:
            logger.error(f"Error parsing Championat.com: {e}")

        return articles
