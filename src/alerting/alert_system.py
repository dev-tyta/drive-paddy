# drive_paddy/alerting/alert_system.py
import time
import os
import io
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("GEMINI_API_KEY")
class BaseAlerter:
    """Base class for alerter systems."""
    def __init__(self, config):
        self.config = config['alerting']
        self.cooldown = self.config['alert_cooldown_seconds']
        self.last_alert_time = 0
        self.alert_on = False

    def trigger_alert(self):
        raise NotImplementedError

    def reset_alert(self):
        if self.alert_on:
            print("Resetting Alert.")
            self.alert_on = False

class FileAlertSystem(BaseAlerter):
    """Loads a static audio file from disk into memory."""
    def __init__(self, config):
        super().__init__(config)
        self.sound_path = self.config['alert_sound_path']
        self.audio_bytes = None
        try:
            if os.path.exists(self.sound_path):
                with open(self.sound_path, "rb") as f:
                    self.audio_bytes = f.read()
            else:
                print(f"Warning: Alert sound file not found at '{self.sound_path}'.")
        except Exception as e:
            print(f"Warning: Could not load audio file. Error: {e}.")

    def trigger_alert(self):
        current_time = time.time()
        if (current_time - self.last_alert_time) > self.cooldown:
            if not self.alert_on and self.audio_bytes:
                print("Triggering Static Alert!")
                self.last_alert_time = current_time
                self.alert_on = True
                return self.audio_bytes # Return the audio data
        return None


class GeminiAlertSystem(BaseAlerter):
    """Generates dynamic audio data using Gemini and gTTS."""
    def __init__(self, config, api_key):
        super().__init__(config)
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # Use the Gemini model
            print("Gemini Alert System initialized successfully.")
        except Exception as e:
            print(f"Error initializing Gemini: {e}.")
            self.model = None

    def _generate_audio_data(self):
        """Generates a unique alert message and returns it as audio bytes."""
        if not self.model:
            alert_text = "Stay alert!"
        else:
            prompt = "You are an AI driving assistant. Generate a short, friendly, but firm audio alert (under 10 words) for a driver showing signs of drowsiness."
            try:
                response = self.model.generate_content(prompt)
                alert_text = response.text.strip().replace('*', '')
            except Exception as e:
                print(f"Error generating alert text with Gemini: {e}")
                alert_text = "Wake up please!"
        
        print(f"Generated Alert Text: '{alert_text}'")
        try:
            # Generate TTS audio in memory
            mp3_fp = io.BytesIO()
            tts = gTTS(text=alert_text, lang='en')
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return mp3_fp.getvalue()
        except Exception as e:
            print(f"Error generating TTS audio: {e}")
            return None

    def trigger_alert(self):
        current_time = time.time()
        if (current_time - self.last_alert_time) > self.cooldown:
            if not self.alert_on and self.model:
                self.last_alert_time = current_time
                self.alert_on = True
                return self._generate_audio_data() # Return the audio data
        return None


def get_alerter(config, api_key=None):
    """Factory to get the appropriate alerter based on config."""
    use_gemini = config.get('gemini_api', {}).get('enabled', False)
    
    if use_gemini and api_key:
        print("Initializing Gemini Alert System.")
        return GeminiAlertSystem(config, api_key)
    else:
        print("Initializing standard File Alert System.")
        return FileAlertSystem(config)