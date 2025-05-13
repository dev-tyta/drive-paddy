import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
from video_processing import DrowsinessDetector, EYE_AR_THRESHOLD, EYE_AR_CONSEC_FRAMES # Import constants from video_processing

# Set page config
st.set_page_config(
    page_title="Driver Drowsiness Detection System",
    page_icon="🚗",
    layout="wide"
)

# Define constants not moved to video_processing
# HEAD_TILT_THRESHOLD = 25 # This constant was in the original file but not used. Removed for now.

# Streamlit UI
def main():
    st.title("Driver Drowsiness Detection System")
    
    # Sidebar for configuration
    st.sidebar.header("Detection Settings")
    # Use the imported constants as default values
    ear_threshold = st.sidebar.slider("Eye Aspect Ratio Threshold", 0.1, 0.4, EYE_AR_THRESHOLD, 0.01)
    frame_threshold = st.sidebar.slider("Consecutive Frames Threshold", 5, 50, EYE_AR_CONSEC_FRAMES, 1)
    
    # Update constants in video_processing module if changed by user
    # This requires a mechanism to pass these values to the DrowsinessDetector instance
    # For now, DrowsinessDetector uses the constants defined in video_processing.py
    # A more robust solution would involve passing these as parameters to DrowsinessDetector
    # or having a shared configuration object.

    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("Live Detection")
        webrtc_ctx = webrtc_streamer(
            key="drowsiness-detection",
            video_processor_factory=DrowsinessDetector, # DrowsinessDetector will use its own EYE_AR_THRESHOLD and EYE_AR_CONSEC_FRAMES
            rtc_configuration=RTCConfiguration(
                {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
            ),
            media_stream_constraints={"video": True, "audio": False},
        )
    
    with col2:
        st.header("Status")
        status_placeholder = st.empty()
        
        if webrtc_ctx.state.playing:
            status_placeholder.success("System Active")
        else:
            status_placeholder.warning("System Inactive - Click 'Start' to begin monitoring")
        
        st.subheader("How It Works")
        st.markdown("""
        1. **Eye Monitoring**: Detects eye closure using Eye Aspect Ratio (EAR)
        2. **Alert System**: Triggers audio alerts when drowsiness is detected
        3. **Real-time Processing**: Analyzes video feed continuously
        """)
        
        st.subheader("Tips")
        st.info("Ensure good lighting for accurate detection")

if __name__ == "__main__":
    main()