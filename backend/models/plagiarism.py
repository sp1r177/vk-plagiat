from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base


class Plagiarism(Base):
    __tablename__ = "plagiarism_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Группа, где найден плагиат
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    group = relationship("Group", back_populates="plagiarism_cases")
    
    # Оригинальный пост
    original_post_id = Column(String, nullable=False)  # VK post ID
    original_group_id = Column(Integer, nullable=False)
    original_text = Column(Text, nullable=True)
    original_images = Column(JSON, nullable=True)  # Список URL изображений
    
    # Пост с плагиатом
    plagiarized_post_id = Column(String, nullable=False)
    plagiarized_group_id = Column(Integer, nullable=False)
    plagiarized_text = Column(Text, nullable=True)
    plagiarized_images = Column(JSON, nullable=True)
    
    # Анализ схожести
    text_similarity = Column(Float, nullable=True)
    image_similarity = Column(Float, nullable=True)
    overall_similarity = Column(Float, nullable=False)
    
    # Статус
    is_confirmed = Column(Boolean, default=False)
    is_false_positive = Column(Boolean, default=False)
    
    # Уведомления
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 