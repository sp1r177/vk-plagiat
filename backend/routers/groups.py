from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User
from models.group import Group
from schemas.group import GroupCreate, GroupResponse, GroupUpdate
from services.vk_api_service import VKAPIService
from services.auth_service import get_current_user
from typing import List

router = APIRouter()


@router.post("/", response_model=GroupResponse)
async def add_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавление новой группы для мониторинга"""
    
    # Проверяем лимит групп для подписки
    user_groups_count = db.query(Group).filter(
        Group.user_id == current_user.id,
        Group.is_active == True
    ).count()
    
    if user_groups_count >= current_user.max_groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Достигнут лимит групп для вашей подписки ({current_user.max_groups})"
        )
    
    # Проверяем, не добавлена ли уже эта группа
    existing_group = db.query(Group).filter(
        Group.vk_group_id == group_data.vk_group_id,
        Group.user_id == current_user.id
    ).first()
    
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Эта группа уже добавлена для мониторинга"
        )
    
    # Получаем информацию о группе через VK API
    vk_api = VKAPIService()
    group_info = await vk_api.get_group_info(group_data.vk_group_id)
    
    if not group_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена или недоступна"
        )
    
    # Создаем новую группу
    group = Group(
        vk_group_id=group_data.vk_group_id,
        name=group_info["name"],
        screen_name=group_info.get("screen_name"),
        photo_url=group_info.get("photo_url"),
        description=group_info.get("description"),
        user_id=current_user.id,
        check_text=group_data.check_text,
        check_images=group_data.check_images,
        exclude_reposts=group_data.exclude_reposts
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    return group


@router.get("/", response_model=List[GroupResponse])
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка групп пользователя"""
    groups = db.query(Group).filter(
        Group.user_id == current_user.id,
        Group.is_active == True
    ).all()
    
    return groups


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о конкретной группе"""
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    
    return group


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление настроек группы"""
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    
    # Обновляем настройки
    if group_data.check_text is not None:
        group.check_text = group_data.check_text
    if group_data.check_images is not None:
        group.check_images = group_data.check_images
    if group_data.exclude_reposts is not None:
        group.exclude_reposts = group_data.exclude_reposts
    
    db.commit()
    db.refresh(group)
    
    return group


@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление группы из мониторинга"""
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    
    group.is_active = False
    db.commit()
    
    return {"message": "Группа успешно удалена из мониторинга"} 