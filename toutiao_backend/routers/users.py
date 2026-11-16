from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import users
from models.users import User
from schemas.users import (
    UserAuthResponse,
    UserChangePasswordRequest,
    UserInfoResponse,
    UserRequest,
    UserUpdateRequest,
)
from utils.auth import get_current_user
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
async def get_user_info(user: User = Depends(get_current_user)):
    # 获取用户信息逻辑： 1.验证token是否有效 2.获取用户信息 3.响应结果
    return success_response(
        message="获取用户信息成功", data=UserInfoResponse.model_validate(user)
    )


# 修改用户信息：验证Token-> 更新（用户输入数据 -> put提交 -> 请求体参数 -> 定义Pydantic模型） -> 响应结果
# 参数：用户输入的 + 验证Token + db
@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user = await users.update_user(db, user.username, user_data)
    return success_response(
        message="更新用户信息成功", data=UserInfoResponse.model_validate(user)
    )


# 修改用户密码
@router.put("/password")
async def change_password(
    password_data: UserChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res_change_pwd = await users.change_password(
        db, user, password_data.old_password, password_data.new_password
    )
    if not res_change_pwd:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请稍后再试",
        )
    return success_response(message="修改密码成功")
