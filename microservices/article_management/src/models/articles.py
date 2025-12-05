from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

from src.models import PyObjectId, SysMixin


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleCreateModel(BaseModel):
    title: str = Field(description="Title of the article")
    author: str = Field(description="Author name")
    article_content: str = Field(description="Full article content")
    publish_date: datetime = Field(description="Publish date of the article in ISO format")
    status: ArticleStatus = ArticleStatus.DRAFT


class ArticleUpdateModel(BaseModel):
    title: Optional[str] = Field(None, description="Title of the article")
    author: Optional[str] = Field(None, description="Author name")
    article_content: Optional[str] = Field(None, description="Full article content")
    publish_date: Optional[datetime] = Field(None, description="Publish date of the article in ISO format")
    status: Optional[ArticleStatus] = Field(None, description="Status of the article")
    

class ArticleModel(BaseModel, SysMixin):
    id: Optional[PyObjectId] = Field(
        default=None, alias="_id", description="MongoDB ObjectId"
    )
    title: str
    author: str
    article_content: str
    publish_date: datetime
    star_ratio: Decimal = Field(default=Decimal("0.0"))
    review_count :int = Field(default=0)
    status: ArticleStatus = ArticleStatus.DRAFT

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True