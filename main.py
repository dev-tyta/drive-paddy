# drive_paddy/main.py
import streamlit as st
import yaml
import os
from dotenv import load_dotenv

# --- Main Application UI ---
st.set_page_config(
    page_title="Drive Paddy | Home",
    page_icon="🚗",
    layout="wide"
)

# Load config to display current settings on the home page
@st.cache_resource
def load_app_config():
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config, gemini_api_key

config, gemini_api_key = load_app_config()

# --- Initialize Session State ---
# This ensures they are set when the app first loads.
if "play_audio" not in st.session_state:
    st.session_state.play_audio = None
if "active_alerts" not in st.session_state:
    st.session_state.active_alerts = {"status": "Awake"}


# --- Page Content ---
st.title("🚗 Welcome to Drive Paddy!")
st.subheader("Your AI-Powered Drowsiness Detection Assistant")

st.markdown("""
Drive Paddy is a real-time system designed to enhance driver safety by detecting signs of drowsiness. 
It uses your computer's webcam to analyze facial features and head movements, providing timely alerts 
to help prevent fatigue-related accidents.
""")

st.info("Navigate to the **Live Detection** page from the sidebar on the left to start the system.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("How It Works")
    st.markdown("""
    The system employs a sophisticated hybrid strategy to monitor for signs of fatigue:
    - **👀 Eye Closure Detection**: Measures Eye Aspect Ratio (EAR) to detect prolonged blinks or closed eyes.
    - **🥱 Yawn Detection**: Measures Mouth Aspect Ratio (MAR) to identify yawns.
    - **😴 Head Pose Analysis**: Tracks head pitch and yaw to detect nodding off or looking away from the road.
    - **🧠 CNN Model Inference**: A deep learning model provides an additional layer of analysis.
    
    These signals are combined into a single drowsiness score to trigger alerts accurately.
    """)

with col2:
    st.header("Current Configuration")
    alert_method = "Gemini API" if config.get('gemini_api', {}).get('enabled') and gemini_api_key else "Static Audio File"
    st.markdown(f"""
    - **Detection Strategy**: `{config['detection_strategy']}`
    - **Alert Method**: `{alert_method}`
    """)
    st.warning("Ensure good lighting and that your face is clearly visible for best results.")

st.markdown("---")
st.markdown("Created with ❤️ using Streamlit, OpenCV, and MediaPipe.")

