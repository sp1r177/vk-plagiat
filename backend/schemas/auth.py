from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.user import SubscriptionType


class UserCreate(BaseModel):
    vk_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    vk_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    subscription_type: SubscriptionType
    subscription_expires: Optional[datetime] = None
    notifications_enabled: bool
    max_groups: int
    total_plagiarism_found: int
    notifications_sent_today: int
    last_notification_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None 