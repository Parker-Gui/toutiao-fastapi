from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

"""
浏览历史模块的router：
1. 添加浏览记录
2. 删除单挑浏览记录
3. 获取浏览历史列表
4. 清空浏览历史列表
"""
router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    1. 进去请求，用请求头Header来获取authorization的token，验证用户是否登录，未登录抛出异常
    2. 已经登陆则检查是否浏览过当前新闻，是则更新浏览时间，否则添加浏览记录
    3. 响应结果
    """
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加浏览记录成功", data=result)


@router.delete("/remove")
async def remove_history(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    1. 进入请求，用请求头Header来获取authorization的token，验证用户是否登录，未登录抛出异常
    2.已经登陆则删除浏览记录
    3.检查命中数量，>0 则响应结果，否则抛出异常
    """
    delete_result = await history.remove_history(db, user.id, news_id)
    if not delete_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="浏览记录不存在"
        )
    return success_response(message="删除浏览记录成功")


@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    1. 进入请求，用请求头Header来获取authorization的token，验证用户是否登录，未登录抛出异常
    2. 已经登陆则获取浏览历史列表
    3. 定义一个浏览历史列表的schema作为data返回
    """
    total, rows = await history.get_history_list(db, user.id, page, page_size)
    history_list = [
        {
            **news.__dict__,
            "view_time": view_time,
            "history_id": history_id,
        }
        for news, view_time, history_id in rows
    ]

    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取浏览历史列表成功", data=data)

@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    1. 进入请求，用请求头Header来获取authorization的token，验证用户是否登录，未登录抛出异常
    2. 已经登陆则清空浏览历史列表
    3. 响应结果
    """
    clear_count = await history.clear_all_history(db, user.id)
    return success_response(message=f"清空{clear_count}条浏览记录")