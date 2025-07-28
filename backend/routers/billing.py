from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User, SubscriptionType
from services.auth_service import get_current_user
from billing.vk_pay_service import VKPayService
from datetime import datetime, timedelta
from typing import List, Dict

router = APIRouter()
vk_pay_service = VKPayService()


@router.get("/subscriptions")
async def get_subscriptions():
    """Получение списка доступных подписок"""
    subscriptions = []
    
    for sub_type, details in settings.PRICING.items():
        subscriptions.append({
            "type": sub_type,
            "name": self._get_subscription_name(sub_type),
            "groups": details["groups"],
            "days": details["days"],
            "price": details["price"] / 100,  # Конвертируем из копеек в рубли
            "price_kop": details["price"]
        })
    
    return {"subscriptions": subscriptions}


@router.post("/create-payment")
async def create_payment(
    subscription_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание платежа для подписки"""
    
    # Проверяем существование подписки
    if subscription_type not in settings.PRICING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный тип подписки"
        )
    
    # Получаем детали подписки
    subscription_details = vk_pay_service.get_subscription_details(subscription_type)
    price = subscription_details["price"]
    
    # Создаем платеж
    payment_result = vk_pay_service.create_payment(
        user_id=current_user.id,
        amount=price,
        description=f"Подписка {self._get_subscription_name(subscription_type)}",
        subscription_type=subscription_type
    )
    
    if not payment_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка создания платежа"
        )
    
    return payment_result


@router.post("/process-payment")
async def process_payment(
    payment_data: Dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обработка успешного платежа"""
    
    # Проверяем подпись платежа
    if not vk_pay_service.verify_payment(payment_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверная подпись платежа"
        )
    
    # Обрабатываем платеж
    result = vk_pay_service.process_payment_success(payment_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка обработки платежа"
        )
    
    # Обновляем подписку пользователя
    subscription_type = SubscriptionType(result["subscription_type"])
    subscription_details = settings.PRICING[result["subscription_type"]]
    
    current_user.subscription_type = subscription_type
    current_user.max_groups = subscription_details["groups"]
    
    # Устанавливаем срок действия подписки
    if subscription_type != SubscriptionType.FREE:
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=subscription_details["days"])
    else:
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=1)
    
    db.commit()
    
    return {
        "success": True,
        "message": "Подписка успешно активирована",
        "subscription_type": subscription_type.value,
        "expires_at": current_user.subscription_expires.isoformat()
    }


@router.get("/my-subscription")
async def get_my_subscription(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущей подписке пользователя"""
    
    subscription_details = settings.PRICING.get(current_user.subscription_type.value, {})
    
    return {
        "subscription_type": current_user.subscription_type.value,
        "subscription_name": self._get_subscription_name(current_user.subscription_type.value),
        "max_groups": current_user.max_groups,
        "expires_at": current_user.subscription_expires.isoformat() if current_user.subscription_expires else None,
        "is_active": self._is_subscription_active(current_user),
        "days_left": self._get_days_left(current_user) if current_user.subscription_expires else None
    }


def _get_subscription_name(self, subscription_type: str) -> str:
    """Получение названия подписки"""
    names = {
        "free": "Бесплатно",
        "basic": "Базовый",
        "standard": "Стандарт",
        "premium": "Премиум"
    }
    return names.get(subscription_type, subscription_type)


def _is_subscription_active(self, user: User) -> bool:
    """Проверка активности подписки"""
    if user.subscription_type == SubscriptionType.FREE:
        return True
    
    if not user.subscription_expires:
        return False
    
    return user.subscription_expires > datetime.utcnow()


def _get_days_left(self, user: User) -> int:
    """Получение количества дней до истечения подписки"""
    if not user.subscription_expires:
        return 0
    
    delta = user.subscription_expires - datetime.utcnow()
    return max(0, delta.days) 