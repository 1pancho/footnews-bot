"""Database connection and operations."""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, delete
from .models import Base, User, UserClub, NewsItem

logger = logging.getLogger(__name__)


class Database:
    """Database manager."""

    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()
        logger.info("Database connection closed")

    # User operations
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """Get existing user or create new one."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Update user info
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
            else:
                # Create new user
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                )
                session.add(user)

            await session.commit()
            await session.refresh(user)
            return user

    async def get_user_clubs(self, telegram_id: int) -> List[str]:
        """Get list of clubs selected by user."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return []

            result = await session.execute(
                select(UserClub).where(UserClub.user_id == user.id)
            )
            clubs = result.scalars().all()
            return [club.club_name for club in clubs]

    async def add_user_club(self, telegram_id: int, club_name: str) -> bool:
        """Add club to user's selection."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Check if club already exists
            result = await session.execute(
                select(UserClub).where(
                    UserClub.user_id == user.id, UserClub.club_name == club_name
                )
            )
            existing = result.scalar_one_or_none()

            if not existing:
                user_club = UserClub(user_id=user.id, club_name=club_name)
                session.add(user_club)
                await session.commit()

            return True

    async def remove_user_club(self, telegram_id: int, club_name: str) -> bool:
        """Remove club from user's selection."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            await session.execute(
                delete(UserClub).where(
                    UserClub.user_id == user.id, UserClub.club_name == club_name
                )
            )
            await session.commit()
            return True

    async def clear_user_clubs(self, telegram_id: int) -> bool:
        """Clear all clubs from user's selection."""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            await session.execute(delete(UserClub).where(UserClub.user_id == user.id))
            await session.commit()
            return True

    # News operations
    async def add_news_item(
        self,
        title: str,
        url: str,
        source: str,
        description: Optional[str] = None,
        clubs_mentioned: Optional[List[str]] = None,
    ) -> Optional[NewsItem]:
        """Add news item to database."""
        async with self.async_session() as session:
            # Check if news already exists
            result = await session.execute(select(NewsItem).where(NewsItem.url == url))
            existing = result.scalar_one_or_none()

            if existing:
                return None

            clubs_str = ",".join(clubs_mentioned) if clubs_mentioned else ""
            news_item = NewsItem(
                title=title,
                url=url,
                source=source,
                description=description,
                clubs_mentioned=clubs_str,
            )
            session.add(news_item)
            await session.commit()
            await session.refresh(news_item)
            return news_item

    async def get_recent_news(
        self, limit: int = 50, clubs: Optional[List[str]] = None
    ) -> List[NewsItem]:
        """Get recent news items, optionally filtered by clubs."""
        async with self.async_session() as session:
            query = select(NewsItem).order_by(NewsItem.created_at.desc()).limit(limit)
            result = await session.execute(query)
            news_items = result.scalars().all()

            if clubs:
                # Filter by clubs
                filtered_news = []
                for item in news_items:
                    if item.clubs_mentioned:
                        item_clubs = [c.strip() for c in item.clubs_mentioned.split(",")]
                        if any(club in item_clubs for club in clubs):
                            filtered_news.append(item)
                return filtered_news

            return list(news_items)

    async def news_exists(self, url: str) -> bool:
        """Check if news item exists in database."""
        async with self.async_session() as session:
            result = await session.execute(select(NewsItem).where(NewsItem.url == url))
            return result.scalar_one_or_none() is not None
