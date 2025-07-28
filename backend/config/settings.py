import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/plagiarism_detector")
    
    # VK API
    VK_ACCESS_TOKEN: str = os.getenv("VK_ACCESS_TOKEN", "")
    VK_GROUP_TOKEN: str = os.getenv("VK_GROUP_TOKEN", "")
    VK_APP_ID: str = os.getenv("VK_APP_ID", "")
    VK_APP_SECRET: str = os.getenv("VK_APP_SECRET", "")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Мониторинг
    MONITORING_INTERVAL_HOURS: int = 12  # 2 раза в день
    MAX_NOTIFICATIONS_PER_DAY: int = 10
    SIMILARITY_THRESHOLD: float = 0.7  # Порог схожести для плагиата
    
    # Платежи
    VK_PAY_MERCHANT_ID: str = os.getenv("VK_PAY_MERCHANT_ID", "")
    VK_PAY_SECRET_KEY: str = os.getenv("VK_PAY_SECRET_KEY", "")
    
    # Тарифы (в копейках)
    PRICING = {
        "free": {"groups": 1, "days": 1, "price": 0},
        "basic": {"groups": 1, "days": 30, "price": 29900},
        "standard": {"groups": 5, "days": 30, "price": 79900},
        "premium": {"groups": 10, "days": 30, "price": 119900}
    }
    
    # Настройки приложения
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = "0.0.0.0"
    PORT: int = 8000


settings = Settings() 