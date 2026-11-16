from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite


async def is_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    # 查询数据库，判断是否收藏
    stmt = select(Favorite).where(
        Favorite.user_id == user_id, Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
