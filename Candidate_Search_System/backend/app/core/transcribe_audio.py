import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
from app.config import Config
from app.utils.parsers import correct_words
import logging

logger = logging.getLogger(__name__)

WHISPER_MODEL = Config.WHISPER_MODEL
_NATIVE_SR_FORMATS = {".wav", ".flac", ".aiff", ".aif"}

def transcribe_audio(audio_path: str, debug: bool = False) -> str:
    recognizer = sr.Recognizer()
    converted_path = None

    try:
        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in _NATIVE_SR_FORMATS:
            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            fd, converted_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            audio.export(converted_path, format="wav")
            load_path = converted_path
        else:
            load_path = audio_path

        if debug:
            debug_path = os.path.join(tempfile.gettempdir(), "debug_transcribe.wav")
            AudioSegment.from_file(load_path).export(debug_path, format="wav")
            logger.debug(f"Converted audio saved at: {debug_path}")

        with sr.AudioFile(load_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)

        text = recognizer.recognize_whisper(audio_data, model=WHISPER_MODEL, language="english")
        text_corrected = correct_words(text)
        return text_corrected

    except sr.UnknownValueError:
        raise Exception("Could not understand the audio. Speak clearly and try again.")

    except sr.RequestError as e:
        raise Exception(f"Transcription service error: {str(e)}")

    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

    finally:
        if converted_path and os.path.exists(converted_path):
            try:
                os.unlink(converted_path)
            except:
                pass