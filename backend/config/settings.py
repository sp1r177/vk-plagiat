import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = "postgresql://user:password@localhost/plagiarism_detector"
    
    # VK API
    VK_ACCESS_TOKEN: Optional[str] = None
    VK_GROUP_TOKEN: Optional[str] = None
    VK_APP_ID: Optional[str] = None
    VK_APP_SECRET: Optional[str] = None
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # Платежи
    VK_PAY_MERCHANT_ID: Optional[str] = None
    VK_PAY_SECRET_KEY: Optional[str] = None
    
    # Настройки приложения
    DEBUG: bool = True
    
    # Настройки детекции плагиата для MVP
    TEXT_SIMILARITY_THRESHOLD: float = 0.7  # 70% как в требованиях MVP
    IMAGE_HAMMING_THRESHOLD: int = 10       # Расстояние Хэмминга ≤10
    MIN_TEXT_LENGTH: int = 20               # Минимальная длина текста для анализа
    
    # Настройки мониторинга
    MONITORING_INTERVAL_HOURS: int = 3      # Каждые 3 часа как в требованиях
    MAX_POSTS_PER_GROUP: int = 100          # Максимум постов для анализа
    MAX_GROUPS_TO_MONITOR: int = 50         # Максимум групп для мониторинга
    
    # Настройки кэширования
    CACHE_DURATION_HOURS: int = 24          # Время жизни кэша
    MAX_CACHE_SIZE: int = 1000              # Максимальный размер кэша
    
    # Настройки уведомлений
    NOTIFICATION_ENABLED: bool = True
    MAX_NOTIFICATIONS_PER_DAY: int = 10     # Максимум уведомлений в день
    
    class Config:
        env_file = ".env"


settings = Settings() 