from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class ProfileBase(BaseModel):
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    orcid_id: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
