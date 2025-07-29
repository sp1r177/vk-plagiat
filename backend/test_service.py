#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы сервиса плагиат-детектора
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vk_api_service import VKAPIService
from monitoring.plagiarism_detector import PlagiarismDetector
from database.database import SessionLocal
from models.group import Group
from models.user import User
from models.plagiarism import Plagiarism

# Загружаем переменные окружения
load_dotenv()


async def test_vk_api():
    """Тест VK API"""
    print("🔍 Тестирование VK API...")
    
    vk_api = VKAPIService()
    
    # Проверяем токен
    if not vk_api.access_token:
        print("❌ VK_ACCESS_TOKEN не настроен")
        return False
    
    try:
        # Тестируем получение информации о группе
        group_info = await vk_api.get_group_info(1)  # Тестовая группа
        if group_info:
            print(f"✅ VK API работает. Получена информация о группе: {group_info['name']}")
            return True
        else:
            print("❌ Не удалось получить информацию о группе")
            return False
    except Exception as e:
        print(f"❌ Ошибка VK API: {e}")
        return False


async def test_plagiarism_detector():
    """Тест детектора плагиата по правилам MVP"""
    print("\n🔍 Тестирование детектора плагиата (MVP)...")
    
    detector = PlagiarismDetector()
    
    # Тестовые случаи для MVP
    test_cases = [
        {
            "name": "Одинаковые тексты (плагиат)",
            "original": "Это оригинальный текст с уникальным содержанием и интересными фактами.",
            "target": "Это оригинальный текст с уникальным содержанием и интересными фактами.",
            "expected_plagiarism": True
        },
        {
            "name": "Разные тексты (не плагиат)",
            "original": "Это оригинальный текст с уникальным содержанием.",
            "target": "Совершенно другой текст с другим содержанием.",
            "expected_plagiarism": False
        },
        {
            "name": "70% схожесть (плагиат по MVP)",
            "original": "Интересная статья о технологиях и инновациях в современном мире.",
            "target": "Интересная статья о технологиях и инновациях в мире.",
            "expected_plagiarism": True
        },
        {
            "name": "Короткие тексты (не плагиат)",
            "original": "Короткий текст.",
            "target": "Другой короткий текст.",
            "expected_plagiarism": False
        }
    ]
    
    try:
        for i, test_case in enumerate(test_cases, 1):
            result = detector.detect_plagiarism(
                {'text': test_case['original'], 'attachments': [], 'date': 1000000000},
                {'text': test_case['target'], 'attachments': [], 'date': 1000000001}
            )
            
            status = "✅" if result['is_plagiarism'] == test_case['expected_plagiarism'] else "❌"
            print(f"   {status} Тест {i}: {test_case['name']}")
            print(f"      - Схожесть: {result['text_similarity']:.2f}")
            print(f"      - Результат: {result['is_plagiarism']} (ожидалось: {test_case['expected_plagiarism']})")
            print(f"      - Причина: {result['text_reason']}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка детектора плагиата: {e}")
        return False


async def test_database():
    """Тест базы данных"""
    print("\n🔍 Тестирование базы данных...")
    
    try:
        db = SessionLocal()
        
        # Проверяем подключение
        result = db.execute("SELECT 1").fetchone()
        if result:
            print("✅ База данных подключена")
            
            # Проверяем таблицы
            tables = ['users', 'groups', 'plagiarism_cases']
            for table in tables:
                try:
                    db.execute(f"SELECT COUNT(*) FROM {table}")
                    print(f"   ✅ Таблица {table} существует")
                except Exception as e:
                    print(f"   ❌ Таблица {table} не существует: {e}")
            
            db.close()
            return True
        else:
            print("❌ Не удалось подключиться к базе данных")
            return False
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False


async def test_settings():
    """Тест настроек"""
    print("\n🔍 Тестирование настроек...")
    
    from config.settings import settings
    
    required_settings = [
        'DATABASE_URL',
        'VK_ACCESS_TOKEN',
        'SECRET_KEY'
    ]
    
    missing_settings = []
    for setting in required_settings:
        value = getattr(settings, setting, None)
        if not value or value == "":
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"❌ Отсутствуют настройки: {', '.join(missing_settings)}")
        return False
    else:
        print("✅ Все необходимые настройки присутствуют")
        return True


async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования сервиса плагиат-детектора\n")
    
    tests = [
        test_settings,
        test_database,
        test_vk_api,
        test_plagiarism_detector
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Ошибка в тесте: {e}")
            results.append(False)
    
    print(f"\n📊 Результаты тестирования:")
    print(f"   - Настройки: {'✅' if results[0] else '❌'}")
    print(f"   - База данных: {'✅' if results[1] else '❌'}")
    print(f"   - VK API: {'✅' if results[2] else '❌'}")
    print(f"   - Детектор плагиата: {'✅' if results[3] else '❌'}")
    
    if all(results):
        print("\n🎉 Все тесты пройдены! Сервис готов к работе.")
    else:
        print("\n⚠️  Некоторые тесты не пройдены. Проверьте настройки.")


if __name__ == "__main__":
    asyncio.run(main()) 