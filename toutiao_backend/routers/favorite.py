from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import favorite
from models.users import User
from schemas.favorite import (
    FavoriteAddRequest,
    FavoriteCheckRequest,
    FavoriteListResponse,
)
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    检查是否收藏
    :param user_id: 用户ID
    :return: 是否收藏
    """
    is_favorited = await favorite.is_news_favorite(db, user.id, news_id)
    return success_response(
        message="检查收藏状态成功", data=FavoriteCheckRequest(isFavorite=is_favorited)
    )


@router.post("/add")
async def add_favorite(
    data: FavoriteAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    return success_response(message="收藏成功", data=result)


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    delete = await favorite.remove_news_favorite(db, user.id, news_id)
    if not delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在")
    return success_response(message="取消收藏成功")


@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total, rows = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [
        {
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id,
        }
        for news, favorite_time, favorite_id in rows
    ]
    has_more = total > page * page_size
    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(
        message="获取新闻收藏列表成功",
        data=data,
    )


@router.delete("/clear")
async def clear_favorite(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 验证Token是否登录，清空当前哦那个收藏新闻
    clear_count = await favorite.clear_all_favorite(db, user.id)
    return success_response(message=f"清空{clear_count}条收藏记录")
