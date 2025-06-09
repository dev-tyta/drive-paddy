# drive_paddy/detection/base_processor.py
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """
    Abstract Base Class for a drowsiness detection processor.
    
    This defines the common interface that all detection strategies
    (e.g., Geometric, CNN Model) must follow.
    """
    
    @abstractmethod
    def process_frame(self, frame):
        """
        Processes a single video frame to detect drowsiness.

        Args:
            frame: The video frame (as a NumPy array) to process.

        Returns:
            A tuple containing:
            - The processed frame (NumPy array) with visualizations.
            - A boolean indicating if an alert should be triggered.
        """
        pass

