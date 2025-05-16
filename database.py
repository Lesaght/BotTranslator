"""
Database module for connecting to the database and managing session.
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from models import Base, UserSettings
from constants import (
    DEFAULT_SOURCE_LANGUAGE, DEFAULT_LANGUAGE, DEFAULT_AUDIO_LANGUAGE, 
    DEFAULT_VOICE_TYPE, DEFAULT_SPEED,
    VOICE_TYPES, AVAILABLE_AUDIO_LANGUAGES
)
from translator import get_available_languages

# Логгер
logger = logging.getLogger(__name__)

# Получение URL базы данных из переменных окружения
# В случае отсутствия переменной окружения DATABASE_URL используем SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")

# Проверяем, что DATABASE_URL не пустой
if not DATABASE_URL:
    logger.warning("DATABASE_URL not set or empty, using SQLite database instead")
    DATABASE_URL = "sqlite:///bot.db"

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создание сессии
Session = sessionmaker(bind=engine)

def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_or_create_user_settings(user_id):
    """
    Get user settings from the database, or create them if they don't exist.
    
    Args:
        user_id: User ID from Telegram
        
    Returns:
        UserSettings object with the user's preferences
    """
    session = Session()
    try:
        # Пытаемся получить настройки пользователя из базы данных
        settings = session.query(UserSettings).filter_by(user_id=str(user_id)).first()
        
        # Если настройки не найдены, создаем новые
        if not settings:
            # Получаем имена языков
            language_name = get_available_languages().get(DEFAULT_LANGUAGE)
            if not language_name:
                language_name = DEFAULT_LANGUAGE.upper()
                
            if DEFAULT_SOURCE_LANGUAGE == "auto":
                source_language_name = "Автоопределение"
            else:
                source_language_name = get_available_languages().get(DEFAULT_SOURCE_LANGUAGE)
                if not source_language_name:
                    source_language_name = DEFAULT_SOURCE_LANGUAGE.upper()
                    
            audio_language_name = AVAILABLE_AUDIO_LANGUAGES.get(DEFAULT_AUDIO_LANGUAGE)
            if not audio_language_name:
                audio_language_name = DEFAULT_AUDIO_LANGUAGE.upper()
                
            voice_type_name = VOICE_TYPES.get(DEFAULT_VOICE_TYPE)
            if not voice_type_name:
                voice_type_name = DEFAULT_VOICE_TYPE.upper()
            
            # Создаем новые настройки
            settings = UserSettings()
            settings.user_id = str(user_id)
            settings.source_language = DEFAULT_SOURCE_LANGUAGE
            settings.language = DEFAULT_LANGUAGE
            settings.audio_language = DEFAULT_AUDIO_LANGUAGE
            settings.voice_type = DEFAULT_VOICE_TYPE
            settings.speed = DEFAULT_SPEED
            settings.source_language_name = source_language_name
            settings.language_name = language_name
            settings.audio_language_name = audio_language_name
            settings.voice_type_name = voice_type_name
            
            session.add(settings)
            session.commit()
            logger.info(f"Created new settings for user {user_id}")
        
        # Создаем копию объекта, чтобы избежать ошибки "не привязан к сессии"
        user_settings = UserSettings()
        user_settings.id = settings.id
        user_settings.user_id = settings.user_id
        user_settings.source_language = settings.source_language
        user_settings.language = settings.language 
        user_settings.audio_language = settings.audio_language
        user_settings.voice_type = settings.voice_type
        user_settings.speed = settings.speed
        user_settings.source_language_name = settings.source_language_name
        user_settings.language_name = settings.language_name
        user_settings.audio_language_name = settings.audio_language_name
        user_settings.voice_type_name = settings.voice_type_name
        
        return user_settings
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while getting user settings: {e}")
        raise
    finally:
        session.close()

def update_user_language(user_id, language_code):
    """
    Update user's preferred translation language.
    
    Args:
        user_id: User ID from Telegram
        language_code: Language code to set
    """
    session = Session()
    try:
        settings = session.query(UserSettings).filter_by(user_id=str(user_id)).first()
        if settings:
            settings.language = language_code
            # Получаем имя языка
            language_name = get_available_languages().get(language_code)
            # Обновляем имя языка
            if language_name:
                settings.language_name = language_name
            else:
                # Если язык не найден в списке, используем код языка с заглавной буквы
                settings.language_name = language_code.upper()
            session.commit()
            logger.info(f"Updated language for user {user_id} to {language_code}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while updating user language: {e}")
        raise
    finally:
        session.close()

def update_user_audio_language(user_id, language_code):
    """
    Update user's preferred audio language.
    
    Args:
        user_id: User ID from Telegram
        language_code: Language code to set
    """
    session = Session()
    try:
        settings = session.query(UserSettings).filter_by(user_id=str(user_id)).first()
        if settings:
            settings.audio_language = language_code
            # Получаем имя языка озвучивания
            audio_language_name = AVAILABLE_AUDIO_LANGUAGES.get(language_code)
            # Обновляем имя языка озвучивания
            if audio_language_name:
                settings.audio_language_name = audio_language_name
            else:
                # Если язык не найден в списке, используем код языка с заглавной буквы
                settings.audio_language_name = language_code.upper()
            session.commit()
            logger.info(f"Updated audio language for user {user_id} to {language_code}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while updating user audio language: {e}")
        raise
    finally:
        session.close()

def update_user_voice_type(user_id, voice_type):
    """
    Update user's preferred voice type.
    
    Args:
        user_id: User ID from Telegram
        voice_type: Voice type code to set
    """
    session = Session()
    try:
        settings = session.query(UserSettings).filter_by(user_id=str(user_id)).first()
        if settings:
            settings.voice_type = voice_type
            # Получаем имя типа голоса
            voice_type_name = VOICE_TYPES.get(voice_type)
            # Обновляем имя типа голоса
            if voice_type_name:
                settings.voice_type_name = voice_type_name
            else:
                # Если тип голоса не найден в списке, используем код типа с заглавной буквы
                settings.voice_type_name = voice_type.upper()
            session.commit()
            logger.info(f"Updated voice type for user {user_id} to {voice_type}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while updating user voice type: {e}")
        raise
    finally:
        session.close()

def update_user_source_language(user_id, language_code):
    """
    Update user's preferred source language for translation.
    
    Args:
        user_id: User ID from Telegram
        language_code: Language code to set (or 'auto' for automatic detection)
    """
    session = Session()
    try:
        settings = session.query(UserSettings).filter_by(user_id=str(user_id)).first()
        if settings:
            settings.source_language = language_code
            # Получаем имя языка
            if language_code == 'auto':
                source_language_name = "Автоопределение"
            else:
                source_language_name = get_available_languages().get(language_code)
                if not source_language_name:
                    # Если язык не найден в списке, используем код языка с заглавной буквы
                    source_language_name = language_code.upper()
            # Обновляем имя языка
            settings.source_language_name = source_language_name
            session.commit()
            logger.info(f"Updated source language for user {user_id} to {language_code}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while updating user source language: {e}")
        raise
    finally:
        session.close()

def update_user_speed(user_id, speed):
    """
    Update user's preferred speech speed.
    
    Args:
        user_id: User ID from Telegram
        speed: Speed value to set
    """
    session = Session()
    try:
        settings = session.query(UserSettings).filter_by(user_id=str(user_id)).first()
        if settings:
            # Преобразуем в float для безопасности
            speed_float = float(speed)
            # Обновляем скорость
            settings.speed = speed_float
            session.commit()
            logger.info(f"Updated speed for user {user_id} to {speed}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error while updating user speed: {e}")
        raise
    finally:
        session.close()