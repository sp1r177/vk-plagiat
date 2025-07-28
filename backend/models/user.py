from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from database.database import Base
import enum


class SubscriptionType(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    
    # Подписка
    subscription_type = Column(Enum(SubscriptionType), default=SubscriptionType.FREE)
    subscription_expires = Column(DateTime, nullable=True)
    
    # Настройки
    notifications_enabled = Column(Boolean, default=True)
    max_groups = Column(Integer, default=1)
    
    # Статистика
    total_plagiarism_found = Column(Integer, default=0)
    notifications_sent_today = Column(Integer, default=0)
    last_notification_date = Column(DateTime, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True) 