"""
User preferences module for storing and managing user settings.
"""
import logging

from constants import (
    DEFAULT_SOURCE_LANGUAGE, DEFAULT_LANGUAGE, DEFAULT_SPEED, DEFAULT_AUDIO_LANGUAGE, 
    AVAILABLE_AUDIO_LANGUAGES, DEFAULT_VOICE_TYPE, VOICE_TYPES
)
from translator import get_available_languages
from database import (
    get_or_create_user_settings,
    update_user_source_language as db_update_source_language,
    update_user_language as db_update_language,
    update_user_audio_language as db_update_audio_language,
    update_user_speed as db_update_speed,
    update_user_voice_type as db_update_voice_type
)

# Настройка логгера
logger = logging.getLogger(__name__)

class UserPreferences:
    """
    Class for storing user preferences including translation language, audio language, speech speed, and voice type.
    Uses database for persistent storage.
    """
    
    def __init__(self, user_id):
        """
        Initialize user preferences from database or with default values if not found.
        
        Args:
            user_id: Telegram user ID
        """
        self.user_id = user_id
        
        try:
            # Получаем настройки пользователя из базы данных или создаем новые
            settings = get_or_create_user_settings(user_id)
            
            # Устанавливаем атрибуты из настроек базы данных
            self.source_language = settings.source_language
            self.language = settings.language
            self.audio_language = settings.audio_language
            try:
                self.speed = float(settings.speed)
            except (ValueError, TypeError):
                self.speed = DEFAULT_SPEED
            self.voice_type = settings.voice_type
            
            # Получаем имена языков и типа голоса
            self.source_language_name = settings.source_language_name
            self.language_name = settings.language_name
            self.audio_language_name = settings.audio_language_name
            self.voice_type_name = settings.voice_type_name
            
            logger.info(f"Loaded preferences for user {user_id} from database")
        except Exception as e:
            # В случае ошибки, используем значения по умолчанию
            logger.error(f"Failed to load preferences from database for user {user_id}: {e}")
            
            self.source_language = DEFAULT_SOURCE_LANGUAGE
            self.language = DEFAULT_LANGUAGE
            self.audio_language = DEFAULT_AUDIO_LANGUAGE
            self.speed = DEFAULT_SPEED
            self.voice_type = DEFAULT_VOICE_TYPE
            
            # Получаем имена языков и типа голоса
            if DEFAULT_SOURCE_LANGUAGE == "auto":
                self.source_language_name = "Автоопределение"
            else:
                source_lang_name = get_available_languages().get(DEFAULT_SOURCE_LANGUAGE)
                self.source_language_name = source_lang_name if source_lang_name else DEFAULT_SOURCE_LANGUAGE.upper()
                
            lang_name = get_available_languages().get(DEFAULT_LANGUAGE)
            self.language_name = lang_name if lang_name else DEFAULT_LANGUAGE.upper()
            
            audio_lang_name = AVAILABLE_AUDIO_LANGUAGES.get(DEFAULT_AUDIO_LANGUAGE)
            self.audio_language_name = audio_lang_name if audio_lang_name else DEFAULT_AUDIO_LANGUAGE.upper()
            
            voice_type_name = VOICE_TYPES.get(DEFAULT_VOICE_TYPE)
            self.voice_type_name = voice_type_name if voice_type_name else DEFAULT_VOICE_TYPE.upper()
    
    def update_language(self, language_code):
        """
        Update the user's preferred translation language and save to database.
        
        Args:
            language_code (str): Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            # Обновляем значение в базе данных
            db_update_language(self.user_id, language_code)
            
            # Обновляем локальные атрибуты
            self.language = language_code
            language_name = get_available_languages().get(language_code)
            if language_name:
                self.language_name = language_name
            else:
                # Если язык не найден в списке, используем код языка с заглавной буквы
                self.language_name = language_code.upper()
            
            logger.info(f"Updated language for user {self.user_id} to {language_code}")
        except Exception as e:
            logger.error(f"Failed to update language for user {self.user_id}: {e}")
    
    def update_audio_language(self, language_code):
        """
        Update the user's preferred audio language for text-to-speech and save to database.
        
        Args:
            language_code (str): Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            # Обновляем значение в базе данных
            db_update_audio_language(self.user_id, language_code)
            
            # Обновляем локальные атрибуты
            self.audio_language = language_code
            audio_language_name = AVAILABLE_AUDIO_LANGUAGES.get(language_code)
            if audio_language_name:
                self.audio_language_name = audio_language_name
            else:
                # Если язык не найден в списке, используем код языка с заглавной буквы
                self.audio_language_name = language_code.upper()
            
            logger.info(f"Updated audio language for user {self.user_id} to {language_code}")
        except Exception as e:
            logger.error(f"Failed to update audio language for user {self.user_id}: {e}")
    
    def update_speed(self, speed):
        """
        Update the user's preferred speech speed and save to database.
        
        Args:
            speed (float): Speed factor (e.g., 0.5, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0)
        """
        try:
            # Преобразуем в float для безопасности
            speed_float = float(speed)
            
            # Обновляем значение в базе данных
            db_update_speed(self.user_id, speed_float)
            
            # Обновляем локальный атрибут
            self.speed = speed_float
            
            logger.info(f"Updated speed for user {self.user_id} to {speed_float}")
        except Exception as e:
            logger.error(f"Failed to update speed for user {self.user_id}: {e}")
        
    def update_source_language(self, language_code):
        """
        Update the user's preferred source language for translation and save to database.
        
        Args:
            language_code (str): Language code (e.g., 'en', 'es', 'fr', or 'auto' for auto-detection)
        """
        try:
            # Обновляем значение в базе данных
            db_update_source_language(self.user_id, language_code)
            
            # Обновляем локальные атрибуты
            self.source_language = language_code
            if language_code == 'auto':
                self.source_language_name = "Автоопределение"
            else:
                language_name = get_available_languages().get(language_code)
                if language_name:
                    self.source_language_name = language_name
                else:
                    # Если язык не найден в списке, используем код языка с заглавной буквы
                    self.source_language_name = language_code.upper()
            
            logger.info(f"Updated source language for user {self.user_id} to {language_code}")
        except Exception as e:
            logger.error(f"Failed to update source language for user {self.user_id}: {e}")
    
    def update_voice_type(self, voice_type):
        """
        Update the user's preferred voice type for text-to-speech and save to database.
        
        Args:
            voice_type (str): Voice type code (e.g., 'normal', 'slow', 'clear', 'emotional')
        """
        try:
            # Обновляем значение в базе данных
            db_update_voice_type(self.user_id, voice_type)
            
            # Обновляем локальные атрибуты
            self.voice_type = voice_type
            self.voice_type_name = VOICE_TYPES.get(voice_type, "Unknown")
            
            logger.info(f"Updated voice type for user {self.user_id} to {voice_type}")
        except Exception as e:
            logger.error(f"Failed to update voice type for user {self.user_id}: {e}")