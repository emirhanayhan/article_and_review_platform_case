from typing import Optional
from pydantic import BaseModel, Field, field_validator

from src.models import SysMixin, PyObjectId

class ReviewModel(BaseModel, SysMixin):
    id: Optional[PyObjectId] = Field(
        default=None, description="MongoDB ObjectId", alias="_id"
    )
    article_id: str = Field(..., description="ID of the related article")

    # since we have reviewer id in created_by
    # this can be ignored
    # reviewer: str = Field(min_length=1, description="Name of the reviewer")

    review_content: str = Field(min_length=1, max_length=120, description="comment to article")
    star_ratio: int = Field(
        ...,
        ge=1,
        le=5,
        description="Star rating from 1 to 5 required field"
    )

class ReviewCreateModel(BaseModel):
    article_id: str = Field(..., description="ID of the related article")
    review_content: str = Field(min_length=1, max_length=120, description="comment to article")
    star_ratio: int = Field(
        ...,
        ge=1,
        le=5,
        description="Star rating from 1 to 5 required field"
    )

class ReviewUpdateModel(BaseModel):
    review_content: str = Field(min_length=1, max_length=120, description="comment to article")
    star_ratio: int = Field(
        ge=1,
        le=5,
        description="Star rating from 1 to 5 required field"
    )