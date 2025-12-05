from pydantic import BaseModel, Field
from uuid import UUID

class UserModel(BaseModel):
    id:UUID = Field(
        default=None, description="user uuid"
    )
    permissions: list