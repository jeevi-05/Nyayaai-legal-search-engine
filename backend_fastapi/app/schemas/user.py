from datetime import datetime
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    model_config = {"from_attributes": True, "populate_by_name": True}

    id: int
    email: str
    full_name: str = Field(serialization_alias="fullName")
    role: str
    created_at: datetime = Field(serialization_alias="createdAt")
