from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from pydantic import Field, BaseModel

MAX_BATCH_SIZE = 100


def to_jsonable(data):
    return jsonable_encoder(
        data,
        custom_encoder={
            ObjectId: str
        }
    )


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(str(value))
        except Exception:
            raise ValueError("Invalid ObjectId")

class SysMixin:
    # Default for database models
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default_factory=str)
    updated_by: str = Field(default_factory=str)

class QueryParamsModel(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=MAX_BATCH_SIZE)
    filter: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_dir: Optional[int] = 1
    select: Optional[List[str]] = None 
