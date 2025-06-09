# drive_paddy/pages/1_Live_Detection.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoProcessorBase
import yaml
import av
import os
from dotenv import load_dotenv
import base64
import queue
import time

from src.detection.factory import get_detector
from src.alerting.alert_system import get_alerter

# --- Load Configuration and Environment Variables ---
@st.cache_resource
def load_app_config():
    """Loads config from yaml and .env files."""
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    # Navigate up to the root to find the config file
    config_path = "/config.yaml" if os.path.exists("/config.yaml") else "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config, gemini_api_key

config, gemini_api_key = load_app_config()

# --- Initialize Session State (if not already done in main.py) ---
if "play_audio" not in st.session_state:
    st.session_state.play_audio = None
if "active_alerts" not in st.session_state:
    st.session_state.active_alerts = {"status": "Awake"}

# --- Client-Side Audio Playback Function ---
def autoplay_audio(audio_bytes: bytes):
    """Injects HTML to autoplay audio in the user's browser."""
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio controls autoplay="true" style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- WebRTC Video Processor ---
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self._detector = get_detector(config)
        self._alerter = get_alerter(config, gemini_api_key)

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        
        strategy = config.get('detection_strategy')
        if strategy == 'hybrid':
            processed_frame, alert_triggered, active_alerts = self._detector.process_frame(img)
            st.session_state.active_alerts = active_alerts if alert_triggered else {"status": "Awake"}
        else: # Fallback for simpler strategies
            processed_frame, indicators = self._detector.process_frame(img)
            alert_triggered = any(indicators.values())
            st.session_state.active_alerts = indicators if alert_triggered else {"status": "Awake"}

        if alert_triggered:
            audio_data = self._alerter.trigger_alert()
            if audio_data:
                st.session_state.play_audio = audio_data
        else:
            self._alerter.reset_alert()
            
        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")

# --- Page UI ---
# The st.set_page_config() call has been removed from this file.
# The configuration from main.py will apply to this page.
st.title("📹 Live Drowsiness Detection")
st.info("Press 'START' to activate your camera and begin monitoring.")

# --- Robust RTC Configuration ---
# Provide a list of STUN servers for better reliability.
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]},
        {"urls": ["stun:stun.services.mozilla.com:3478"]},
    ]
})


col1, col2 = st.columns([3, 1])

with col1:
    webrtc_ctx = webrtc_streamer(
        key="drowsiness-detection",
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIGURATION, # Use the new robust configuration
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.header("System Status")
    if not webrtc_ctx.state.playing:
        st.warning("System Inactive.")
    else:
        st.success("✅ System Active & Monitoring")

    st.subheader("Live Status:")
    status_placeholder = st.empty()
    audio_placeholder = st.empty()

if webrtc_ctx.state.playing:
    # --- Polling Loop ---
    try:
        status_result = st.session_state.status_queue.get(timeout=0.1)
    except queue.Empty:
        status_result = None

    # Check for new audio alerts
    try:
        audio_data = st.session_state.audio_queue.get(timeout=0.1)
    except queue.Empty:
        audio_data = None
    
    with status_placeholder.container():
        # Persist the last known status if there's no new one
        if status_result:
            st.session_state.last_status = status_result
        
        last_status = getattr(st.session_state, 'last_status', {"status": "Awake"})
        
        if last_status.get("Low Light"):
             st.warning("⚠️ Low Light Detected! Accuracy may be affected.")
        elif last_status.get("status") == "Awake":
            st.info("✔️ Driver is Awake")
        else:
            st.error("🚨 DROWSINESS DETECTED!")
            for key, value in last_status.items():
                if key != "Low Light":
                    st.warning(f"-> {key}: {value:.2f}" if isinstance(value, float) else f"-> {key}")
    
    if audio_data:
        with audio_placeholder.container():
            autoplay_audio(audio_data)
    
    # Force a rerun to keep the polling active
    time.sleep(0.1)
    st.rerun()

else:
    with status_placeholder.container():
        st.info("✔️ Driver is Awake")
