import re
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import imagehash
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from config.settings import settings


class PlagiarismDetector:
    def __init__(self):
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
    
    def detect_text_plagiarism(self, text1: str, text2: str) -> float:
        """Детекция плагиата в тексте"""
        if not text1 or not text2:
            return 0.0
        
        # Очистка текста
        text1_clean = self._clean_text(text1)
        text2_clean = self._clean_text(text2)
        
        if not text1_clean or not text2_clean:
            return 0.0
        
        # Векторизация текстов
        try:
            tfidf_matrix = self.text_vectorizer.fit_transform([text1_clean, text2_clean])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception:
            return 0.0
    
    def detect_image_plagiarism(self, image_url1: str, image_url2: str) -> float:
        """Детекция плагиата в изображениях"""
        try:
            # Загрузка изображений
            img1 = self._download_image(image_url1)
            img2 = self._download_image(image_url2)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # Вычисление хешей изображений
            hash1 = imagehash.average_hash(img1)
            hash2 = imagehash.average_hash(img2)
            
            # Вычисление расстояния между хешами
            max_distance = 64  # Максимальное расстояние для хеша 8x8
            distance = hash1 - hash2
            similarity = 1 - (distance / max_distance)
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            print(f"Ошибка при анализе изображений: {e}")
            return 0.0
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов"""
        # Удаление URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Удаление хештегов
        text = re.sub(r'#\w+', '', text)
        
        # Удаление упоминаний
        text = re.sub(r'@\w+', '', text)
        
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Загрузка изображения по URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return img
        except Exception as e:
            print(f"Ошибка загрузки изображения {url}: {e}")
            return None
    
    def is_repost(self, post_data: Dict) -> bool:
        """Проверка, является ли пост репостом"""
        # Проверка copy_history
        if 'copy_history' in post_data and post_data['copy_history']:
            return True
        
        # Проверка текста на ключевые слова
        text = post_data.get('text', '').lower()
        repost_keywords = ['репост', 'repost', 'поделился', 'поделилась', 'поделились']
        
        for keyword in repost_keywords:
            if keyword in text:
                return True
        
        # Проверка attachments на wall
        attachments = post_data.get('attachments', [])
        for attachment in attachments:
            if attachment.get('type') == 'wall':
                return True
        
        return False
    
    def calculate_overall_similarity(self, text_similarity: float, image_similarity: float) -> float:
        """Вычисление общей схожести"""
        # Взвешенная формула: 70% текст + 30% изображения
        overall = (text_similarity * 0.7) + (image_similarity * 0.3)
        return min(1.0, max(0.0, overall))
    
    def is_plagiarism(self, similarity: float) -> bool:
        """Проверка, превышает ли схожесть порог плагиата"""
        return similarity >= self.similarity_threshold 