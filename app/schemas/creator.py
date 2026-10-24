from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.portfolio import PortfolioItemResponse

class VerificationSignalResponse(BaseModel):
    id: int
    signal_type: str
    badge_name: str
    description: str | None = None
    verified_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CreatorProfileBase(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=255)
    headline: str | None = None
    bio: str | None = None
    specialization: str | None = None
    skills: str | None = None  # Comma-separated
    tools_models: str | None = None  # Comma-separated
    workflow: str | None = None
    experience_level: str | None = None
    location: str | None = None
    profile_image_url: str | None = None

class CreatorProfileCreate(CreatorProfileBase):
    pass

class CreatorProfileUpdate(BaseModel):
    display_name: str | None = None
    headline: str | None = None
    bio: str | None = None
    specialization: str | None = None
    skills: str | None = None
    tools_models: str | None = None
    workflow: str | None = None
    experience_level: str | None = None
    location: str | None = None
    profile_image_url: str | None = None

class CreatorProfileResponse(CreatorProfileBase):
    id: int
    user_id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    portfolio_items: list[PortfolioItemResponse] = []
    verification_signals: list[VerificationSignalResponse] = []

    model_config = ConfigDict(from_attributes=True)

class CreatorProfileBrief(BaseModel):
    id: int
    user_id: int
    display_name: str
    headline: str | None = None
    specialization: str | None = None
    skills: str | None = None
    tools_models: str | None = None
    location: str | None = None
    profile_image_url: str | None = None
    is_verified: bool
    portfolio_count: int = 0
    verification_signals: list[VerificationSignalResponse] = []

    model_config = ConfigDict(from_attributes=True)
