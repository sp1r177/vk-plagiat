from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.group import Group
from models.user import User
from services.vk_api_service import VKAPIService
from monitoring.plagiarism_detector import PlagiarismDetector
from notifications.notification_service import NotificationService
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.vk_api = VKAPIService()
        self.detector = PlagiarismDetector()
        self.notification_service = NotificationService()
    
    def start(self):
        """Запуск планировщика"""
        # Мониторинг в 09:00
        self.scheduler.add_job(
            self.run_monitoring,
            CronTrigger(hour=9, minute=0),
            id="morning_monitoring",
            name="Утренний мониторинг"
        )
        
        # Мониторинг в 18:00
        self.scheduler.add_job(
            self.run_monitoring,
            CronTrigger(hour=18, minute=0),
            id="evening_monitoring",
            name="Вечерний мониторинг"
        )
        
        self.scheduler.start()
        logger.info("Планировщик мониторинга запущен")
    
    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик мониторинга остановлен")
    
    async def run_monitoring(self):
        """Запуск мониторинга всех активных групп"""
        logger.info("Начинаем мониторинг групп")
        
        db = SessionLocal()
        try:
            # Получаем все активные группы
            active_groups = db.query(Group).filter(Group.is_active == True).all()
            
            for group in active_groups:
                try:
                    await self.monitor_group(group, db)
                except Exception as e:
                    logger.error(f"Ошибка мониторинга группы {group.id}: {e}")
            
            logger.info(f"Мониторинг завершен. Проверено групп: {len(active_groups)}")
            
        except Exception as e:
            logger.error(f"Ошибка в процессе мониторинга: {e}")
        finally:
            db.close()
    
    async def monitor_group(self, group: Group, db: Session):
        """Мониторинг конкретной группы"""
        logger.info(f"Мониторинг группы: {group.name} (ID: {group.vk_group_id})")
        
        # Получаем посты группы
        posts = await self.vk_api.get_group_posts(group.vk_group_id, count=50)
        
        if not posts:
            logger.warning(f"Не удалось получить посты для группы {group.name}")
            return
        
        # Обновляем статистику
        group.posts_checked += len(posts)
        group.last_check = datetime.utcnow()
        
        # Проверяем каждый пост на плагиат
        plagiarism_found = 0
        
        for post in posts:
            try:
                if await self.check_post_for_plagiarism(post, group, db):
                    plagiarism_found += 1
            except Exception as e:
                logger.error(f"Ошибка проверки поста {post.get('id')}: {e}")
        
        # Обновляем статистику группы
        group.plagiarism_found += plagiarism_found
        db.commit()
        
        logger.info(f"Группа {group.name}: проверено {len(posts)} постов, найдено плагиата: {plagiarism_found}")
    
    async def check_post_for_plagiarism(self, post: Dict, group: Group, db: Session) -> bool:
        """Проверка поста на плагиат"""
        post_text = post.get('text', '')
        post_images = self._extract_images(post)
        
        if not post_text and not post_images:
            return False
        
        # Ищем похожие посты в других группах
        similar_posts = await self.find_similar_posts(post_text, post_images, group.vk_group_id)
        
        for similar_post in similar_posts:
            # Проверяем схожесть
            text_similarity = 0.0
            image_similarity = 0.0
            
            if post_text and similar_post.get('text'):
                text_similarity = self.detector.detect_text_plagiarism(
                    post_text, similar_post.get('text', '')
                )
            
            if post_images and similar_post.get('images'):
                # Сравниваем изображения
                for img1 in post_images:
                    for img2 in similar_post.get('images', []):
                        similarity = self.detector.detect_image_plagiarism(img1, img2)
                        image_similarity = max(image_similarity, similarity)
            
            # Вычисляем общую схожесть
            overall_similarity = self.detector.calculate_overall_similarity(
                text_similarity, image_similarity
            )
            
            # Если схожесть превышает порог, создаем запись о плагиате
            if self.detector.is_plagiarism(overall_similarity):
                await self.create_plagiarism_record(
                    post, similar_post, group, overall_similarity,
                    text_similarity, image_similarity, db
                )
                return True
        
        return False
    
    def _extract_images(self, post: Dict) -> List[str]:
        """Извлечение URL изображений из поста"""
        images = []
        attachments = post.get('attachments', [])
        
        for attachment in attachments:
            if attachment.get('type') == 'photo':
                sizes = attachment['photo'].get('sizes', [])
                if sizes:
                    # Берем самое большое изображение
                    largest_size = max(sizes, key=lambda x: x.get('width', 0))
                    images.append(largest_size['url'])
        
        return images
    
    async def find_similar_posts(self, text: str, images: List[str], exclude_group_id: int) -> List[Dict]:
        """Поиск похожих постов"""
        # Здесь должна быть логика поиска похожих постов
        # Для MVP используем простой поиск по ключевым словам
        
        similar_posts = []
        
        # Получаем посты из популярных групп для сравнения
        popular_groups = [-1, -2, -3]  # ID популярных групп
        
        for group_id in popular_groups:
            if group_id == exclude_group_id:
                continue
            
            try:
                posts = await self.vk_api.get_group_posts(group_id, count=20)
                
                for post in posts:
                    post_text = post.get('text', '')
                    post_images = self._extract_images(post)
                    
                    # Простая проверка на схожесть
                    if text and post_text:
                        similarity = self.detector.detect_text_plagiarism(text, post_text)
                        if similarity > 0.3:  # Низкий порог для предварительной фильтрации
                            similar_posts.append({
                                'id': post['id'],
                                'text': post_text,
                                'images': post_images,
                                'group_id': group_id
                            })
            
            except Exception as e:
                logger.error(f"Ошибка поиска в группе {group_id}: {e}")
        
        return similar_posts
    
    async def create_plagiarism_record(self, original_post: Dict, plagiarized_post: Dict,
                                     group: Group, overall_similarity: float,
                                     text_similarity: float, image_similarity: float,
                                     db: Session):
        """Создание записи о найденном плагиате"""
        from models.plagiarism import Plagiarism
        
        plagiarism = Plagiarism(
            group_id=group.id,
            original_post_id=f"{original_post['owner_id']}_{original_post['id']}",
            original_group_id=original_post['owner_id'],
            original_text=original_post.get('text'),
            original_images=original_post.get('images', []),
            plagiarized_post_id=f"{plagiarized_post['group_id']}_{plagiarized_post['id']}",
            plagiarized_group_id=plagiarized_post['group_id'],
            plagiarized_text=plagiarized_post.get('text'),
            plagiarized_images=plagiarized_post.get('images', []),
            text_similarity=text_similarity,
            image_similarity=image_similarity,
            overall_similarity=overall_similarity
        )
        
        db.add(plagiarism)
        db.commit()
        
        # Отправляем уведомление пользователю
        await self.notification_service.send_plagiarism_notification(
            group.user_id, plagiarism, db
        ) 