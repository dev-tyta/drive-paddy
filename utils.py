# utils.py

import numpy as np
import cv2
# Removed: import random, string, generate_gibberish

# Function to calculate Eye Aspect Ratio (EAR)
def calculate_ear(eye_landmarks, frame_shape):
    """
    Calculates the Eye Aspect Ratio (EAR) for a given eye.

    Args:
        eye_landmarks: A list of 6 MediaPipe landmark objects for the eye.
                       Expected order: [p1, p2, p3, p4, p5, p6]
                       where p1, p4 are horizontal extremes, and p2, p3, p5, p6
                       are vertical extremes.
        frame_shape: Tuple (height, width) of the frame.

    Returns:
        The calculated EAR value.
    """
    if len(eye_landmarks) != 6:
        # print("Warning: Expected 6 eye landmarks, but received", len(eye_landmarks)) # Optional warning
        return 0.0 # Return 0 or handle error appropriately

    # Convert MediaPipe landmarks to numpy array (pixel coordinates)
    coords = np.array([(landmark.x * frame_shape[1], landmark.y * frame_shape[0])
                      for landmark in eye_landmarks])

    # Calculate the Euclidean distances between the two sets of vertical eye landmarks
    # p2-p6 and p3-p5
    vertical_dist1 = np.linalg.norm(coords[1] - coords[5])
    vertical_dist2 = np.linalg.norm(coords[2] - coords[4])

    # Calculate the Euclidean distance between the horizontal eye landmark
    # p1-p4
    horizontal_dist = np.linalg.norm(coords[0] - coords[3])

    # Calculate the EAR
    # Avoid division by zero
    if horizontal_dist == 0:
        return 0.0

    ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)

    return ear

def draw_landmarks(image, landmarks, connections=None, point_color=(0, 255, 0), connection_color=(255, 255, 255)):
    """
    Draws landmarks and connections on the image.

    Args:
        image: The image (numpy array) to draw on.
        landmarks: A list of MediaPipe landmark objects.
        connections: A list of tuples representing landmark connections (e.g., [(0, 1), (1, 2)]).
        point_color: Color for the landmarks (BGR tuple).
        connection_color: Color for the connections (BGR tuple).
    """
    if not landmarks:
        return image

    img_h, img_w, _ = image.shape
    landmark_points = [(int(l.x * img_w), int(l.y * img_h)) for l in landmarks]

    # Draw connections
    if connections:
        for connection in connections:
            p1 = landmark_points[connection[0]]
            p2 = landmark_points[connection[1]]
            cv2.line(image, p1, p2, connection_color, 1)

    # Draw points
    for point in landmark_points:
         cv2.circle(image, point, 2, point_color, -1)

    return image