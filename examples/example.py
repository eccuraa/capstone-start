#!/usr/bin/env python3
"""
Example script demonstrating how to use the YouTube Live Processor.

This script shows how to process a YouTube live stream, detect specific phrases,
capture screenshots, and analyze them with Google's Gemini Vision API.
"""

import os
from dotenv import load_dotenv

# Import our modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from la_nation import YouTubeLiveProcessor

# Load environment variables
load_dotenv()

def main():
    """Run the example."""
    # YouTube URL - using a known working recorded video
    url = "https://www.youtube.com/watch?v=8jPQjjsBbIc"  # TED Talk about AI
    
    # Phrases to detect - customize these for your use case
    target_phrases = [
        "artificial intelligence",
        "machine learning",
        "neural network",
        "deep learning",
        "data science"
    ]
    
    # Create output directory
    output_dir = "example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and start the processor
    processor = YouTubeLiveProcessor(
        url=url,
        target_phrases=target_phrases,
        output_dir=output_dir
    )
    
    print(f"Starting to process YouTube video: {url}")
    print(f"Detecting phrases: {', '.join(target_phrases)}")
    print("Press Ctrl+C to stop")
    
    # Start processing
    processor.start()

if __name__ == "__main__":
    main() 