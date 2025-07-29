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


class PlagiarismDetector:
    def __init__(self):
        self.text_vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95
        )
        # Более строгие пороги для минимизации ложных срабатываний
        self.text_similarity_threshold = 0.85  # Было 0.7
        self.image_similarity_threshold = 0.90  # Было 0.7
        self.overall_similarity_threshold = 0.80  # Было 0.7
        
        # Минимальная длина текста для анализа
        self.min_text_length = 50
        
        # Ключевые слова для исключения
        self.common_phrases = [
            'спасибо за внимание', 'подписывайтесь', 'ставьте лайки',
            'репост', 'поделиться', 'комментарий', 'вопрос',
            'интересно', 'полезно', 'важно', 'срочно'
        ]
    
    def detect_plagiarism(self, original_post: Dict, target_post: Dict) -> Dict:
        """Основной метод детекции плагиата с учетом правил ВКонтакте"""
        
        # Проверяем, не является ли пост репостом
        if self.is_repost(target_post):
            return self._create_no_plagiarism_result("Пост является репостом")
        
        # Анализируем текст
        text_analysis = self._analyze_text_plagiarism(
            original_post.get('text', ''),
            target_post.get('text', '')
        )
        
        # Анализируем изображения
        image_analysis = self._analyze_image_plagiarism(
            original_post.get('attachments', []),
            target_post.get('attachments', [])
        )
        
        # Применяем правила ВКонтакте
        vk_rules_check = self._check_vk_rules(text_analysis, image_analysis)
        
        # Финальная оценка
        result = self._final_evaluation(text_analysis, image_analysis, vk_rules_check)
        
        return result
    
    def _analyze_text_plagiarism(self, original_text: str, target_text: str) -> Dict:
        """Улучшенный анализ текстового плагиата"""
        
        # Очистка текстов
        original_clean = self._clean_text(original_text)
        target_clean = self._clean_text(target_text)
        
        # Проверка минимальной длины
        if len(original_clean) < self.min_text_length or len(target_clean) < self.min_text_length:
            return {
                'similarity': 0.0,
                'reason': 'Недостаточная длина текста для анализа',
                'is_plagiarism': False
            }
        
        # Проверка на общие фразы
        if self._is_common_content(original_clean, target_clean):
            return {
                'similarity': 0.0,
                'reason': 'Содержит общие фразы и шаблоны',
                'is_plagiarism': False
            }
        
        # Анализ структуры предложений
        structure_similarity = self._analyze_sentence_structure(original_clean, target_clean)
        
        # TF-IDF анализ
        tfidf_similarity = self._calculate_tfidf_similarity(original_clean, target_clean)
        
        # Анализ ключевых фраз
        phrase_similarity = self._analyze_key_phrases(original_clean, target_clean)
        
        # Взвешенная оценка
        text_similarity = (
            tfidf_similarity * 0.5 +
            structure_similarity * 0.3 +
            phrase_similarity * 0.2
        )
        
        return {
            'similarity': text_similarity,
            'tfidf_similarity': tfidf_similarity,
            'structure_similarity': structure_similarity,
            'phrase_similarity': phrase_similarity,
            'is_plagiarism': text_similarity >= self.text_similarity_threshold,
            'reason': self._get_text_plagiarism_reason(text_similarity)
        }
    
    def _analyze_image_plagiarism(self, original_attachments: List, target_attachments: List) -> Dict:
        """Улучшенный анализ плагиата изображений"""
        
        original_images = self._extract_images(original_attachments)
        target_images = self._extract_images(target_attachments)
        
        if not original_images or not target_images:
            return {
                'similarity': 0.0,
                'reason': 'Нет изображений для сравнения',
                'is_plagiarism': False
            }
        
        # Сравниваем каждое изображение
        max_similarity = 0.0
        best_match = None
        
        for orig_img in original_images:
            for target_img in target_images:
                similarity = self._compare_images(orig_img, target_img)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = (orig_img, target_img)
        
        return {
            'similarity': max_similarity,
            'is_plagiarism': max_similarity >= self.image_similarity_threshold,
            'reason': self._get_image_plagiarism_reason(max_similarity),
            'best_match': best_match
        }
    
    def _check_vk_rules(self, text_analysis: Dict, image_analysis: Dict) -> Dict:
        """Проверка по правилам ВКонтакте"""
        
        rules_violations = []
        
        # Правило 1: Минимальный объем заимствования
        if text_analysis['similarity'] > 0.7 and text_analysis['similarity'] < 0.85:
            rules_violations.append("Недостаточный объем заимствования для жалобы")
        
        # Правило 2: Творческая переработка
        if text_analysis['structure_similarity'] < 0.3 and text_analysis['tfidf_similarity'] < 0.6:
            rules_violations.append("Контент может быть творческой переработкой")
        
        # Правило 3: Общедоступная информация
        if self._is_public_information(text_analysis):
            rules_violations.append("Информация может быть общедоступной")
        
        # Правило 4: Временной фактор
        if self._is_recent_content():
            rules_violations.append("Контент слишком свежий для определения плагиата")
        
        return {
            'violations': rules_violations,
            'can_report': len(rules_violations) == 0,
            'reason': '; '.join(rules_violations) if rules_violations else 'Соответствует правилам ВКонтакте'
        }
    
    def _final_evaluation(self, text_analysis: Dict, image_analysis: Dict, vk_rules: Dict) -> Dict:
        """Финальная оценка плагиата"""
        
        # Общая схожесть
        overall_similarity = (
            text_analysis['similarity'] * 0.7 +
            image_analysis['similarity'] * 0.3
        )
        
        # Определяем, является ли это плагиатом
        is_plagiarism = (
            overall_similarity >= self.overall_similarity_threshold and
            vk_rules['can_report'] and
            (text_analysis['is_plagiarism'] or image_analysis['is_plagiarism'])
        )
        
        # Уровень уверенности
        confidence = self._calculate_confidence(text_analysis, image_analysis, vk_rules)
        
        return {
            'is_plagiarism': is_plagiarism,
            'overall_similarity': overall_similarity,
            'text_similarity': text_analysis['similarity'],
            'image_similarity': image_analysis['similarity'],
            'confidence': confidence,
            'text_reason': text_analysis['reason'],
            'image_reason': image_analysis['reason'],
            'vk_rules_reason': vk_rules['reason'],
            'can_report_to_vk': vk_rules['can_report'],
            'recommendation': self._get_recommendation(is_plagiarism, confidence, vk_rules)
        }
    
    def _analyze_sentence_structure(self, text1: str, text2: str) -> float:
        """Анализ структуры предложений"""
        sentences1 = re.split(r'[.!?]+', text1)
        sentences2 = re.split(r'[.!?]+', text2)
        
        # Сравниваем порядок и структуру предложений
        common_sentences = 0
        for sent1 in sentences1:
            for sent2 in sentences2:
                if self._similar_sentence(sent1, sent2):
                    common_sentences += 1
        
        return min(1.0, common_sentences / max(len(sentences1), len(sentences2)))
    
    def _analyze_key_phrases(self, text1: str, text2: str) -> float:
        """Анализ ключевых фраз"""
        # Извлекаем фразы длиной 3-5 слов
        phrases1 = self._extract_phrases(text1, 3, 5)
        phrases2 = self._extract_phrases(text2, 3, 5)
        
        common_phrases = 0
        for phrase1 in phrases1:
            for phrase2 in phrases2:
                if self._similar_phrase(phrase1, phrase2):
                    common_phrases += 1
        
        return min(1.0, common_phrases / max(len(phrases1), len(phrases2)))
    
    def _calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Вычисление TF-IDF схожести"""
        try:
            tfidf_matrix = self.text_vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception:
            return 0.0
    
    def _is_common_content(self, text1: str, text2: str) -> bool:
        """Проверка на общий контент"""
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        for phrase in self.common_phrases:
            if phrase in text1_lower and phrase in text2_lower:
                return True
        
        return False
    
    def _is_public_information(self, text_analysis: Dict) -> bool:
        """Проверка на общедоступную информацию"""
        # Здесь можно добавить проверку на новости, факты, даты и т.д.
        return False
    
    def _is_recent_content(self) -> bool:
        """Проверка временного фактора"""
        # Посты должны быть разнесены во времени
        return False
    
    def _calculate_confidence(self, text_analysis: Dict, image_analysis: Dict, vk_rules: Dict) -> float:
        """Вычисление уровня уверенности"""
        confidence = 0.0
        
        # Высокая уверенность при высокой схожести
        if text_analysis['similarity'] > 0.9:
            confidence += 0.4
        elif text_analysis['similarity'] > 0.8:
            confidence += 0.3
        elif text_analysis['similarity'] > 0.7:
            confidence += 0.2
        
        # Дополнительная уверенность при схожести изображений
        if image_analysis['similarity'] > 0.9:
            confidence += 0.3
        elif image_analysis['similarity'] > 0.8:
            confidence += 0.2
        
        # Снижение уверенности при нарушениях правил ВК
        if not vk_rules['can_report']:
            confidence *= 0.5
        
        return min(1.0, confidence)
    
    def _get_recommendation(self, is_plagiarism: bool, confidence: float, vk_rules: Dict) -> str:
        """Получение рекомендации"""
        if not is_plagiarism:
            return "Плагиат не обнаружен"
        
        if confidence > 0.8 and vk_rules['can_report']:
            return "Высокая вероятность плагиата - можно жаловаться"
        elif confidence > 0.6:
            return "Средняя вероятность плагиата - требует ручной проверки"
        else:
            return "Низкая вероятность плагиата - не рекомендуется жаловаться"
    
    def _clean_text(self, text: str) -> str:
        """Улучшенная очистка текста"""
        # Удаление URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Удаление хештегов
        text = re.sub(r'#\w+', '', text)
        
        # Удаление упоминаний
        text = re.sub(r'@\w+', '', text)
        
        # Удаление эмодзи
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_phrases(self, text: str, min_words: int, max_words: int) -> List[str]:
        """Извлечение фраз из текста"""
        words = text.split()
        phrases = []
        
        for i in range(len(words) - min_words + 1):
            for j in range(min_words, min(max_words + 1, len(words) - i + 1)):
                phrase = ' '.join(words[i:i+j])
                if len(phrase) > 10:  # Минимальная длина фразы
                    phrases.append(phrase)
        
        return phrases
    
    def _similar_sentence(self, sent1: str, sent2: str) -> bool:
        """Проверка схожести предложений"""
        if len(sent1) < 10 or len(sent2) < 10:
            return False
        
        # Простое сравнение по словам
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) > 0.7
    
    def _similar_phrase(self, phrase1: str, phrase2: str) -> bool:
        """Проверка схожести фраз"""
        return self._similar_sentence(phrase1, phrase2)
    
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
    
    def _compare_images(self, url1: str, url2: str) -> float:
        """Сравнение изображений"""
        try:
            img1 = self._download_image(url1)
            img2 = self._download_image(url2)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # Используем несколько алгоритмов хеширования
            hash1_avg = imagehash.average_hash(img1)
            hash2_avg = imagehash.average_hash(img2)
            
            hash1_phash = imagehash.phash(img1)
            hash2_phash = imagehash.phash(img2)
            
            # Вычисляем схожесть по двум алгоритмам
            similarity_avg = 1 - (hash1_avg - hash2_avg) / 64
            similarity_phash = 1 - (hash1_phash - hash2_phash) / 64
            
            # Возвращаем среднее значение
            return max(0.0, min(1.0, (similarity_avg + similarity_phash) / 2))
            
        except Exception as e:
            print(f"Ошибка сравнения изображений: {e}")
            return 0.0
    
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
    
    def _create_no_plagiarism_result(self, reason: str) -> Dict:
        """Создание результата без плагиата"""
        return {
            'is_plagiarism': False,
            'overall_similarity': 0.0,
            'text_similarity': 0.0,
            'image_similarity': 0.0,
            'confidence': 0.0,
            'text_reason': reason,
            'image_reason': 'Не применимо',
            'vk_rules_reason': 'Не применимо',
            'can_report_to_vk': False,
            'recommendation': 'Плагиат не обнаружен'
        }
    
    def _get_text_plagiarism_reason(self, similarity: float) -> str:
        """Получение причины для текстового плагиата"""
        if similarity >= 0.9:
            return "Высокая схожесть текста - вероятный плагиат"
        elif similarity >= 0.8:
            return "Средняя схожесть текста - возможный плагиат"
        elif similarity >= 0.7:
            return "Низкая схожесть текста - требует проверки"
        else:
            return "Текст не похож - плагиат маловероятен"
    
    def _get_image_plagiarism_reason(self, similarity: float) -> str:
        """Получение причины для плагиата изображений"""
        if similarity >= 0.9:
            return "Высокая схожесть изображений - вероятный плагиат"
        elif similarity >= 0.8:
            return "Средняя схожесть изображений - возможный плагиат"
        else:
            return "Изображения не похожи - плагиат маловероятен" 