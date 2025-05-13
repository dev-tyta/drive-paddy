import numpy as np
import random
import string

# Function to calculate Eye Aspect Ratio (EAR)
def calculate_ear(eye_landmarks, frame_shape):
    # Get the landmarks for the eye
    coords = np.array([(landmark.x * frame_shape[1], landmark.y * frame_shape[0])
                      for landmark in eye_landmarks])
    
    # Calculate the horizontal distance
    horizontal_dist = np.linalg.norm(coords[0] - coords[3])
    
    # Calculate the vertical distances
    vertical_dist1 = np.linalg.norm(coords[1] - coords[5])
    vertical_dist2 = np.linalg.norm(coords[2] - coords[4])
    
    # Calculate the EAR
    ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)
    
    return ear

# Function to generate random gibberish text
def generate_gibberish(length=10):
    letters = string.ascii_lowercase + string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(length))
