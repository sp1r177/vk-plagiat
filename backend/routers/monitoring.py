from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User
from models.group import Group
from services.auth_service import get_current_user
from monitoring.scheduler import MonitoringScheduler
from monitoring.plagiarism_detector import PlagiarismDetector
from services.vk_api_service import VKAPIService
from typing import List, Dict
import asyncio

router = APIRouter()
monitoring_scheduler = MonitoringScheduler()
plagiarism_detector = PlagiarismDetector()
vk_api = VKAPIService()


@router.post("/start")
async def start_monitoring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Запуск мониторинга вручную"""
    
    # Получаем активные группы пользователя
    user_groups = db.query(Group).filter(
        Group.user_id == current_user.id,
        Group.is_active == True
    ).all()
    
    if not user_groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас нет активных групп для мониторинга"
        )
    
    # Запускаем мониторинг
    try:
        await monitoring_scheduler.run_monitoring()
        return {"message": f"Мониторинг запущен для {len(user_groups)} групп"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка запуска мониторинга: {str(e)}"
        )


@router.get("/status")
async def get_monitoring_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статуса мониторинга"""
    
    # Получаем группы пользователя
    user_groups = db.query(Group).filter(
        Group.user_id == current_user.id,
        Group.is_active == True
    ).all()
    
    status_info = []
    for group in user_groups:
        status_info.append({
            "group_id": group.id,
            "group_name": group.name,
            "vk_group_id": group.vk_group_id,
            "posts_checked": group.posts_checked,
            "plagiarism_found": group.plagiarism_found,
            "last_check": group.last_check.isoformat() if group.last_check else None,
            "check_text": group.check_text,
            "check_images": group.check_images,
            "exclude_reposts": group.exclude_reposts
        })
    
    return {
        "groups": status_info,
        "total_groups": len(status_info),
        "scheduler_running": monitoring_scheduler.scheduler.running
    }


@router.post("/check-post")
async def check_single_post(
    post_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверка отдельного поста на плагиат"""
    
    try:
        # Парсим URL поста
        # Формат: https://vk.com/wall-123456_789
        parts = post_url.split("wall")[-1].split("_")
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат URL поста"
            )
        
        owner_id = int(parts[0])
        post_id = int(parts[1])
        
        # Получаем информацию о посте
        post_info = await vk_api.get_post_info(f"{owner_id}_{post_id}")
        
        if not post_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пост не найден или недоступен"
            )
        
        # Проверяем на плагиат
        post_text = post_info.get('text', '')
        post_images = monitoring_scheduler._extract_images(post_info)
        
        # Ищем похожие посты
        similar_posts = await monitoring_scheduler.find_similar_posts(
            post_text, post_images, owner_id
        )
        
        results = []
        for similar_post in similar_posts:
            text_similarity = 0.0
            image_similarity = 0.0
            
            if post_text and similar_post.get('text'):
                text_similarity = plagiarism_detector.detect_text_plagiarism(
                    post_text, similar_post.get('text', '')
                )
            
            if post_images and similar_post.get('images'):
                for img1 in post_images:
                    for img2 in similar_post.get('images', []):
                        similarity = plagiarism_detector.detect_image_plagiarism(img1, img2)
                        image_similarity = max(image_similarity, similarity)
            
            overall_similarity = plagiarism_detector.calculate_overall_similarity(
                text_similarity, image_similarity
            )
            
            if plagiarism_detector.is_plagiarism(overall_similarity):
                results.append({
                    "similar_post_id": similar_post['id'],
                    "similar_group_id": similar_post['group_id'],
                    "text_similarity": text_similarity,
                    "image_similarity": image_similarity,
                    "overall_similarity": overall_similarity,
                    "is_plagiarism": True
                })
        
        return {
            "post_id": f"{owner_id}_{post_id}",
            "post_text": post_text[:200] + "..." if len(post_text) > 200 else post_text,
            "similar_posts_found": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка проверки поста: {str(e)}"
        )


@router.get("/statistics")
async def get_monitoring_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики мониторинга"""
    
    # Получаем группы пользователя
    user_groups = db.query(Group).filter(
        Group.user_id == current_user.id,
        Group.is_active == True
    ).all()
    
    total_posts_checked = sum(group.posts_checked for group in user_groups)
    total_plagiarism_found = sum(group.plagiarism_found for group in user_groups)
    
    # Статистика по дням (последние 7 дней)
    from datetime import datetime, timedelta
    from models.plagiarism import Plagiarism
    
    daily_stats = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        plagiarism_count = db.query(Plagiarism).join(Group).filter(
            Group.user_id == current_user.id,
            Plagiarism.created_at >= start_date,
            Plagiarism.created_at < end_date
        ).count()
        
        daily_stats.append({
            "date": start_date.date().isoformat(),
            "plagiarism_found": plagiarism_count
        })
    
    return {
        "total_groups": len(user_groups),
        "total_posts_checked": total_posts_checked,
        "total_plagiarism_found": total_plagiarism_found,
        "average_plagiarism_rate": total_plagiarism_found / max(total_posts_checked, 1) * 100,
        "daily_statistics": daily_stats
    } 