import os
import logging
import json
import time
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class VisionAnalyzer:
    def __init__(self, model="gemini-1.5-flash"):
        """
        Initialize the vision analyzer.
        
        Args:
            model: The Gemini model to use for vision analysis
        """
        self.model = model
        self.analysis_history = []
        
    def analyze_image(self, image_path, prompt=None):
        """
        Analyze an image using Google's Gemini Vision API.
        
        Args:
            image_path: Path to the image file
            prompt: Custom prompt for the analysis
            
        Returns:
            Analysis result as text
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
            
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Default prompt if none provided
            if not prompt:
                prompt = "Describe what you see in this image in detail."
                
            # Initialize the Gemini model
            model = genai.GenerativeModel(self.model)
            
            # Call the Gemini API
            response = model.generate_content([prompt, image])
            
            # Extract the analysis
            analysis = response.text
            
            # Save to history
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.analysis_history.append({
                "timestamp": timestamp,
                "image_path": image_path,
                "prompt": prompt,
                "analysis": analysis
            })
            
            logger.info(f"Image analysis completed for {image_path}")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None
            
    def analyze_image_with_context(self, image_path, transcript, 
                                   detected_phrase=None):
        """
        Analyze an image with context from the transcript.
        
        Args:
            image_path: Path to the image file
            transcript: Recent transcript text
            detected_phrase: The phrase that triggered the screenshot
            
        Returns:
            Analysis result as text
        """
        # Build a context-aware prompt
        prompt = "Analyze this image from a YouTube video."
        
        if detected_phrase:
            prompt += f" The phrase '{detected_phrase}' was just mentioned."
            
        if transcript:
            # Limit transcript length
            max_transcript_length = 500
            if len(transcript) > max_transcript_length:
                transcript = transcript[-max_transcript_length:]
                
            prompt += f" Recent transcript: '{transcript}'"
            
        prompt += " Please describe what you see and how it relates to "
        prompt += "what was being discussed."
        
        return self.analyze_image(image_path, prompt)
        
    def get_analysis_history(self):
        """Get the history of image analyses."""
        return self.analysis_history.copy()
        
    def save_analysis_history(self, output_file="analysis_history.json"):
        """
        Save the analysis history to a JSON file.
        
        Args:
            output_file: Path to the output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(self.analysis_history, f, indent=2)
                
            logger.info(f"Analysis history saved to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis history: {str(e)}")
            return False 