from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history(db: AsyncSession, user_id: int, news_id: int):
    """
    添加历史浏览记录，如果已经存在则更新浏览时间
    """
    query = select(History).where(
        History.user_id == user_id, History.news_id == news_id
    )
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()

    if existing_history:
        # 如果已经存在，则更新浏览时间
        existing_history.view_time = func.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        new_history = History(user_id=user_id, news_id=news_id)
        db.add(new_history)
        await db.commit()
        await db.refresh(new_history)
        return new_history


async def remove_history(db: AsyncSession, user_id: int, news_id: int):
    query = delete(History).where(
        History.user_id == user_id, History.news_id == news_id
    )
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0  # ty: ignore[missing-attribute]


async def get_history_list(db: AsyncSession, user_id: int, page: int, page_size: int):
    query = (
        select(
            News, History.view_time.label("view_time"), History.id.label("history_id")
        )
        .join(History, News.id == History.news_id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    rows = result.all()

    count_query = select(func.count(History.id)).where(History.user_id == user_id)
    count_res = await db.execute(count_query)
    total = count_res.scalar_one()

    return total, rows


async def clear_all_history(db: AsyncSession, user_id: int):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0  # 返回删除数量  # ty: ignore[missing-attribute]
