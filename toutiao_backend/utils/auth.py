# 根据Token查用户，返回用户信息
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import users


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(..., alias="Authorization"),
):
    # 1.验证token是否有效 2.获取用户信息 3.响应结果
    # 兼容两种写法：标准的 "Bearer <token>" 和直接传裸 token
    parts = authorization.split()
    token = parts[-1] if parts else ""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少 Token"
        )
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效或已过期"
        )

    return user
