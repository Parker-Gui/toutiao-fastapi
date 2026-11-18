from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import favorite, history, news, users
from utils.exception_handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)  # 注册全局异常处理器

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# 挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
# 运行命令 uv run uvicorn main:app --reload
