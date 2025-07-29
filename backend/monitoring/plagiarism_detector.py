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
from datetime import datetime, timedelta
from difflib import SequenceMatcher


class PlagiarismDetector:
    def __init__(self):
        # Настройки для MVP
        self.text_similarity_threshold = 0.7  # 70% как в требованиях
        self.image_hamming_threshold = 10    # Расстояние Хэмминга ≤10
        self.min_text_length = 20            # Минимальная длина для анализа
        
        # Векторизатор для семантического анализа
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def detect_plagiarism(self, original_post: Dict, target_post: Dict) -> Dict:
        """Основной метод детекции плагиата по правилам MVP"""
        
        # Проверяем, не является ли пост репостом
        if self.is_repost(target_post):
            return self._create_no_plagiarism_result("Пост является репостом")
        
        # Проверяем даты публикации
        if not self._is_posted_after_original(original_post, target_post):
            return self._create_no_plagiarism_result("Пост опубликован раньше оригинала")
        
        # Проверяем наличие ссылки на оригинал
        if self._has_original_attribution(target_post, original_post):
            return self._create_no_plagiarism_result("Пост содержит ссылку на оригинал")
        
        # Анализируем текст
        text_analysis = self._analyze_text_plagiarism_mvp(
            original_post.get('text', ''),
            target_post.get('text', '')
        )
        
        # Анализируем изображения
        image_analysis = self._analyze_image_plagiarism_mvp(
            original_post.get('attachments', []),
            target_post.get('attachments', [])
        )
        
        # Финальная оценка по правилам MVP
        result = self._final_evaluation_mvp(text_analysis, image_analysis, original_post, target_post)
        
        return result
    
    def _analyze_text_plagiarism_mvp(self, original_text: str, target_text: str) -> Dict:
        """Анализ текстового плагиата по правилам MVP"""
        
        # Очистка текстов
        original_clean = self._clean_text(original_text)
        target_clean = self._clean_text(target_text)
        
        # Проверка минимальной длины
        if len(original_clean) < self.min_text_length or len(target_clean) < self.min_text_length:
            return {
                'similarity': 0.0,
                'is_plagiarism': False,
                'reason': 'Недостаточная длина текста для анализа'
            }
        
        # 1. Символьное сравнение (по символам)
        char_similarity = self._calculate_char_similarity(original_clean, target_clean)
        
        # 2. Семантическое сравнение (по смыслу)
        semantic_similarity = self._calculate_semantic_similarity(original_clean, target_clean)
        
        # 3. Fuzzy match (Levenshtein)
        fuzzy_similarity = self._calculate_fuzzy_similarity(original_clean, target_clean)
        
        # Выбираем максимальную схожесть
        text_similarity = max(char_similarity, semantic_similarity, fuzzy_similarity)
        
        return {
            'similarity': text_similarity,
            'char_similarity': char_similarity,
            'semantic_similarity': semantic_similarity,
            'fuzzy_similarity': fuzzy_similarity,
            'is_plagiarism': text_similarity >= self.text_similarity_threshold,
            'reason': self._get_text_plagiarism_reason(text_similarity)
        }
    
    def _analyze_image_plagiarism_mvp(self, original_attachments: List, target_attachments: List) -> Dict:
        """Анализ плагиата изображений по правилам MVP"""
        
        original_images = self._extract_images(original_attachments)
        target_images = self._extract_images(target_attachments)
        
        if not original_images or not target_images:
            return {
                'similarity': 0.0,
                'is_plagiarism': False,
                'reason': 'Нет изображений для сравнения'
            }
        
        # Сравниваем каждое изображение
        max_similarity = 0.0
        best_match = None
        plagiarism_found = False
        
        for orig_img in original_images:
            for target_img in target_images:
                # Вычисляем perceptual hash
                similarity, hamming_distance = self._compare_images_phash(orig_img, target_img)
                
                if hamming_distance <= self.image_hamming_threshold:
                    plagiarism_found = True
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_match = (orig_img, target_img, hamming_distance)
        
        return {
            'similarity': max_similarity,
            'is_plagiarism': plagiarism_found,
            'reason': self._get_image_plagiarism_reason(max_similarity, best_match[2] if best_match else None),
            'best_match': best_match
        }
    
    def _final_evaluation_mvp(self, text_analysis: Dict, image_analysis: Dict, 
                             original_post: Dict, target_post: Dict) -> Dict:
        """Финальная оценка по правилам MVP"""
        
        # Определяем плагиат по правилам MVP
        text_plagiarism = text_analysis['is_plagiarism']
        image_plagiarism = image_analysis['is_plagiarism']
        
        # Общая схожесть (взвешенная)
        overall_similarity = (
            text_analysis['similarity'] * 0.7 +
            image_analysis['similarity'] * 0.3
        )
        
        # Плагиат если есть плагиат текста ИЛИ изображений
        is_plagiarism = text_plagiarism or image_plagiarism
        
        return {
            'is_plagiarism': is_plagiarism,
            'overall_similarity': overall_similarity,
            'text_similarity': text_analysis['similarity'],
            'image_similarity': image_analysis['similarity'],
            'text_plagiarism': text_plagiarism,
            'image_plagiarism': image_plagiarism,
            'text_reason': text_analysis['reason'],
            'image_reason': image_analysis['reason'],
            'recommendation': self._get_mvp_recommendation(is_plagiarism, text_plagiarism, image_plagiarism)
        }
    
    def _calculate_char_similarity(self, text1: str, text2: str) -> float:
        """Символьное сравнение текстов"""
        if not text1 or not text2:
            return 0.0
        
        # Используем SequenceMatcher для символьного сравнения
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Семантическое сравнение текстов"""
        try:
            tfidf_matrix = self.text_vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception:
            return 0.0
    
    def _calculate_fuzzy_similarity(self, text1: str, text2: str) -> float:
        """Fuzzy match с использованием Levenshtein"""
        from difflib import SequenceMatcher
        
        # Нормализуем тексты
        text1_words = set(text1.lower().split())
        text2_words = set(text2.lower().split())
        
        if not text1_words or not text2_words:
            return 0.0
        
        # Вычисляем Jaccard similarity
        intersection = text1_words.intersection(text2_words)
        union = text1_words.union(text2_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _compare_images_phash(self, url1: str, url2: str) -> Tuple[float, int]:
        """Сравнение изображений с использованием perceptual hash"""
        try:
            img1 = self._download_image(url1)
            img2 = self._download_image(url2)
            
            if img1 is None or img2 is None:
                return 0.0, 999
            
            # Вычисляем perceptual hash
            hash1 = imagehash.phash(img1)
            hash2 = imagehash.phash(img2)
            
            # Вычисляем расстояние Хэмминга
            hamming_distance = hash1 - hash2
            
            # Конвертируем в схожесть (0-1)
            max_distance = 64  # Максимальное расстояние для pHash
            similarity = 1 - (hamming_distance / max_distance)
            
            return max(0.0, min(1.0, similarity)), hamming_distance
            
        except Exception as e:
            print(f"Ошибка сравнения изображений: {e}")
            return 0.0, 999
    
    def _is_posted_after_original(self, original_post: Dict, target_post: Dict) -> bool:
        """Проверка, что пост опубликован позже оригинала"""
        try:
            original_date = datetime.fromtimestamp(original_post.get('date', 0))
            target_date = datetime.fromtimestamp(target_post.get('date', 0))
            
            return target_date > original_date
        except Exception:
            return False
    
    def _has_original_attribution(self, target_post: Dict, original_post: Dict) -> bool:
        """Проверка наличия ссылки на оригинал"""
        text = target_post.get('text', '').lower()
        
        # Проверяем упоминания оригинального автора/группы
        original_owner_id = original_post.get('owner_id', 0)
        
        # Ключевые слова для атрибуции
        attribution_keywords = [
            'источник', 'автор', 'оригинал', 'via', 'from', 'credit',
            'спасибо', 'благодарим', 'подписывайтесь'
        ]
        
        for keyword in attribution_keywords:
            if keyword in text:
                return True
        
        return False
    
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
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста"""
        # Удаление URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Удаление хештегов
        text = re.sub(r'#\w+', '', text)
        
        # Удаление упоминаний
        text = re.sub(r'@\w+', '', text)
        
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_images(self, attachments: List) -> List[str]:
        """Извлечение URL изображений из attachments"""
        images = []
        for attachment in attachments:
            if attachment.get('type') == 'photo':
                photo = attachment.get('photo', {})
                if 'sizes' in photo:
                    # Берем максимальный размер
                    max_size = max(photo['sizes'], key=lambda x: x.get('width', 0))
                    images.append(max_size['url'])
        return images
    
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
    
    def _create_no_plagiarism_result(self, reason: str) -> Dict:
        """Создание результата без плагиата"""
        return {
            'is_plagiarism': False,
            'overall_similarity': 0.0,
            'text_similarity': 0.0,
            'image_similarity': 0.0,
            'text_plagiarism': False,
            'image_plagiarism': False,
            'text_reason': reason,
            'image_reason': 'Не применимо',
            'recommendation': 'Плагиат не обнаружен'
        }
    
    def _get_text_plagiarism_reason(self, similarity: float) -> str:
        """Получение причины для текстового плагиата"""
        if similarity >= 0.9:
            return "Высокая схожесть текста (≥90%) - вероятный плагиат"
        elif similarity >= 0.8:
            return "Средняя схожесть текста (≥80%) - возможный плагиат"
        elif similarity >= 0.7:
            return "Схожесть текста ≥70% - плагиат по правилам MVP"
        else:
            return "Схожесть текста <70% - плагиат не обнаружен"
    
    def _get_image_plagiarism_reason(self, similarity: float, hamming_distance: Optional[int]) -> str:
        """Получение причины для плагиата изображений"""
        if hamming_distance is not None and hamming_distance <= self.image_hamming_threshold:
            return f"Дубликат изображения (расстояние Хэмминга: {hamming_distance} ≤ {self.image_hamming_threshold})"
        else:
            return "Изображения не похожи - плагиат не обнаружен"
    
    def _get_mvp_recommendation(self, is_plagiarism: bool, text_plagiarism: bool, image_plagiarism: bool) -> str:
        """Получение рекомендации по правилам MVP"""
        if not is_plagiarism:
            return "Плагиат не обнаружен"
        
        if text_plagiarism and image_plagiarism:
            return "Плагиат текста и изображений - рекомендуется жалоба"
        elif text_plagiarism:
            return "Плагиат текста ≥70% - рекомендуется жалоба"
        elif image_plagiarism:
            return "Дубликат изображения - рекомендуется жалоба"
        else:
            return "Плагиат не обнаружен" 