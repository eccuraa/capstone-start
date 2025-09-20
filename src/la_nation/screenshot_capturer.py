import os
import cv2
import time
import logging
import threading
from datetime import datetime
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScreenshotCapturer:
    def __init__(self, output_dir="screenshots"):
        """
        Initialize the screenshot capturer.
        
        Args:
            output_dir: Directory to save screenshots
        """
        self.output_dir = output_dir
        self.last_capture_time = 0
        self.min_capture_interval = 2  # Minimum seconds between captures
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def capture_screenshot(self, frame, phrase=None, throttle=True):
        """
        Capture a screenshot from the provided frame.
        
        Args:
            frame: The video frame to capture
            phrase: The phrase that triggered the capture (for filename)
            throttle: Whether to enforce minimum capture interval
            
        Returns:
            Path to the saved screenshot, or None if capture was skipped
        """
        # Check if we should throttle captures
        current_time = time.time()
        if throttle and (current_time - self.last_capture_time) < self.min_capture_interval:
            logger.debug("Skipping capture due to throttling")
            return None
            
        self.last_capture_time = current_time
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            phrase_tag = ""
            if phrase:
                # Clean phrase for filename
                phrase_tag = "_" + "".join(c if c.isalnum() else "_" for c in phrase)
                phrase_tag = phrase_tag[:50]  # Limit length
                
            filename = f"screenshot_{timestamp}{phrase_tag}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save the screenshot
            if isinstance(frame, np.ndarray):
                # OpenCV frame
                cv2.imwrite(filepath, frame)
            else:
                # PIL Image
                frame.save(filepath)
                
            logger.info(f"Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}")
            return None
            
    def capture_async(self, frame, phrase=None):
        """
        Capture a screenshot asynchronously.
        
        Args:
            frame: The video frame to capture
            phrase: The phrase that triggered the capture
            
        Returns:
            True if the capture was initiated, False otherwise
        """
        try:
            # Make a copy of the frame to avoid issues with it being modified
            if isinstance(frame, np.ndarray):
                frame_copy = frame.copy()
            else:
                frame_copy = frame.copy()
                
            # Start a thread to capture the screenshot
            threading.Thread(
                target=self.capture_screenshot,
                args=(frame_copy, phrase),
                daemon=True
            ).start()
            
            return True
        except Exception as e:
            logger.error(f"Error initiating async capture: {str(e)}")
            return False
            
    def convert_to_pil_image(self, frame):
        """
        Convert an OpenCV frame to a PIL Image.
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            PIL Image object
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        return Image.fromarray(rgb_frame) 