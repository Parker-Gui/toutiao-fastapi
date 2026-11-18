from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import news
from schemas.base import NewsItemBase

router = APIRouter(prefix="/api/news", tags=["news"])

"""
接口实现流程
1. 模块化路由 -> API接口规范文档
2. 定义模型类 -> 数据库表
3. 在crud.py中实现增删改查方法 -> 数据库操作
4. 在路由处理函数中调用crud封装好的方法，响应结果
"""


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    # 先获取数据库里面新闻分类数据
    categories = await news.get_categories(db, skip, limit)
    return {"code": 200, "message": "success", "data": categories}


@router.get("/list")
async def get_news_list(
    db: AsyncSession = Depends(get_db),
    category_id: int = Query(..., alias="categoryId", description="新闻分类ID"),
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100, description="每页显示数量"),
):
    """
    处理分页规则， 查询新闻列表， 计算总量， 计算是否还有更多
    """
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    has_more = (offset + len(news_list)) < total
    # 统一成前端约定的驼峰字段（categoryId / publishTime），与详情接口保持一致
    items = [
        NewsItemBase.model_validate(item).model_dump(by_alias=True)
        for item in news_list
    ]
    return {
        "code": 200,
        "message": "success",
        "data": {"list": items, "total": total, "hasMore": has_more},
    }


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="newsId"), db: AsyncSession = Depends(get_db)
):
    """
    获取新闻详情， 浏览量+1， 相关新闻
    """
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    views_res = await news.increment_news_views(db, news_detail.id)  # 浏览量+1
    if not views_res:
        raise HTTPException(status_code=404, detail="浏览量更新失败")

    related_news = await news.get_related_news(
        db, news_detail.category_id, news_detail.id
    )

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        },
    }
