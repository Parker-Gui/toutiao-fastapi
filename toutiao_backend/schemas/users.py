from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6, max_length=20)


# user_info对应的类：基础类 + Info 类（id、用户名等）
class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """

    nickname: str | None = Field(None, max_length=50, description="用户昵称")
    avatar: str | None = Field(None, max_length=255, description="用户头像")
    gender: str | None = Field(None, max_length=10, description="用户性别")
    bio: str | None = Field(None, max_length=500, description="用户简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True,  # 允许从ORM对象中读取数据
    )


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True,  # alias / 字段名兼容
        from_attributes=True,  # 允许从ORM对象中读取数据
    )

# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="用户昵称")
    avatar: str | None = Field(None, max_length=255, description="用户头像")
    gender: str | None = Field(None, max_length=10, description="用户性别")
    bio: str | None = Field(None, max_length=500, description="用户简介")


#修改用户密码
class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=20, description="旧密码", alias="oldPassword")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码", alias="newPassword")