"""
Models for the database.
"""
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserSettings(Base):
    """
    User settings for the bot, stored in the database.
    """
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False)
    source_language = Column(String, default='auto')  # Язык с которого переводим (auto - автоопределение)
    language = Column(String, default='ru')  # Язык на который переводим
    audio_language = Column(String, default='ru')
    voice_type = Column(String, default='normal')
    speed = Column(Float, default=1.0)
    source_language_name = Column(String, default='Автоопределение')  # Название исходного языка
    language_name = Column(String, default='Русский')
    audio_language_name = Column(String, default='Русский')
    voice_type_name = Column(String, default='Обычный')

    def __repr__(self):
        return f"<UserSettings(user_id='{self.user_id}', language='{self.language}', audio_language='{self.audio_language}', voice_type='{self.voice_type}', speed={self.speed})>"
        
    # Явно объявляем сеттеры для всех атрибутов, чтобы избежать ошибок LSP
    @property
    def get_user_id(self):
        return self.user_id
        
    @get_user_id.setter
    def set_user_id(self, value):
        self.user_id = value
        
    @property
    def get_language(self):
        return self.language
        
    @get_language.setter
    def set_language(self, value):
        self.language = value
        
    @property
    def get_audio_language(self):
        return self.audio_language
        
    @get_audio_language.setter
    def set_audio_language(self, value):
        self.audio_language = value
        
    @property
    def get_voice_type(self):
        return self.voice_type
        
    @get_voice_type.setter
    def set_voice_type(self, value):
        self.voice_type = value
        
    @property
    def get_speed(self):
        return self.speed
        
    @get_speed.setter
    def set_speed(self, value):
        self.speed = value
        
    @property
    def get_language_name(self):
        return self.language_name
        
    @get_language_name.setter
    def set_language_name(self, value):
        self.language_name = value
        
    @property
    def get_audio_language_name(self):
        return self.audio_language_name
        
    @get_audio_language_name.setter
    def set_audio_language_name(self, value):
        self.audio_language_name = value
        
    @property
    def get_voice_type_name(self):
        return self.voice_type_name
        
    @get_voice_type_name.setter
    def set_voice_type_name(self, value):
        self.voice_type_name = value
        
    @property
    def get_source_language(self):
        return self.source_language
        
    @get_source_language.setter
    def set_source_language(self, value):
        self.source_language = value
        
    @property
    def get_source_language_name(self):
        return self.source_language_name
        
    @get_source_language_name.setter
    def set_source_language_name(self, value):
        self.source_language_name = value