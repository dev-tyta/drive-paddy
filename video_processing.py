import cv2
import mediapipe as mp
import time
import av
from streamlit_webrtc import VideoProcessorBase
from utils import calculate_ear, generate_gibberish
from alert_system import AlertSystem

# Define constants that were previously in main.py and are used here
EYE_AR_THRESHOLD = 0.25  # Eye Aspect Ratio threshold
EYE_AR_CONSEC_FRAMES = 20  # Number of consecutive frames to trigger alarm

# Initialize face detector and facial landmarks detector
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Video processor class for drowsiness detection
class DrowsinessDetector(VideoProcessorBase):
    def __init__(self):
        self.eye_counter = 0
        self.frame_counter = 0
        self.start_time = time.time()
        self.fps = 0
        self.alert_system = AlertSystem()
        
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Update FPS counter
        self.frame_counter += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.fps = self.frame_counter / elapsed_time
            self.frame_counter = 0
            self.start_time = time.time()
            
        # Process with Face Mesh
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get facial landmarks
                landmarks = face_landmarks.landmark
                
                # Eye landmarks (using MediaPipe Face Mesh indices)
                # Left eye
                left_eye = [landmarks[i] for i in [362, 385, 387, 263, 373, 380]]
                # Right eye
                right_eye = [landmarks[i] for i in [33, 160, 158, 133, 153, 144]]
                
                # Calculate EAR for both eyes
                left_ear = calculate_ear(left_eye, img.shape)
                right_ear = calculate_ear(right_eye, img.shape)
                
                # Average EAR
                ear = (left_ear + right_ear) / 2.0
                
                # Get nose landmark for visualization (optional, can be removed if not needed)
                nose = landmarks[4]
                nose_x, nose_y = int(nose.x * img.shape[1]), int(nose.y * img.shape[0])
                
                # Draw face and eye landmarks for visualization
                for landmark in left_eye + right_eye:
                    x, y = int(landmark.x * img.shape[1]), int(landmark.y * img.shape[0])
                    cv2.circle(img, (x, y), 2, (0, 255, 0), -1)
                
                cv2.circle(img, (nose_x, nose_y), 5, (255, 0, 0), -1)
                
                # Check if eyes are closed
                if ear < EYE_AR_THRESHOLD:
                    self.eye_counter += 1
                    # Draw red rectangle when eyes are closing
                    cv2.rectangle(img, (0, 0), (img.shape[1], img.shape[0]), (0, 0, 255), 5)
                    
                    # Trigger alarm if eyes remain closed for sufficient frames
                    if self.eye_counter >= EYE_AR_CONSEC_FRAMES:
                        gibberish = generate_gibberish(20)
                        cv2.putText(img, f"WAKE UP! {gibberish}", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        self.alert_system.trigger_alert(gibberish)
                else:
                    self.eye_counter = 0
                    self.alert_system.reset_alert()
                
                # Display EAR value
                cv2.putText(img, f"EAR: {ear:.2f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display FPS
        cv2.putText(img, f"FPS: {self.fps:.2f}", (img.shape[1] - 120, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")
