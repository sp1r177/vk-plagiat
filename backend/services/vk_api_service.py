import vk_api
import httpx
from typing import List, Dict, Optional
from config.settings import settings
import time
import logging

logger = logging.getLogger(__name__)


class VKAPIService:
    def __init__(self):
        self.access_token = settings.VK_ACCESS_TOKEN
        self.group_token = settings.VK_GROUP_TOKEN
        self.vk_session = vk_api.VkApi(token=self.access_token)
        self.vk = self.vk_session.get_api()
        
        # Настройки для обработки ошибок
        self.max_retries = 3
        self.retry_delay = 1  # секунды
        
    def _handle_vk_error(self, error, operation: str):
        """Обработка ошибок VK API"""
        error_code = getattr(error, 'code', None)
        
        if error_code == 6:  # Too many requests per second
            logger.warning(f"VK API: Слишком много запросов для {operation}")
            time.sleep(self.retry_delay)
            return True  # Повторить
        elif error_code == 5:  # Invalid token
            logger.error(f"VK API: Неверный токен для {operation}")
            return False
        elif error_code == 15:  # Access denied
            logger.warning(f"VK API: Доступ запрещен для {operation}")
            return False
        else:
            logger.error(f"VK API ошибка {error_code} для {operation}: {error}")
            return False
    
    async def get_group_info(self, group_id: int) -> Optional[Dict]:
        """Получение информации о группе с обработкой ошибок"""
        for attempt in range(self.max_retries):
            try:
                # Убираем минус для групп
                group_id_positive = abs(group_id)
                
                response = self.vk.groups.getById(
                    group_id=group_id_positive,
                    fields="description,photo_100"
                )
                
                if response:
                    group = response[0]
                    return {
                        "id": group["id"],
                        "name": group["name"],
                        "screen_name": group.get("screen_name"),
                        "photo_url": group.get("photo_100"),
                        "description": group.get("description")
                    }
                
            except Exception as e:
                if hasattr(e, 'code') and self._handle_vk_error(e, f"get_group_info({group_id})"):
                    continue  # Повторить
                else:
                    logger.error(f"Ошибка получения информации о группе {group_id}: {e}")
                    break
        
        return None
    
    async def get_group_posts(self, group_id: int, count: int = 100) -> List[Dict]:
        """Получение постов группы с обработкой ошибок"""
        for attempt in range(self.max_retries):
            try:
                # Убираем минус для групп
                group_id_positive = abs(group_id)
                
                response = self.vk.wall.get(
                    owner_id=-group_id_positive,
                    count=min(count, 100),  # Ограничиваем количество
                    extended=1
                )
                
                posts = response.get("items", [])
                
                # Фильтруем репосты если нужно
                filtered_posts = []
                for post in posts:
                    if not self._is_repost(post):
                        filtered_posts.append(post)
                
                return filtered_posts
                
            except Exception as e:
                if hasattr(e, 'code') and self._handle_vk_error(e, f"get_group_posts({group_id})"):
                    continue  # Повторить
                else:
                    logger.error(f"Ошибка получения постов группы {group_id}: {e}")
                    break
        
        return []
    
    async def get_post_info(self, post_id: str) -> Optional[Dict]:
        """Получение информации о конкретном посте"""
        try:
            # Парсим post_id (формат: group_id_post_id)
            parts = post_id.split("_")
            if len(parts) != 2:
                return None
            
            owner_id = int(parts[0])
            post_id_num = int(parts[1])
            
            response = self.vk.wall.getById(
                posts=f"{owner_id}_{post_id_num}"
            )
            
            if response:
                return response[0]
            
        except Exception as e:
            print(f"Ошибка получения информации о посте {post_id}: {e}")
        
        return None
    
    def _is_repost(self, post: Dict) -> bool:
        """Проверка, является ли пост репостом"""
        # Проверка copy_history
        if 'copy_history' in post and post['copy_history']:
            return True
        
        # Проверка текста на ключевые слова
        text = post.get('text', '').lower()
        repost_keywords = ['репост', 'repost', 'поделился', 'поделилась', 'поделились']
        
        for keyword in repost_keywords:
            if keyword in text:
                return True
        
        # Проверка attachments на wall
        attachments = post.get('attachments', [])
        for attachment in attachments:
            if attachment.get('type') == 'wall':
                return True
        
        return False
    
    async def send_message(self, user_id: int, message: str, keyboard: Optional[Dict] = None) -> bool:
        """Отправка сообщения пользователю с обработкой ошибок"""
        for attempt in range(self.max_retries):
            try:
                params = {
                    "user_id": user_id,
                    "message": message,
                    "random_id": int(time.time() * 1000)  # Уникальный ID
                }
                
                if keyboard:
                    params["keyboard"] = keyboard
                
                self.vk.messages.send(**params)
                logger.info(f"Сообщение отправлено пользователю {user_id}")
                return True
                
            except Exception as e:
                if hasattr(e, 'code') and self._handle_vk_error(e, f"send_message({user_id})"):
                    continue  # Повторить
                else:
                    logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                    break
        
        return False
    
    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        try:
            response = self.vk.users.get(
                user_ids=user_id,
                fields="screen_name,photo_100"
            )
            
            if response:
                user = response[0]
                return {
                    "id": user["id"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "screen_name": user.get("screen_name"),
                    "photo_url": user.get("photo_100")
                }
            
        except Exception as e:
            print(f"Ошибка получения информации о пользователе {user_id}: {e}")
        
        return None
    
    def parse_button_payload(self, payload: str) -> Optional[Dict]:
        """Парсинг payload кнопки для определения действия"""
        try:
            if payload.startswith("confirm_plagiarism_"):
                plagiarism_id = int(payload.split("_")[-1])
                return {
                    "action": "confirm_plagiarism",
                    "plagiarism_id": plagiarism_id
                }
            elif payload.startswith("false_positive_"):
                plagiarism_id = int(payload.split("_")[-1])
                return {
                    "action": "false_positive",
                    "plagiarism_id": plagiarism_id
                }
            else:
                return None
        except Exception as e:
            print(f"Ошибка парсинга payload кнопки: {e}")
            return None
    
    def create_complaint_url(self, group_id: int, post_id: str) -> str:
        """Создание URL для жалобы на пост"""
        try:
            # Извлекаем ID поста из полного ID
            post_id_num = post_id.split("_")[-1]
            return f"https://vk.com/support?act=report&type=post&owner_id={group_id}&item_id={post_id_num}"
        except Exception as e:
            print(f"Ошибка создания URL жалобы: {e}")
            return "" 
    
    async def get_user_groups(self, user_id: int) -> List[Dict]:
        """Получение групп пользователя"""
        for attempt in range(self.max_retries):
            try:
                response = self.vk.groups.get(
                    user_id=user_id,
                    extended=1,
                    fields="description,photo_100"
                )
                
                groups = response.get("items", [])
                return groups
                
            except Exception as e:
                if hasattr(e, 'code') and self._handle_vk_error(e, f"get_user_groups({user_id})"):
                    continue  # Повторить
                else:
                    logger.error(f"Ошибка получения групп пользователя {user_id}: {e}")
                    break
        
        return []
    
    async def get_post_by_id(self, owner_id: int, post_id: str) -> Optional[Dict]:
        """Получение поста по ID"""
        for attempt in range(self.max_retries):
            try:
                response = self.vk.wall.getById(
                    posts=f"{owner_id}_{post_id}"
                )
                
                if response:
                    return response[0]
                
            except Exception as e:
                if hasattr(e, 'code') and self._handle_vk_error(e, f"get_post_by_id({owner_id}_{post_id})"):
                    continue  # Повторить
                else:
                    logger.error(f"Ошибка получения поста {owner_id}_{post_id}: {e}")
                    break
        
        return None 