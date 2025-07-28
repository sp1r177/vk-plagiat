import httpx
from config.settings import settings
from typing import Dict, Optional


class VKAuthService:
    def __init__(self):
        self.app_id = settings.VK_APP_ID
        self.app_secret = settings.VK_APP_SECRET
        self.redirect_uri = "https://your-domain.com/auth/callback"
    
    async def get_user_data(self, code: str) -> Dict:
        """Получение данных пользователя по коду авторизации"""
        try:
            # Обмен кода на access token
            token_url = "https://oauth.vk.com/access_token"
            params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "redirect_uri": self.redirect_uri,
                "code": code
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(token_url, params=params)
                response.raise_for_status()
                token_data = response.json()
            
            access_token = token_data["access_token"]
            user_id = token_data["user_id"]
            
            # Получение информации о пользователе
            user_info = await self._get_user_info(access_token, user_id)
            
            return {
                "vk_id": user_id,
                "access_token": access_token,
                **user_info
            }
            
        except Exception as e:
            raise Exception(f"Ошибка получения данных пользователя: {str(e)}")
    
    async def _get_user_info(self, access_token: str, user_id: int) -> Dict:
        """Получение информации о пользователе"""
        try:
            url = "https://api.vk.com/method/users.get"
            params = {
                "user_ids": user_id,
                "fields": "screen_name,photo_100",
                "access_token": access_token,
                "v": "5.131"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            user = data["response"][0]
            
            return {
                "username": user.get("screen_name"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "photo_url": user.get("photo_100")
            }
            
        except Exception as e:
            raise Exception(f"Ошибка получения информации о пользователе: {str(e)}")
    
    def get_auth_url(self) -> str:
        """Получение URL для авторизации"""
        return (
            f"https://oauth.vk.com/authorize?"
            f"client_id={self.app_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope=groups,wall,photos&"
            f"response_type=code&"
            f"v=5.131"
        ) 