from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User
from models.plagiarism import Plagiarism
from services.auth_service import get_current_user
from notifications.notification_service import NotificationService
from typing import List
from datetime import datetime, timedelta
from models.group import Group
import settings

router = APIRouter()
notification_service = NotificationService()


@router.get("/history")
async def get_notification_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Получение истории уведомлений о плагиате"""
    
    # Получаем случаи плагиата для групп пользователя
    plagiarism_cases = db.query(Plagiarism).join(Group).filter(
        Group.user_id == current_user.id,
        Plagiarism.notification_sent == True
    ).order_by(Plagiarism.created_at.desc()).offset(offset).limit(limit).all()
    
    history = []
    for case in plagiarism_cases:
        history.append({
            "id": case.id,
            "created_at": case.created_at.isoformat(),
            "overall_similarity": case.overall_similarity,
            "text_similarity": case.text_similarity,
            "image_similarity": case.image_similarity,
            "original_post_url": f"https://vk.com/wall{case.original_post_id}",
            "plagiarized_post_url": f"https://vk.com/wall{case.plagiarized_post_id}",
            "group_name": case.group.name,
            "notification_sent_at": case.notification_sent_at.isoformat() if case.notification_sent_at else None
        })
    
    return {
        "history": history,
        "total": len(history),
        "limit": limit,
        "offset": offset
    }


@router.get("/statistics")
async def get_notification_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики уведомлений"""
    
    # Статистика за сегодня
    today = datetime.utcnow().date()
    today_cases = db.query(Plagiarism).join(Group).filter(
        Group.user_id == current_user.id,
        Plagiarism.created_at >= today
    ).count()
    
    # Статистика за неделю
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_cases = db.query(Plagiarism).join(Group).filter(
        Group.user_id == current_user.id,
        Plagiarism.created_at >= week_ago
    ).count()
    
    # Статистика за месяц
    month_ago = datetime.utcnow() - timedelta(days=30)
    month_cases = db.query(Plagiarism).join(Group).filter(
        Group.user_id == current_user.id,
        Plagiarism.created_at >= month_ago
    ).count()
    
    return {
        "today": today_cases,
        "week": week_cases,
        "month": month_cases,
        "total": current_user.total_plagiarism_found,
        "notifications_sent_today": current_user.notifications_sent_today,
        "max_notifications_per_day": settings.MAX_NOTIFICATIONS_PER_DAY
    }


@router.post("/test")
async def send_test_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка тестового уведомления"""
    
    # Проверяем лимит уведомлений
    if current_user.notifications_sent_today >= settings.MAX_NOTIFICATIONS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Достигнут лимит уведомлений на сегодня"
        )
    
    # Отправляем тестовое уведомление
    success = await notification_service.send_test_notification(current_user.vk_id)
    
    if success:
        current_user.notifications_sent_today += 1
        current_user.last_notification_date = datetime.utcnow()
        db.commit()
        
        return {"message": "Тестовое уведомление отправлено"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка отправки тестового уведомления"
        )


@router.put("/settings")
async def update_notification_settings(
    notifications_enabled: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление настроек уведомлений"""
    
    current_user.notifications_enabled = notifications_enabled
    db.commit()
    
    return {
        "message": "Настройки уведомлений обновлены",
        "notifications_enabled": notifications_enabled
    }


@router.get("/settings")
async def get_notification_settings(
    current_user: User = Depends(get_current_user)
):
    """Получение настроек уведомлений"""
    
    return {
        "notifications_enabled": current_user.notifications_enabled,
        "notifications_sent_today": current_user.notifications_sent_today,
        "max_notifications_per_day": settings.MAX_NOTIFICATIONS_PER_DAY
    } 