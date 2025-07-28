from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GroupCreate(BaseModel):
    vk_group_id: int
    check_text: bool = True
    check_images: bool = True
    exclude_reposts: bool = True


class GroupUpdate(BaseModel):
    check_text: Optional[bool] = None
    check_images: Optional[bool] = None
    exclude_reposts: Optional[bool] = None


class GroupResponse(BaseModel):
    id: int
    vk_group_id: int
    name: str
    screen_name: Optional[str] = None
    photo_url: Optional[str] = None
    description: Optional[str] = None
    user_id: int
    is_active: bool
    check_text: bool
    check_images: bool
    exclude_reposts: bool
    posts_checked: int
    plagiarism_found: int
    last_check: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 