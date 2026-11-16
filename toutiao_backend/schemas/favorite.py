from pydantic import BaseModel, Field


class FavoriteCheckRequest(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")
