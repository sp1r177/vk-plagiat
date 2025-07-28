import hashlib
import hmac
import json
from typing import Dict, Optional
from config.settings import settings


class VKPayService:
    def __init__(self):
        self.merchant_id = settings.VK_PAY_MERCHANT_ID
        self.secret_key = settings.VK_PAY_SECRET_KEY
    
    def create_payment(self, user_id: int, amount: int, description: str, 
                      subscription_type: str) -> Dict:
        """Создание платежа через VK Pay"""
        try:
            payment_data = {
                "merchant_id": self.merchant_id,
                "amount": amount,
                "currency": "RUB",
                "description": description,
                "merchant_data": json.dumps({
                    "user_id": user_id,
                    "subscription_type": subscription_type
                }),
                "merchant_sign": self._generate_signature({
                    "merchant_id": self.merchant_id,
                    "amount": amount,
                    "currency": "RUB",
                    "description": description
                })
            }
            
            return {
                "success": True,
                "payment_data": payment_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_payment(self, payment_data: Dict) -> bool:
        """Проверка подписи платежа"""
        try:
            received_sign = payment_data.get("merchant_sign")
            if not received_sign:
                return False
            
            # Убираем подпись из данных для проверки
            data_to_verify = {k: v for k, v in payment_data.items() if k != "merchant_sign"}
            
            expected_sign = self._generate_signature(data_to_verify)
            
            return received_sign == expected_sign
            
        except Exception:
            return False
    
    def _generate_signature(self, data: Dict) -> str:
        """Генерация подписи для VK Pay"""
        # Сортируем ключи для стабильной подписи
        sorted_data = dict(sorted(data.items()))
        
        # Создаем строку для подписи
        sign_string = "&".join([f"{k}={v}" for k, v in sorted_data.items()])
        
        # Генерируем HMAC-SHA256 подпись
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def process_payment_success(self, payment_data: Dict) -> Dict:
        """Обработка успешного платежа"""
        try:
            merchant_data = json.loads(payment_data.get("merchant_data", "{}"))
            user_id = merchant_data.get("user_id")
            subscription_type = merchant_data.get("subscription_type")
            amount = payment_data.get("amount", 0)
            
            return {
                "success": True,
                "user_id": user_id,
                "subscription_type": subscription_type,
                "amount": amount
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_subscription_price(self, subscription_type: str) -> int:
        """Получение цены подписки"""
        pricing = settings.PRICING.get(subscription_type, {})
        return pricing.get("price", 0)
    
    def get_subscription_details(self, subscription_type: str) -> Dict:
        """Получение деталей подписки"""
        return settings.PRICING.get(subscription_type, {}) 