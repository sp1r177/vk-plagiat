from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from models.group import Group
from models.plagiarism import Plagiarism
from models.user import User
from services.vk_api_service import VKAPIService
from monitoring.plagiarism_detector import PlagiarismDetector
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Инициализация сервисов
vk_api = VKAPIService()
detector = PlagiarismDetector()


@router.get("/groups")
async def get_user_groups(user_id: int, db: Session = Depends(get_db)):
    """Получение групп пользователя для подключения"""
    try:
        # Получаем группы пользователя из VK API
        user_groups = await vk_api.get_user_groups(user_id)
        
        # Получаем уже подключенные группы из БД
        connected_groups = db.query(Group).filter(
            Group.user_id == user_id,
            Group.is_active == True
        ).all()
        
        connected_group_ids = {group.vk_group_id for group in connected_groups}
        
        # Формируем ответ
        groups = []
        for group in user_groups:
            groups.append({
                "vk_group_id": group["id"],
                "name": group["name"],
                "screen_name": group.get("screen_name"),
                "photo_url": group.get("photo_100"),
                "is_connected": group["id"] in connected_group_ids
            })
        
        return {"groups": groups}
        
    except Exception as e:
        logger.error(f"Ошибка получения групп пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения групп")


@router.post("/groups/connect")
async def connect_group(
    user_id: int,
    vk_group_id: int,
    db: Session = Depends(get_db)
):
    """Подключение группы к мониторингу"""
    try:
        # Проверяем, не подключена ли уже группа
        existing_group = db.query(Group).filter(
            Group.vk_group_id == vk_group_id,
            Group.user_id == user_id
        ).first()
        
        if existing_group:
            if existing_group.is_active:
                raise HTTPException(status_code=400, detail="Группа уже подключена")
            else:
                # Активируем существующую группу
                existing_group.is_active = True
                existing_group.connected_at = datetime.utcnow()
                db.commit()
                return {"message": "Группа активирована"}
        
        # Получаем информацию о группе из VK API
        group_info = await vk_api.get_group_info(vk_group_id)
        if not group_info:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        
        # Создаем новую группу
        new_group = Group(
            user_id=user_id,
            vk_group_id=vk_group_id,
            name=group_info["name"],
            screen_name=group_info.get("screen_name"),
            photo_url=group_info.get("photo_url"),
            is_active=True,
            connected_at=datetime.utcnow()
        )
        
        db.add(new_group)
        db.commit()
        
        return {"message": "Группа успешно подключена", "group": group_info}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка подключения группы: {e}")
        raise HTTPException(status_code=500, detail="Ошибка подключения группы")


@router.post("/groups/disconnect")
async def disconnect_group(
    user_id: int,
    vk_group_id: int,
    db: Session = Depends(get_db)
):
    """Отключение группы от мониторинга"""
    try:
        group = db.query(Group).filter(
            Group.vk_group_id == vk_group_id,
            Group.user_id == user_id
        ).first()
        
        if not group:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        
        group.is_active = False
        group.disconnected_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Группа отключена"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка отключения группы: {e}")
        raise HTTPException(status_code=500, detail="Ошибка отключения группы")


@router.get("/plagiarism")
async def get_plagiarism_cases(
    user_id: int,
    group_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получение списка обнаруженных случаев плагиата"""
    try:
        # Базовый запрос
        query = db.query(Plagiarism).join(Group).filter(
            Group.user_id == user_id
        )
        
        # Фильтр по группе
        if group_id:
            query = query.filter(Plagiarism.group_id == group_id)
        
        # Сортировка по дате (новые сначала)
        query = query.order_by(Plagiarism.created_at.desc())
        
        # Пагинация
        total = query.count()
        offset = (page - 1) * limit
        plagiarism_cases = query.offset(offset).limit(limit).all()
        
        # Формируем ответ
        cases = []
        for case in plagiarism_cases:
            cases.append({
                "id": case.id,
                "original_post_id": case.original_post_id,
                "plagiarized_post_id": case.plagiarized_post_id,
                "original_group_id": case.original_group_id,
                "plagiarized_group_id": case.plagiarized_group_id,
                "text_similarity": case.text_similarity,
                "image_similarity": case.image_similarity,
                "overall_similarity": case.overall_similarity,
                "created_at": case.created_at.isoformat(),
                "is_confirmed": case.is_confirmed,
                "is_false_positive": case.is_false_positive,
                "group_name": case.group.name if case.group else None
            })
        
        return {
            "cases": cases,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения случаев плагиата: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения данных")


@router.get("/plagiarism/{case_id}")
async def get_plagiarism_case(
    case_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получение детальной информации о случае плагиата"""
    try:
        case = db.query(Plagiarism).join(Group).filter(
            Plagiarism.id == case_id,
            Group.user_id == user_id
        ).first()
        
        if not case:
            raise HTTPException(status_code=404, detail="Случай плагиата не найден")
        
        # Получаем информацию о постах из VK API
        original_post = None
        plagiarized_post = None
        
        try:
            original_post = await vk_api.get_post_by_id(
                case.original_group_id, 
                case.original_post_id.split('_')[-1]
            )
        except Exception as e:
            logger.warning(f"Не удалось получить оригинальный пост: {e}")
        
        try:
            plagiarized_post = await vk_api.get_post_by_id(
                case.plagiarized_group_id,
                case.plagiarized_post_id.split('_')[-1]
            )
        except Exception as e:
            logger.warning(f"Не удалось получить плагиатный пост: {e}")
        
        return {
            "id": case.id,
            "original_post": original_post,
            "plagiarized_post": plagiarized_post,
            "text_similarity": case.text_similarity,
            "image_similarity": case.image_similarity,
            "overall_similarity": case.overall_similarity,
            "created_at": case.created_at.isoformat(),
            "is_confirmed": case.is_confirmed,
            "is_false_positive": case.is_false_positive,
            "group_name": case.group.name if case.group else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения случая плагиата: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения данных")


@router.post("/plagiarism/{case_id}/confirm")
async def confirm_plagiarism(
    case_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Подтверждение случая плагиата"""
    try:
        case = db.query(Plagiarism).join(Group).filter(
            Plagiarism.id == case_id,
            Group.user_id == user_id
        ).first()
        
        if not case:
            raise HTTPException(status_code=404, detail="Случай плагиата не найден")
        
        case.is_confirmed = True
        case.confirmed_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Плагиат подтвержден"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка подтверждения плагиата: {e}")
        raise HTTPException(status_code=500, detail="Ошибка подтверждения")


@router.post("/plagiarism/{case_id}/false-positive")
async def mark_false_positive(
    case_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отметка ложного срабатывания"""
    try:
        case = db.query(Plagiarism).join(Group).filter(
            Plagiarism.id == case_id,
            Group.user_id == user_id
        ).first()
        
        if not case:
            raise HTTPException(status_code=404, detail="Случай плагиата не найден")
        
        case.is_false_positive = True
        case.false_positive_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Отмечено как ложное срабатывание"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка отметки ложного срабатывания: {e}")
        raise HTTPException(status_code=500, detail="Ошибка отметки")


@router.get("/statistics")
async def get_statistics(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получение статистики мониторинга"""
    try:
        # Статистика групп
        total_groups = db.query(Group).filter(
            Group.user_id == user_id
        ).count()
        
        active_groups = db.query(Group).filter(
            Group.user_id == user_id,
            Group.is_active == True
        ).count()
        
        # Статистика плагиата
        total_plagiarism = db.query(Plagiarism).join(Group).filter(
            Group.user_id == user_id
        ).count()
        
        confirmed_plagiarism = db.query(Plagiarism).join(Group).filter(
            Group.user_id == user_id,
            Plagiarism.is_confirmed == True
        ).count()
        
        false_positives = db.query(Plagiarism).join(Group).filter(
            Group.user_id == user_id,
            Plagiarism.is_false_positive == True
        ).count()
        
        # Статистика за последние 7 дней
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_plagiarism = db.query(Plagiarism).join(Group).filter(
            Group.user_id == user_id,
            Plagiarism.created_at >= week_ago
        ).count()
        
        return {
            "groups": {
                "total": total_groups,
                "active": active_groups
            },
            "plagiarism": {
                "total": total_plagiarism,
                "confirmed": confirmed_plagiarism,
                "false_positives": false_positives,
                "recent_week": recent_plagiarism
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики") 