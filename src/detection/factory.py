# drive_paddy/detection/factory.py
from src.detection.strategies.geometric import GeometricProcessor
from src.detection.strategies.cnn_model import CnnProcessor
from src.detection.strategies.hybrid import HybridProcessor

def get_detector(config):
    """
    Factory function to get the appropriate drowsiness detector.
    """
    strategy = config.get('detection_strategy', 'geometric')
    
    if strategy == 'geometric':
        print("Initializing Geometric drowsiness detector...")
        return GeometricProcessor(config)
    elif strategy == 'cnn_model':
        print("Initializing CNN Model drowsiness detector...")
        return CnnProcessor(config)
    elif strategy == 'hybrid':
        print("Initializing Hybrid (Geometric + CNN) drowsiness detector...")
        return HybridProcessor(config)
    else:
        raise ValueError(f"Unknown detection strategy: {strategy}")
