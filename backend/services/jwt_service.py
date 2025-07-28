from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from config.settings import settings


class JWTService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[int]:
        """Проверка и декодирование JWT токена"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except JWTError:
            return None
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Декодирование JWT токена без проверки"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None 