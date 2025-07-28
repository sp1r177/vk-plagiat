from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base


class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    vk_group_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    screen_name = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Владелец группы
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="groups")
    
    # Настройки мониторинга
    is_active = Column(Boolean, default=True)
    check_text = Column(Boolean, default=True)
    check_images = Column(Boolean, default=True)
    exclude_reposts = Column(Boolean, default=True)
    
    # Статистика
    posts_checked = Column(Integer, default=0)
    plagiarism_found = Column(Integer, default=0)
    last_check = Column(DateTime, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 