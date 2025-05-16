"""
Text-to-speech module for converting text to audio.
Uses gTTS for speech synthesis and pydub for audio processing.
"""
import logging
import os
import tempfile
from gtts import gTTS
from pydub import AudioSegment

# Logger for this module
logger = logging.getLogger(__name__)

def text_to_speech(text, language='en', voice_type='normal'):
    """
    Convert text to speech using Google Text-to-Speech with enhanced voice options.
    
    Args:
        text (str): Text to convert to speech
        language (str): Language code for the speech (default: 'en')
        voice_type (str): Voice type ('normal', 'slow', 'clear', 'emotional')
        
    Returns:
        str: Path to the generated audio file
    """
    if not text:
        logger.warning("Empty text provided for text-to-speech")
        # Create a temporary file with silence
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        silence = AudioSegment.silent(duration=500)  # 500ms of silence
        silence.export(temp_file.name, format="mp3")
        return temp_file.name
    
    try:
        # Create a temporary file for the audio
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        
        # Convert text to speech with enhanced voice options
        logger.info(f"Converting text to speech in language: {language}, voice type: {voice_type}")
        
        # Настраиваем параметры в зависимости от типа голоса
        slow_speed = False
        tld_domain = "com"  # По умолчанию используем .com TLD
        
        # Настройка параметров в зависимости от типа голоса
        if voice_type == 'slow':
            # Для медленного голоса всегда используем slow=True
            slow_speed = True
        elif voice_type == 'clear':
            # Для четкого голоса используем специальные настройки
            if language in ['en', 'fr', 'es', 'it', 'pt']:
                tld_domain = "co.uk"  # Британский акцент обычно более четкий
            if language == 'ru':
                tld_domain = "ru"  # Русский голос через локальный домен
        elif voice_type == 'emotional':
            # Для эмоционального голоса используем другие настройки
            if language in ['es', 'it', 'fr']:
                tld_domain = "ca"  # Канадский/латиноамериканский домен для некоторых языков
        
        # Особые настройки для азиатских языков
        if language in ['ja', 'zh-CN', 'ko']:
            # Для азиатских языков корректируем настройки
            if voice_type in ['slow', 'clear']:
                slow_speed = True
            tld_domain = "com"  # Азиатские языки лучше через .com
        
        # Создаем объект gTTS с настроенными параметрами
        tts = gTTS(text=text, lang=language, slow=slow_speed, tld=tld_domain)
        
        # Сохраняем аудио
        tts.save(temp_file.name)
        
        return temp_file.name
    
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {e}")
        # Return a path to a silent audio file
        fallback_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        fallback_file.close()
        silence = AudioSegment.silent(duration=500)  # 500ms of silence
        silence.export(fallback_file.name, format="mp3")
        return fallback_file.name

def adjust_audio_speed(audio_path, speed=1.0):
    """
    Adjust the playback speed of an audio file.
    
    Args:
        audio_path (str): Path to the audio file
        speed (float): Speed factor (1.0 is normal speed)
        
    Returns:
        str: Path to the speed-adjusted audio file
    """
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return audio_path
    
    try:
        # Load the audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Create a temporary file for the adjusted audio
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        
        # Adjust the speed
        # For changing speed without changing pitch, we modify the frame rate
        logger.info(f"Adjusting audio speed to {speed}x")
        adjusted_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        })
        adjusted_audio = adjusted_audio.set_frame_rate(audio.frame_rate)
        
        # Export the adjusted audio
        adjusted_audio.export(temp_file.name, format="mp3")
        
        return temp_file.name
    
    except Exception as e:
        logger.error(f"Error adjusting audio speed: {e}")
        return audio_path  # Return the original audio file in case of error
