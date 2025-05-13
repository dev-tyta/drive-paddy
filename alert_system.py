import threading
import time
from gtts import gTTS
import os
import simpleaudio as sa
from pydub import AudioSegment

# Function to generate audio from text
def generate_audio(text):
    try:
        print(f"Generating audio for: {text}")  # Debug print
        tts = gTTS(text=text, lang='en')
        temp_mp3_file = "temp_alert.mp3"
        temp_wav_file = "temp_alert.wav"
        tts.save(temp_mp3_file)

        # Convert MP3 to WAV
        audio = AudioSegment.from_mp3(temp_mp3_file)
        audio.export(temp_wav_file, format="wav")
        
        # Play WAV file
        wave_obj = sa.WaveObject.from_wave_file(temp_wav_file)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing
        
        # Attempt to remove the temporary files
        for temp_file in [temp_mp3_file, temp_wav_file]:
            attempts = 0
            while attempts < 5:
                try:
                    os.remove(temp_file)
                    print(f"Temporary audio file {temp_file} removed.")  # Debug print
                    break
                except PermissionError:
                    print(f"PermissionError: Could not remove {temp_file}. Retrying...")
                    attempts += 1
                    time.sleep(0.2)  # Wait a bit before retrying
                except Exception as e:
                    print(f"Warning: Could not remove temporary audio file {temp_file}. Error: {e}")
                    break
            if attempts == 5:
                print(f"Warning: Failed to remove temporary audio file {temp_file} after multiple attempts.")

    except Exception as e:  # Catch gTTS, pydub, simpleaudio errors or other issues
        print(f"Warning: Could not generate or play TTS audio. Error: {e}")

class AlertSystem:
    def __init__(self):
        self.alarm_on = False
        self.alert_thread = None
        self.last_alert_time = 0

    def trigger_alert(self, gibberish_text):
        # No mixer initialization check needed for simpleaudio in this context
        current_time = time.time()
        if current_time - self.last_alert_time > 3:  # At least 3 seconds between alerts
            self.last_alert_time = current_time
            if not self.alarm_on:
                self.alarm_on = True
                # Play alert sound
                if self.alert_thread is None or not self.alert_thread.is_alive():
                    self.alert_thread = threading.Thread(target=generate_audio, args=(gibberish_text,))
                    self.alert_thread.daemon = True
                    self.alert_thread.start()

    def reset_alert(self):
        self.alarm_on = False
