import speech_recognition as sr
import sys
import time

recognizer = sr.Recognizer()
# Disable voice for now - use text input instead
VOICE_AVAILABLE = True  # Set to False to skip microphone and use text input

# Try importing audio libraries
try:
    import sounddevice
except ImportError:
    try:
        import pyaudio
    except (ImportError, AttributeError, OSError, RuntimeError):
        VOICE_AVAILABLE = False

# Text-to-speech support
TTS_AVAILABLE = False
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

engine = None


def get_engine():
    global engine

    if not TTS_AVAILABLE:
        return None

    if engine is None:
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 160)
        except Exception:
            return None

    return engine


def speak(text):
    """Speak text aloud using TTS if supported."""
    if not text:
        return

    try:
        current_engine = get_engine()
        if current_engine is None:
            print(f"JARVIS: {text}")
            return

        current_engine.stop()
        current_engine.say(text)
        current_engine.runAndWait()
    except Exception:
        print(f"JARVIS: {text}")


def listen():
    """Listen for voice input, or fall back to text input if unavailable"""
    
    if not VOICE_AVAILABLE:
        # Fallback: text input
        text = input("You: ").strip()
        return text
    
    try:
        with sr.Microphone() as source:
            print("🎤 Listening... (3 seconds or press Ctrl+C for text)")
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)

        try:
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text
        except sr.UnknownValueError:
            print("I couldn't understand that.")
            return ""
        except sr.RequestError as e:
            print(f"API Error: {e}")
            return ""

    except KeyboardInterrupt:
        # User pressed Ctrl+C - fall back to text
        print("\nFalling back to text input...")
        text = input("You: ").strip()
        return text
    except sr.exceptions.WaitTimeoutError:
        # No audio detected - fallback to text input
        print("\nNo audio detected. Using text input...")
        text = input("You: ").strip()
        return text
    except (OSError, RuntimeError) as e:
        # PyAudio error at runtime - fallback to text input
        print(f"Microphone error: {type(e).__name__}")
        print("Falling back to text input...")
        text = input("You: ").strip()
        return text
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}")
        print("Falling back to text input...")
        text = input("You: ").strip()
        return text
        return text