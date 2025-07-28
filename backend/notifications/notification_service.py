from sqlalchemy.orm import Session
from models.user import User
from models.plagiarism import Plagiarism
from services.vk_api_service import VKAPIService
from datetime import datetime, date
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.vk_api = VKAPIService()
        self.max_notifications_per_day = settings.MAX_NOTIFICATIONS_PER_DAY
    
    async def send_plagiarism_notification(self, user_id: int, plagiarism: Plagiarism, db: Session):
        """Отправка уведомления о найденном плагиате"""
        try:
            # Получаем пользователя
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"Пользователь {user_id} не найден")
                return False
            
            # Проверяем лимит уведомлений
            if not self._can_send_notification(user, db):
                logger.info(f"Достигнут лимит уведомлений для пользователя {user_id}")
                return False
            
            # Формируем сообщение
            message = self._format_plagiarism_message(plagiarism)
            
            # Отправляем сообщение
            success = await self.vk_api.send_message(user.vk_id, message)
            
            if success:
                # Обновляем статистику
                user.notifications_sent_today += 1
                user.last_notification_date = datetime.utcnow()
                user.total_plagiarism_found += 1
                
                # Отмечаем уведомление как отправленное
                plagiarism.notification_sent = True
                plagiarism.notification_sent_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"Уведомление отправлено пользователю {user_id}")
                return True
            else:
                logger.error(f"Ошибка отправки уведомления пользователю {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            return False
    
    def _can_send_notification(self, user: User, db: Session) -> bool:
        """Проверка возможности отправки уведомления"""
        # Сбрасываем счетчик если новый день
        if user.last_notification_date:
            last_date = user.last_notification_date.date()
            current_date = date.today()
            
            if last_date < current_date:
                user.notifications_sent_today = 0
                db.commit()
        
        return user.notifications_sent_today < self.max_notifications_per_day
    
    def _format_plagiarism_message(self, plagiarism: Plagiarism) -> str:
        """Форматирование сообщения о плагиате"""
        similarity_percent = int(plagiarism.overall_similarity * 100)
        
        message = f"""🔍 Найден плагиат!

📊 Схожесть: {similarity_percent}%

📝 Оригинальный пост:
https://vk.com/wall{plagiarism.original_post_id}

🔄 Пост с плагиатом:
https://vk.com/wall{plagiarism.plagiarized_post_id}

📈 Детали анализа:
• Текст: {int(plagiarism.text_similarity * 100) if plagiarism.text_similarity else 0}%
• Изображения: {int(plagiarism.image_similarity * 100) if plagiarism.image_similarity else 0}%

💡 Для получения подробной статистики откройте приложение."""
        
        return message
    
    async def send_daily_summary(self, user_id: int, db: Session):
        """Отправка ежедневного отчета"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Получаем статистику за день
            today = date.today()
            plagiarism_today = db.query(Plagiarism).filter(
                Plagiarism.group_id.in_(
                    db.query(Group.id).filter(Group.user_id == user_id)
                ),
                Plagiarism.created_at >= today
            ).count()
            
            if plagiarism_today > 0:
                message = f"""📊 Ежедневный отчет

🔍 Найдено случаев плагиата: {plagiarism_today}
📈 Всего за все время: {user.total_plagiarism_found}
📱 Уведомлений отправлено: {user.notifications_sent_today}

💡 Откройте приложение для подробной статистики."""
                
                await self.vk_api.send_message(user.vk_id, message)
                return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки ежедневного отчета: {e}")
        
        return False
    
    async def send_subscription_expiry_warning(self, user_id: int, days_left: int, db: Session):
        """Предупреждение об истечении подписки"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            message = f"""⚠️ Внимание!

Ваша подписка истекает через {days_left} дней.

💳 Для продления подписки откройте приложение и перейдите в раздел "Тарифы".

🔗 Или перейдите по ссылке: vk.com/app123456#tariffs"""
            
            await self.vk_api.send_message(user.vk_id, message)
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки предупреждения о подписке: {e}")
            return False
    
    async def send_welcome_message(self, user_id: int, db: Session):
        """Приветственное сообщение для нового пользователя"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            message = """🎉 Добро пожаловать в Плагиат-Детектор!

🔍 Мы будем автоматически мониторить ваши группы и уведомлять о найденном плагиате.

📱 Для начала работы:
1. Добавьте группы для мониторинга
2. Настройте параметры проверки
3. Получайте уведомления о плагиате

💡 Откройте приложение для настройки: vk.com/app123456"""
            
            await self.vk_api.send_message(user.vk_id, message)
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки приветственного сообщения: {e}")
            return False 