import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
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


async def get_user_by_token(db: AsyncSession, token: str):
    # 根据token查询用户信息，验证token是否过期
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if not user_token:
        return None
    if user_token.expires_at < datetime.now():
        return None

    stmt = select(User).where(User.id == user_token.user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 更新用户信息
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # 根据用户名查询用户，更新用户信息
    # user_data 是一个Pydantic模型对象，里面包含了用户输入的更新信息，需要用**解包
    # 用户没有设置的字段不更新
    query = (
        update(User)
        .where(User.username == username)
        .values(**user_data.model_dump(exclude_unset=True, exclude_none=True))
    )
    result = await db.execute(query)
    await db.commit()

    # 检查更新
    if result.rowcount == 0:  # ty: ignore[missing-attribute]
        raise HTTPException(status_code=404, detail="用户不存在或未更新任何信息")

    # 获取更新后的用户信息
    updated_user = await get_user_by_username(db, username)
    return updated_user


# 修改用户密码：验证旧密码 -> 新密码加密 -> 更新数据库
async def change_password(
    db: AsyncSession, user: User, old_password: str, new_password: str
):
    if not security.verify_password(old_password, user.password):
        return False

    hashed_new_password = security.get_hash_password(new_password)
    user.password = hashed_new_password
    db.add(
        user
    )  # 更新：有SQLAlchemy真正接管这个user对象，确保可以commit，规避session过期或者关闭导致不能提交
    await db.commit()
    await db.refresh(user)
    return True
