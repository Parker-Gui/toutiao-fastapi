from datetime import datetime as dt

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import (
    cache_news_detail,
    cache_related_news,
    get_cache_news_list,
    get_cached_categories,
    get_cached_news_detail,
    get_cached_related_news,
    set_cache_categories,
    set_cache_news_list,
)
from models.news import Category, News
from schemas.base import NewsItemBase


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    # 写入缓存 — 手动转字典避免 datetime 序列化问题
    if categories:
        cat_list = [
            {"id": c.id, "name": c.name, "description": c.description}
            for c in categories
        ]
        await set_cache_categories(cat_list)
    return categories


async def get_news_list(
    db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10
):
    # 先尝试从缓存获取新闻列表
    # 跳过的数量skip = (页码 - 1) * 每页数量 -> 页码 = 跳过的数量 // 每页数量 + 1
    # await get_cache_news_list(分类id, 页码, 每页数量)

    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)  # 缓存数据 json
    if cached_list:
        # return cached_list  # 要的是 ORM
        return [News(**item) for item in cached_list]

    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    # 写入缓存
    if news_list:
        # 先把 ORM 数据 转换 字典才能写入缓存
        # ORM 转成 Pydantic，再转为 字典
        # by_alias=False 不适用别名，保存 Python 风格，因为 Redis 数据是给后端用的
        news_data = [
            NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False)
            for item in news_list
        ]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list


async def get_news_count(db: AsyncSession, category_id: int):
    # 查询指定分类的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果，否则报错


async def get_news_detail(db: AsyncSession, news_id: int):
    # 先尝试从缓存获取新闻详情
    cached_detail = await get_cached_news_detail(news_id)
    # 从缓存中读取时需要把 ISO 格式字符串转回 datetime 再构建 ORM 对象
    if cached_detail:
        detail = dict(cached_detail)
        for field in ("publish_time", "created_at", "updated_at"):
            if detail.get(field) and isinstance(detail[field], str):
                detail[field] = dt.fromisoformat(detail[field])
        return News(**detail)

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()

    # 写入缓存 — 手动构造字典避免 datetime 序列化问题
    if news:
        news_data = {
            "id": news.id,
            "title": news.title,
            "description": news.description,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "category_id": news.category_id,
            "views": news.views,
            "publish_time": news.publish_time.isoformat() if news.publish_time else None,
            "created_at": news.created_at.isoformat() if news.created_at else None,
            "updated_at": news.updated_at.isoformat() if news.updated_at else None,
        }
        await cache_news_detail(news_id, news_data)

    return news  # 返回单个结果或None


async def increment_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 更新操作需要检查数据库是否真的命中数据， 命中了返回True， 没有命中返回False
    return result.rowcount > 0  # ty: ignore[missing-attribute]


async def get_related_news(
    db: AsyncSession, category_id: int, news_id: int, limit: int = 5
):
    # 先尝试从缓存获取相关新闻
    cached_related = await get_cached_related_news(news_id, category_id)
    if cached_related:
        return cached_related

    stmt = (
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(News.views.desc(), News.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    related_list = [
        {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "image": item.image,
            "author": item.author,
            "publishTime": item.publish_time,
            "categoryId": item.category_id,
            "views": item.views,
        }
        for item in related_news
    ]

    # 写入缓存
    if related_list:
        await cache_related_news(news_id, category_id, related_list)

    return related_list
