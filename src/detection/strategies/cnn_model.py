# drive_paddy/detection/strategies/cnn_model.py
from src.detection.base_processor import BaseProcessor
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b7
import cv2
import dlib
from PIL import Image
import os

class CnnProcessor(BaseProcessor):
    """
    Drowsiness detection using a pre-trained EfficientNet-B7 model.
    """
    def __init__(self, config):
        self.settings = config['cnn_model_settings']
        self.model_path = self.settings['model_path']
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize dlib for face detection
        self.face_detector = dlib.get_frontal_face_detector()
        
        # Load the model
        self.model = self._load_model()
        
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def _load_model(self):
        """Loads the EfficientNet-B7 model and custom weights."""
        if not os.path.exists(self.model_path):
            print(f"Error: Model file not found at {self.model_path}")
            print("Please run 'python download_model.py' first.")
            return None
            
        try:
            # Initialize the model structure
            model = efficientnet_b7()
            # Modify the final classifier layer to match the number of output classes (e.g., 2: drowsy, not_drowsy)
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = torch.nn.Linear(num_ftrs, 2) # Assuming 2 output classes

            # Load the saved weights
            model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            model.to(self.device)
            model.eval() # Set the model to evaluation mode
            print(f"CNN Model '{self.model_path}' loaded successfully on {self.device}.")
            return model
        except Exception as e:
            print(f"Error loading CNN model: {e}")
            return None

    def process_frame(self, frame):
        """
        Processes a frame to detect drowsiness using the CNN model.
        """
        if self.model is None:
            return frame, {"cnn_prediction": False}

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector(gray)
        is_drowsy_prediction = False

        for face in faces:
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            
            # Crop the face from the frame
            face_crop = frame[y1:y2, x1:x2]
            
            # Ensure the crop is valid before processing
            if face_crop.size == 0:
                continue
                
            # Convert to PIL Image and apply transformations
            pil_image = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
            image_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # Perform inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                _, preds = torch.max(outputs, 1)
                # Assuming class 1 is 'drowsy' and class 0 is 'not_drowsy'
                print(preds)
                if preds.item() == 1:
                    is_drowsy_prediction = True

            # Draw bounding box for visualization
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            label = "Drowsy" if is_drowsy_prediction else "Awake"
            cv2.putText(frame, f"CNN: {label}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Process only the first detected face
            break
            
        return frame, {"cnn_prediction": is_drowsy_prediction}
