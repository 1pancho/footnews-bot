"""Parser for Sports.ru news."""
import logging
from typing import List
from .base_parser import BaseParser, NewsArticle

logger = logging.getLogger(__name__)


class SportsRuParser(BaseParser):
    """Parser for Sports.ru football news."""

    def __init__(self, clubs: List[str]):
        super().__init__(
            source_name="Sports.ru",
            base_url="https://www.sports.ru",
            clubs=clubs,
        )

    async def parse(self) -> List[NewsArticle]:
        """Parse latest football news from Sports.ru."""
        articles = []
        url = f"{self.base_url}/football/news/"

        try:
            html = await self.fetch_html(url)
            if not html:
                return articles

            soup = self.parse_html(html)

            # Find news items (селекторы могут меняться, нужно проверить актуальную структуру)
            news_items = soup.select(".news-item, .item, article")

            for item in news_items[:20]:  # Берем последние 20 новостей
                try:
                    # Ищем заголовок
                    title_elem = item.select_one(".title, .news-item-title, h3, h2")
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Ищем ссылку
                    link_elem = item.select_one("a[href]")
                    if not link_elem:
                        continue

                    link = link_elem.get("href", "")
                    if link.startswith("/"):
                        link = f"{self.base_url}{link}"

                    # Ищем описание
                    desc_elem = item.select_one(".anons, .description, p")
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
                    logger.error(f"Error parsing Sports.ru news item: {e}")
                    continue

            logger.info(f"Parsed {len(articles)} articles from Sports.ru")

        except Exception as e:
            logger.error(f"Error parsing Sports.ru: {e}")

        return articles
