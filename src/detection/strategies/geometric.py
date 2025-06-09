# drive_paddy/detection/strategies/geometric.py
import cv2
import mediapipe as mp
import numpy as np
import math
from ..base_processor import BaseProcessor

# --- Helper Functions ---
def calculate_ear(eye_landmarks, frame_shape):
    """Calculates the Eye Aspect Ratio (EAR)."""
    # ... (implementation remains the same)
    coords = np.array([(lm.x * frame_shape[1], lm.y * frame_shape[0]) for lm in eye_landmarks])
    v1 = np.linalg.norm(coords[1] - coords[5]); v2 = np.linalg.norm(coords[2] - coords[4])
    h1 = np.linalg.norm(coords[0] - coords[3])
    return (v1 + v2) / (2.0 * h1) if h1 > 0 else 0.0

def calculate_mar(mouth_landmarks, frame_shape):
    """Calculates the Mouth Aspect Ratio (MAR) for yawn detection."""
    coords = np.array([(lm.x * frame_shape[1], lm.y * frame_shape[0]) for lm in mouth_landmarks])
    v1 = np.linalg.norm(coords[1] - coords[7]) # Vertical distances
    v2 = np.linalg.norm(coords[2] - coords[6])
    v3 = np.linalg.norm(coords[3] - coords[5])
    h1 = np.linalg.norm(coords[0] - coords[4]) # Horizontal distance
    return (v1 + v2 + v3) / (2.0 * h1) if h1 > 0 else 0.0

class GeometricProcessor(BaseProcessor):
    """
    Drowsiness detection using a combination of facial landmarks:
    - Eye Aspect Ratio (EAR) for eye closure.
    - Mouth Aspect Ratio (MAR) for yawning.
    - Head Pose Estimation for nodding off or looking away.
    """
    def __init__(self, config):
        self.settings = config['geometric_settings']
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # State counters
        self.counters = {
            "eye_closure": 0, "yawning": 0,
            "head_nod": 0, "looking_away": 0
        }

        # Landmark indices
        self.L_EYE = [362, 385, 387, 263, 373, 380]
        self.R_EYE = [33, 160, 158, 133, 153, 144]
        self.MOUTH = [61, 291, 39, 181, 0, 17, 84, 178]

    def process_frame(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        results = self.face_mesh.process(img_rgb)
        
        drowsiness_indicators = {
            "eye_closure": False, "yawning": False,
            "head_nod": False, "looking_away": False, "details": {}
        }

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # --- Eye Closure Detection (EAR) ---
            left_ear = calculate_ear([landmarks[i] for i in self.L_EYE], (h, w))
            right_ear = calculate_ear([landmarks[i] for i in self.R_EYE], (h, w))
            ear = (left_ear + right_ear) / 2.0
            if ear < self.settings['eye_ar_thresh']:
                self.counters['eye_closure'] += 1
                if self.counters['eye_closure'] >= self.settings['eye_ar_consec_frames']:
                    drowsiness_indicators['eye_closure'] = True
            else:
                self.counters['eye_closure'] = 0
            drowsiness_indicators['details']['EAR'] = ear

            # --- Yawn Detection (MAR) ---
            mar = calculate_mar([landmarks[i] for i in self.MOUTH], (h, w))
            if mar > self.settings['yawn_mar_thresh']:
                self.counters['yawning'] += 1
                if self.counters['yawning'] >= self.settings['yawn_consec_frames']:
                    drowsiness_indicators['yawning'] = True
            else:
                self.counters['yawning'] = 0
            drowsiness_indicators['details']['MAR'] = mar
                
            # --- Head Pose Estimation ---
            face_3d = np.array([
                [0.0, 0.0, 0.0],            # Nose tip
                [0.0, -330.0, -65.0],       # Chin
                [-225.0, 170.0, -135.0],    # Left eye left corner
                [225.0, 170.0, -135.0],     # Right eye right corner
                [-150.0, -150.0, -125.0],   # Left Mouth corner
                [150.0, -150.0, -125.0]     # Right mouth corner
            ], dtype=np.float64)
            face_2d = np.array([
                (landmarks[1].x * w, landmarks[1].y * h),   # Nose tip
                (landmarks[152].x * w, landmarks[152].y * h), # Chin
                (landmarks[263].x * w, landmarks[263].y * h), # Left eye corner
                (landmarks[33].x * w, landmarks[33].y * h),   # Right eye corner
                (landmarks[287].x * w, landmarks[287].y * h), # Left mouth corner
                (landmarks[57].x * w, landmarks[57].y * h)   # Right mouth corner
            ], dtype=np.float64)

            cam_matrix = np.array([[w, 0, w / 2], [0, w, h / 2], [0, 0, 1]], dtype=np.float64)
            _, rot_vec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, np.zeros((4, 1), dtype=np.float64))
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            
            pitch, yaw = angles[0], angles[1]
            drowsiness_indicators['details']['Pitch'] = pitch
            drowsiness_indicators['details']['Yaw'] = yaw

            if pitch > self.settings['head_nod_thresh']:
                self.counters['head_nod'] += 1
                if self.counters['head_nod'] >= self.settings['head_pose_consec_frames']:
                    drowsiness_indicators['head_nod'] = True
            else:
                self.counters['head_nod'] = 0

            if abs(yaw) > self.settings['head_look_away_thresh']:
                self.counters['looking_away'] += 1
                if self.counters['looking_away'] >= self.settings['head_pose_consec_frames']:
                    drowsiness_indicators['looking_away'] = True
            else:
                self.counters['looking_away'] = 0

        # This processor now returns the frame and a dictionary of indicators
        return frame, drowsiness_indicators
