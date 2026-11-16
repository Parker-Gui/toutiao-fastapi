from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import users
from schemas.users import UserAuthResponse, UserInfoResponse, UserRequest
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 注册逻辑： 1.验证用户是否存在 2.创建用户 3.生成token 4.响应结果
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    """ return {
        "code": 200,
        "message": "success",
        "data": {
            "token": token,
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "bio": user.bio,
                "avatar": user.avatar,
            },
        },
    } """
    response_data = UserAuthResponse(
        token=token, user_info=UserInfoResponse.model_validate(user)
    )
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑： 1.验证用户是否存在 2.验证密码是否正确 3.生成token 4.响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(
        token=token, user_info=UserInfoResponse.model_validate(user)
    )
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info():
    return success_response(message="获取用户信息成功", data={})