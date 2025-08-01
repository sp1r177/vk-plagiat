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
import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.vk_api = VKAPIService()
        self.detector = PlagiarismDetector()
        self.notification_service = NotificationService()
    
    def start(self):
        """Запуск планировщика мониторинга"""
        try:
            # Настройка планировщика для MVP - каждые 3 часа
            self.scheduler.add_job(
                self.run_monitoring,
                CronTrigger(hour=f"*/{settings.MONITORING_INTERVAL_HOURS}"),  # Каждые 3 часа
                id="plagiarism_monitoring",
                name="Мониторинг плагиата",
                replace_existing=True
            )
            
            # Дополнительно запускаем мониторинг при старте
            self.scheduler.add_job(
                self.run_monitoring,
                'date',
                id="initial_monitoring",
                name="Начальный мониторинг",
                run_date=datetime.now() + timedelta(minutes=1)
            )
            
            self.scheduler.start()
            logger.info("Планировщик мониторинга запущен")
            
        except Exception as e:
            logger.error(f"Ошибка запуска планировщика: {e}")
    
    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик мониторинга остановлен")
    
    async def run_monitoring(self):
        """Запуск мониторинга всех активных групп"""
        logger.info("Запуск мониторинга плагиата")
        
        db = SessionLocal()
        try:
            # Получаем все активные группы для мониторинга
            groups = db.query(Group).filter(
                Group.is_active == True
            ).limit(settings.MAX_GROUPS_TO_MONITOR).all()
            
            logger.info(f"Найдено {len(groups)} групп для мониторинга")
            
            # Запускаем мониторинг для каждой группы
            for group in groups:
                try:
                    await self.monitor_group(group, db)
                    # Небольшая задержка между группами
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Ошибка мониторинга группы {group.vk_group_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка мониторинга: {e}")
        finally:
            db.close()
    
    async def monitor_group(self, group: Group, db: Session):
        """Мониторинг конкретной группы"""
        try:
            # Получаем посты группы
            posts = await self.vk_api.get_group_posts(
                group.vk_group_id, 
                count=settings.MAX_POSTS_PER_GROUP
            )
            
            logger.info(f"Получено {len(posts)} постов для группы {group.vk_group_id}")
            
            # Проверяем каждый пост на плагиат
            for post in posts:
                try:
                    await self.check_post_for_plagiarism(post, group, db)
                except Exception as e:
                    logger.error(f"Ошибка проверки поста {post.get('id')}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка мониторинга группы {group.vk_group_id}: {e}")
    
    async def check_post_for_plagiarism(self, post: Dict, group: Group, db: Session) -> bool:
        """Проверка поста на плагиат по правилам MVP"""
        
        # Проверяем, не является ли пост репостом
        if self.detector.is_repost(post):
            logger.debug(f"Пост {post.get('id')} является репостом - пропускаем")
            return False
        
        # Получаем текст и изображения поста
        post_text = post.get('text', '')
        post_images = self._extract_images(post)
        
        # Ищем похожие посты в других группах
        similar_posts = await self.find_similar_posts(
            post_text, post_images, group.vk_group_id
        )
        
        plagiarism_found = False
        
        for similar_post in similar_posts:
            try:
                # Проверяем плагиат по правилам MVP
                analysis_result = self.detector.detect_plagiarism(similar_post, post)
                
                if analysis_result['is_plagiarism']:
                    # Создаем запись о плагиате
                    await self.create_plagiarism_record_improved(
                        similar_post, post, group, analysis_result, db
                    )
                    plagiarism_found = True
                    logger.info(f"Обнаружен плагиат: {analysis_result['recommendation']}")
                
            except Exception as e:
                logger.error(f"Ошибка анализа плагиата: {e}")
                continue
        
        return plagiarism_found
    
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
        """Поиск похожих постов в реальных группах"""
        similar_posts = []
        
        # Получаем список групп для мониторинга из базы данных
        db = SessionLocal()
        try:
            monitored_groups = db.query(Group).filter(
                Group.is_active == True,
                Group.vk_group_id != exclude_group_id
            ).limit(10).all()  # Ограничиваем количество групп для производительности
            
            for group in monitored_groups:
                try:
                    # Получаем посты группы
                    posts = await self.vk_api.get_group_posts(group.vk_group_id, count=10)
                    
                    for post in posts:
                        post_text = post.get('text', '')
                        post_images = self._extract_images(post)
                        
                        # Проверяем схожесть текста
                        if text and post_text and len(text) > 20 and len(post_text) > 20:
                            # Используем новую логику детекции
                            analysis_result = self.detector.detect_plagiarism(
                                {'text': text, 'attachments': [{'type': 'photo', 'photo': {'sizes': [{'url': img}]}} for img in images]},
                                {'text': post_text, 'attachments': [{'type': 'photo', 'photo': {'sizes': [{'url': img}]}} for img in post_images]}
                            )
                            
                            # Добавляем пост если есть схожесть
                            if analysis_result['text_similarity'] > 0.3 or analysis_result['image_similarity'] > 0.3:
                                similar_posts.append({
                                    'id': post['id'],
                                    'owner_id': post['owner_id'],
                                    'text': post_text,
                                    'images': post_images,
                                    'attachments': post.get('attachments', [])
                                })
                
                except Exception as e:
                    logger.error(f"Ошибка поиска в группе {group.vk_group_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка получения групп для поиска: {e}")
        finally:
            db.close()
        
        return similar_posts
    
    async def create_plagiarism_record(self, original_post: Dict, plagiarized_post: Dict,
                                     group: Group, overall_similarity: float,
                                     text_similarity: float, image_similarity: float,
                                     db: Session):
        """Создание записи о найденном плагиате"""
        from models.plagiarism import Plagiarism
        
        # Создаем запись о плагиате
        plagiarism = Plagiarism(
            group_id=group.id,
            original_post_id=f"{original_post['owner_id']}_{original_post['id']}",
            original_group_id=original_post['owner_id'],
            original_text=original_post.get('text', ''),
            original_images=original_post.get('images', []),
            plagiarized_post_id=f"{plagiarized_post['owner_id']}_{plagiarized_post['id']}",
            plagiarized_group_id=plagiarized_post['owner_id'],
            plagiarized_text=plagiarized_post.get('text', ''),
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
    
    async def create_plagiarism_record_improved(self, original_post: Dict, plagiarized_post: Dict,
                                              group: Group, analysis_result: Dict, db: Session):
        """Создание записи о найденном плагиате с улучшенной логикой"""
        from models.plagiarism import Plagiarism
        
        # Создаем запись о плагиате
        plagiarism = Plagiarism(
            group_id=group.id,
            original_post_id=f"{original_post['owner_id']}_{original_post['id']}",
            original_group_id=original_post['owner_id'],
            original_text=original_post.get('text', ''),
            original_images=self._extract_images(original_post),
            plagiarized_post_id=f"{plagiarized_post['owner_id']}_{plagiarized_post['id']}",
            plagiarized_group_id=plagiarized_post['owner_id'],
            plagiarized_text=plagiarized_post.get('text', ''),
            plagiarized_images=self._extract_images(plagiarized_post),
            text_similarity=analysis_result['text_similarity'],
            image_similarity=analysis_result['image_similarity'],
            overall_similarity=analysis_result['overall_similarity']
        )
        
        db.add(plagiarism)
        db.commit()
        
        # Отправляем уведомление пользователю только если уверенность высокая
        if analysis_result['confidence'] >= settings.CONFIDENCE_THRESHOLD:
            await self.notification_service.send_plagiarism_notification(
                group.user_id, plagiarism, db
            )
            logger.info(f"Уведомление отправлено для плагиата с уверенностью {analysis_result['confidence']}")
        else:
            logger.info(f"Уведомление не отправлено из-за низкой уверенности: {analysis_result['confidence']}") 