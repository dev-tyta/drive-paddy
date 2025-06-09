# drive_paddy/detection/strategies/hybrid.py
from src.detection.base_processor import BaseProcessor
from src.detection.strategies.geometric import GeometricProcessor
from src.detection.strategies.cnn_model import CnnProcessor
import cv2
import concurrent.futures

class HybridProcessor(BaseProcessor):
    """
    Combines outputs from multiple detection strategies (Geometric and CNN)
    concurrently to make a more robust and efficient drowsiness decision.
    This version includes frame skipping for the CNN model to improve performance.
    """
    def __init__(self, config):
        self.geometric_processor = GeometricProcessor(config)
        self.cnn_processor = CnnProcessor(config)
        self.weights = config['hybrid_settings']['weights']
        self.alert_threshold = config['hybrid_settings']['alert_threshold']
        self.active_alerts = {}
        
        # --- Performance Optimization ---
        self.frame_counter = 0
        self.cnn_process_interval = 10  # Run CNN every 10 frames
        self.last_cnn_indicators = {"cnn_prediction": False} # Cache the last CNN result

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    def process_frame(self, frame):
        self.frame_counter += 1

        # --- Concurrent Execution ---
        # The geometric processor runs on every frame.
        geo_future = self.executor.submit(self.geometric_processor.process_frame, frame.copy())

        # The CNN processor only runs on specified intervals.
        if self.frame_counter % self.cnn_process_interval == 0:
            cnn_future = self.executor.submit(self.cnn_processor.process_frame, frame.copy())
        
        # Get the result from the geometric processor.
        geo_frame, geo_indicators = geo_future.result()

        # Get the CNN result if it was run, otherwise use the cached result.
        if self.frame_counter % self.cnn_process_interval == 0:
            _, self.last_cnn_indicators = cnn_future.result()
        
        cnn_indicators = self.last_cnn_indicators
        
        # Calculate weighted drowsiness score from the combined results.
        score = 0
        self.active_alerts.clear()

        if geo_indicators.get("eye_closure"):
            score += self.weights['eye_closure']
            self.active_alerts['Eyes Closed'] = geo_indicators['details'].get('EAR', 0)
        if geo_indicators.get("yawning"):
            score += self.weights['yawning']
            self.active_alerts['Yawning'] = geo_indicators['details'].get('MAR', 0)
        if geo_indicators.get("head_nod"):
            score += self.weights['head_nod']
            self.active_alerts['Head Nod'] = geo_indicators['details'].get('Pitch', 0)
        if geo_indicators.get("looking_away"):
            score += self.weights['looking_away']
            self.active_alerts['Looking Away'] = geo_indicators['details'].get('Yaw', 0)
        if cnn_indicators.get("cnn_prediction"):
            score += self.weights['cnn_prediction']
            self.active_alerts['CNN Alert'] = 'Active'

        # --- Visualization ---
        output_frame = geo_frame
        y_pos = 30
        for alert, value in self.active_alerts.items():
            text = f"{alert}: {value:.2f}" if isinstance(value, float) else alert
            cv2.putText(output_frame, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_pos += 25
            
        cv2.putText(output_frame, f"Score: {score:.2f}", (output_frame.shape[1] - 150, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        alert_triggered = score >= self.alert_threshold
        if alert_triggered:
            cv2.rectangle(output_frame, (0, 0), (output_frame.shape[1], output_frame.shape[0]), (0, 0, 255), 5)

        # Return the processed frame, the alert trigger, and the active alert details
        return output_frame, alert_triggered, self.active_alerts
