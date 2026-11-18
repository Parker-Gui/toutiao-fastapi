from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def is_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    # 查询数据库，判断是否收藏
    stmt = select(Favorite).where(
        Favorite.user_id == user_id, Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id, Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0  # 返回是否成功删除  # ty: ignore[missing-attribute]


# 获取收藏列表：获取的是某个用户的收藏列表 + 分页功能
async def get_favorite_list(
    db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10
):
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 获取收藏列表-联表查询 join + 收藏时间排序 + 分页
    query = (
        select(
            News,
            Favorite.created_at.label("favorite_time"),
            Favorite.id.label("favorite_id"),
        )
        .join(Favorite, News.id == Favorite.news_id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return total, rows


async def clear_all_favorite(db: AsyncSession, user_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    # 返回删除数量
    return result.rowcount or 0  # ty: ignore[missing-attribute]
