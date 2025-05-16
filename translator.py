"""
Translator module for text translation between languages.
Uses the deep-translator library for translations.
"""
import logging
from deep_translator import GoogleTranslator

# Logger for this module
logger = logging.getLogger(__name__)

def get_available_languages():
    """
    Get a dictionary of available languages for translation.
    
    Returns:
        dict: Dictionary of language codes and names
    """
    # Define a subset of commonly used languages to avoid overwhelming the user
    common_languages = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh-CN': 'Chinese (Simplified)',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'tr': 'Turkish',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'fi': 'Finnish',
        'pl': 'Polish',
        'uk': 'Ukrainian'
    }
    
    return common_languages

def translate_text(text, target_language, source_language='auto'):
    """
    Translate text to the target language.
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (e.g., 'en', 'es', 'fr')
        source_language (str): Source language code, or 'auto' for auto-detection (default: 'auto')
        
    Returns:
        str: Translated text, or original text if translation failed
    """
    if not text or not target_language:
        return text
    
    # Если целевой и исходный языки совпадают, возвращаем исходный текст
    if source_language != 'auto' and source_language == target_language:
        logger.info(f"Source and target languages are the same ({target_language}), skipping translation")
        return text
    
    try:
        # Create a translator with source and target language
        translator = GoogleTranslator(source=source_language, target=target_language)
        
        # Translate the text
        translated = translator.translate(text)
        logger.info(f"Translated text from {source_language} to {target_language}")
        
        return translated
    
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return text  # Return original text in case of error
