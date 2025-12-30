import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserProfileBase(BaseModel):
    """Base schema for user profile data."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric and underscores only)",
    )
    display_name: str | None = Field(
        None,
        max_length=100,
        description="Display name shown in the UI",
    )


class UserProfileCreate(UserProfileBase):
    """Schema for creating a user profile."""

    pass


class UserProfileUpdate(BaseModel):
    """Schema for updating a user profile."""

    username: str | None = Field(
        None,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric and underscores only)",
    )
    display_name: str | None = Field(
        None,
        max_length=100,
        description="Display name shown in the UI",
    )


class UserProfileResponse(UserProfileBase):
    """Schema for user profile responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    supabase_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
