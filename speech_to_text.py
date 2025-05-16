"""
Speech-to-text module for converting voice messages to text.
Uses SpeechRecognition library for local speech recognition.
"""
import logging
import os
import tempfile
import subprocess
import speech_recognition as sr

# Logger for this module
logger = logging.getLogger(__name__)

def speech_to_text(audio_path):
    """
    Convert speech to text using offline and online recognition methods.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text from the audio, or empty string if transcription failed
    """
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return ""
    
    # Проверяем наличие Vosk модели сразу
    vosk_model_available = os.path.exists("model") and os.path.isdir("model")
    
    try:
        # Try to convert audio to wav format for better compatibility
        temp_wav_file = convert_to_wav(audio_path)
        file_to_use = temp_wav_file if temp_wav_file else audio_path
        
        # Попробуем сначала использовать Vosk для русского языка, если модель доступна
        if vosk_model_available:
            try:
                import vosk
                import json
                import wave
                
                logger.info("Используем русскую модель Vosk для распознавания речи")
                
                # Конвертируем аудио в WAV формат для Vosk, если еще не сделано
                if not file_to_use.endswith('.wav'):
                    vosk_wav_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                    vosk_wav_file.close()
                    
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(file_to_use)
                    audio = audio.set_frame_rate(16000).set_channels(1)
                    audio.export(vosk_wav_file.name, format="wav")
                    
                    vosk_file = vosk_wav_file.name
                else:
                    vosk_file = file_to_use
                
                # Инициализируем модель и распознаватель
                model = vosk.Model("model")
                
                # Открываем файл как wave объект
                wf = wave.open(vosk_file, "rb")
                
                # Проверяем формат
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    logger.warning("Аудио файл должен быть в формате WAV mono 16bit PCM")
                else:
                    # Создаем распознаватель с правильной частотой дискретизации
                    rec = vosk.KaldiRecognizer(model, wf.getframerate())
                    rec.SetWords(True)  # Включаем информацию о словах
                    
                    # Обрабатываем аудиофайл порциями
                    while True:
                        data = wf.readframes(4000)  # Читаем по 4000 фреймов
                        if len(data) == 0:
                            break
                        rec.AcceptWaveform(data)
                    
                    # Получаем финальный результат
                    result_json = rec.FinalResult()
                    result = json.loads(result_json)
                    
                    # Закрываем файл
                    wf.close()
                    
                    # Удаляем временный файл, если он был создан
                    try:
                        if 'vosk_wav_file' in locals() and hasattr(vosk_wav_file, 'name') and os.path.exists(vosk_wav_file.name):
                            os.remove(vosk_wav_file.name)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить временный файл: {e}")
                    
                    # Проверяем, что результат не пустой
                    if result and "text" in result and result["text"]:
                        text = result["text"]
                        logger.info(f"Transcribed audio with Vosk (Russian): {text}")
                        return text
            except Exception as e:
                logger.warning(f"Ошибка при использовании Vosk: {e}")
        
        # Initialize the recognizer
        recognizer = sr.Recognizer()
        
        # Increase the energy threshold to improve accuracy
        recognizer.energy_threshold = 300
        
        # Load the audio file
        with sr.AudioFile(file_to_use) as source:
            # Adjust for ambient noise and record with more dynamic adjustment
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Set operation timeout to a higher value for better processing (default is 10s)
            audio_data = recognizer.record(source, duration=None)
            
            # Try different recognition services in order
            
            # Try to detect the language of speech - default to Russian as that appears to be what we're getting
            detected_language = "ru"
            
            # 1. Try Google Speech Recognition API with specific language hints
            try:
                # Try with Russian first (or the detected language)
                text = recognizer.recognize_google(audio_data, language=detected_language)
                logger.info(f"Transcribed audio with Google Speech Recognition (language: {detected_language})")
                return text
            except sr.UnknownValueError:
                logger.warning(f"Google Speech Recognition could not understand audio in {detected_language}")
                
                # Try with other languages if Russian fails
                try:
                    # Try English
                    text = recognizer.recognize_google(audio_data, language="en-US")
                    logger.info("Transcribed audio with Google Speech Recognition (language: en-US)")
                    return text
                except sr.UnknownValueError:
                    logger.warning("Google Speech Recognition could not understand audio in en-US")
            except sr.RequestError as e:
                logger.warning(f"Could not request results from Google Speech Recognition service; {e}")
            
            # 2. Try Google Cloud Speech if available
            try:
                # Try with various language options (preferring Russian)
                for lang in ["ru-RU", "en-US"]:
                    try:
                        text = recognizer.recognize_google_cloud(
                            audio_data, 
                            language=lang,
                            preferred_phrases=["привет", "как дела", "что ты умеешь", "спасибо"]
                        )
                        logger.info(f"Transcribed audio with Google Cloud Speech Recognition (language: {lang})")
                        return text
                    except sr.UnknownValueError:
                        logger.warning(f"Google Cloud Speech could not understand audio in {lang}")
                    except sr.RequestError:
                        logger.warning("Google Cloud Speech API not available")
                        break
            except (sr.UnknownValueError, LookupError, AttributeError):
                pass
            
            # 3. Try Sphinx for offline recognition with Russian support
            try:
                # Explicitly specify language model for Russian if available
                # This might not work well without proper language models installed
                language_model = None
                try:
                    # If Russian language model exists
                    if os.path.exists("/usr/local/share/pocketsphinx/model/ru-RU"):
                        language_model = "/usr/local/share/pocketsphinx/model/ru-RU"
                except:
                    pass
                
                if language_model:
                    text = recognizer.recognize_sphinx(audio_data, language=language_model)
                else:
                    text = recognizer.recognize_sphinx(audio_data)
                
                logger.info("Transcribed audio with CMU Sphinx (offline)")
                return text
            except (sr.UnknownValueError, LookupError) as e:
                logger.warning(f"Sphinx could not understand audio or Sphinx not installed: {e}")
            
            # 4. If we have OpenAI API key, use whisper API
            if os.environ.get("OPENAI_API_KEY"):
                from openai import OpenAI
                
                client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                
                with open(file_to_use, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file
                    )
                
                logger.info(f"Transcribed audio with OpenAI API")
                return transcript.text
            
            # Vosk уже проверен выше, поэтому эта часть не нужна
                
            # 6. As a final resort, return a helpful message
            logger.warning("All speech recognition methods failed")
            return "Не удалось распознать речь. Пожалуйста, говорите четче или попробуйте отправить текстовое сообщение."
            
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return f"Ошибка при распознавании речи: {str(e)}"
    finally:
        # Clean up temporary file
        try:
            if 'temp_wav_file' in locals() and temp_wav_file and os.path.exists(temp_wav_file):
                try:
                    os.remove(temp_wav_file)
                except:
                    pass
        except:
            pass

def convert_to_wav(input_file):
    """
    Convert audio file to WAV format for better compatibility with speech recognition.
    
    Args:
        input_file (str): Path to the input audio file
        
    Returns:
        str: Path to the WAV file, or None if conversion failed
    """
    temp_file_name = None
    try:
        from pydub import AudioSegment
        
        # Create a temporary file for WAV audio
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file_name = temp_file.name
        temp_file.close()
        
        # Try to convert using pydub
        try:
            audio = AudioSegment.from_file(input_file)
            audio.export(temp_file_name, format="wav")
            logger.info(f"Converted audio to WAV format using pydub")
            return temp_file_name
        except Exception as pydub_err:
            logger.warning(f"Failed to convert audio with pydub, trying ffmpeg: {pydub_err}")
            
            # Try to convert using ffmpeg directly
            try:
                subprocess.call(['ffmpeg', '-i', input_file, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', temp_file_name, '-y'])
                logger.info(f"Converted audio to WAV format using ffmpeg")
                return temp_file_name
            except Exception as ffmpeg_err:
                logger.error(f"Failed to convert audio to WAV format with ffmpeg: {ffmpeg_err}")
                if temp_file_name and os.path.exists(temp_file_name):
                    os.remove(temp_file_name)
                return None
    
    except Exception as e:
        logger.error(f"Error converting audio to WAV: {e}")
        if temp_file_name and os.path.exists(temp_file_name):
            try:
                os.remove(temp_file_name)
            except:
                pass
        return None