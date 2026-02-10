"""Parser for Soccer.ru news."""
import logging
from typing import List
from .base_parser import BaseParser, NewsArticle

logger = logging.getLogger(__name__)


class SoccerRuParser(BaseParser):
    """Parser for Soccer.ru football news."""

    def __init__(self, clubs: List[str]):
        super().__init__(
            source_name="Soccer.ru", base_url="https://soccer.ru", clubs=clubs
        )

    async def parse(self) -> List[NewsArticle]:
        """Parse latest football news from Soccer.ru."""
        articles = []
        url = f"{self.base_url}/news/"

        try:
            html = await self.fetch_html(url)
            if not html:
                return articles

            soup = self.parse_html(html)

            # Find news items
            news_items = soup.select(".news, .article, .item, article, [class*='news']")

            for item in news_items[:20]:
                try:
                    # Ищем заголовок
                    title_elem = item.select_one(".title, h3, h2, a.title")
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
                    desc_elem = item.select_one(".text, .description, .anons, p")
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
                    logger.error(f"Error parsing Soccer.ru news item: {e}")
                    continue

            logger.info(f"Parsed {len(articles)} articles from Soccer.ru")

        except Exception as e:
            logger.error(f"Error parsing Soccer.ru: {e}")

        return articles
