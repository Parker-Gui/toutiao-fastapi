# toutiao-fastapi

一个头条风格的资讯应用，采用前后端分离架构。本仓库当前包含后端服务，基于 **FastAPI + 异步 SQLAlchemy + MySQL** 实现新闻资讯与用户模块，提供 RESTful 接口。

## 技术栈

| 分类 | 技术 |
| --- | --- |
| 语言 | Python 3.14 |
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.0（asyncio） |
| 数据库 | MySQL 8 / aiomysql |
| 数据校验 | Pydantic v2 |
| 密码哈希 | pwdlib（bcrypt） |
| 依赖管理 | uv |
| 代码检查 | Ruff / ty |

## 项目结构

```
.
└── toutiao_backend/
    ├── main.py             # 应用入口，注册中间件与路由
    ├── config/             # 数据库引擎与会话管理
    ├── models/             # SQLAlchemy ORM 模型
    ├── schemas/            # Pydantic 请求 / 响应模型
    ├── crud/               # 数据访问层，封装查询逻辑
    ├── routers/            # 路由与接口实现
    ├── utils/              # 统一响应、全局异常处理、密码工具
    └── database.sql        # 建表语句与初始化数据
```

分层思路：`routers` 负责协议与参数，`crud` 只管 SQL，`models` 描述表结构，`schemas` 约束输入输出。

## 快速开始

**环境要求**：Python 3.14+、MySQL 8、[uv](https://docs.astral.sh/uv/)

```bash
# 1. 初始化数据库（建库、建表、写入示例数据）
mysql -u root -p < toutiao_backend/database.sql

# 2. 安装依赖
cd toutiao_backend
uv sync

# 3. 修改数据库连接串
#    编辑 config/db_config.py 中的 ASYNC_DATABASE_URL

# 4. 启动服务
uv run uvicorn main:app --reload
```

启动后：

- 接口文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/

## 接口一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/news/categories` | 获取新闻分类列表 |
| GET | `/api/news/list` | 新闻列表，支持分类筛选与分页 |
| GET | `/api/news/detail` | 新闻详情，含浏览量自增与相关推荐 |
| POST | `/api/user/register` | 用户注册 |
| POST | `/api/user/login` | 用户登录 |

统一响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 开发进度

- [x] 新闻分类、列表、详情
- [x] 用户注册、登录（bcrypt 密码哈希 + Token 鉴权）
- [ ] 收藏与浏览历史
- [ ] 个人中心
- [ ] 前端应用
