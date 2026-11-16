import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest
from utils import security


# 根据用户名来查询
async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    # 先给密码hash加密，再add
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 从数据库读回最新的user
    return user


# 生成 Token
async def create_token(db: AsyncSession, user_id: int):
    # 生成Token， 设置过期时间， 查询数据库当前用户是否有Token， 有：更新；没有：添加
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)  # 设置过期时间为7days
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token

async def authenticate_user(db: AsyncSession, username: str, password: str):
    # 验证用户是否存在，验证密码是否正确
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None
    return user