from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data=None):
    # 把任何FastAPI、Pydantic、ORM对象都要响应成：code、message、data
    content = {"code": 200, "message": message, "data": data}

    return JSONResponse(content=jsonable_encoder(content))
