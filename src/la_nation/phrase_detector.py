import re
import logging
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PhraseDetector:
    def __init__(self, target_phrases=None, context_window=5):
        """
        Initialize the phrase detector.
        
        Args:
            target_phrases: List of phrases to detect
            context_window: Number of transcript chunks to keep in context
        """
        self.target_phrases = target_phrases or []
        self.context_window = context_window
        self.transcript_history = deque(maxlen=context_window)
        self.detected_phrases = []
        
    def add_target_phrase(self, phrase):
        """Add a new phrase to detect."""
        if phrase and phrase not in self.target_phrases:
            self.target_phrases.append(phrase)
            logger.info(f"Added target phrase: '{phrase}'")
            
    def remove_target_phrase(self, phrase):
        """Remove a phrase from detection."""
        if phrase in self.target_phrases:
            self.target_phrases.remove(phrase)
            logger.info(f"Removed target phrase: '{phrase}'")
            
    def process_transcript(self, transcript_chunk):
        """
        Process a new transcript chunk and detect phrases.
        
        Args:
            transcript_chunk: New piece of transcribed text
            
        Returns:
            List of newly detected phrases
        """
        if not transcript_chunk or not self.target_phrases:
            return []
            
        # Add to history
        self.transcript_history.append(transcript_chunk)
        
        # Create a combined text from recent history
        combined_text = " ".join(self.transcript_history).lower()
        
        # Check for phrases
        new_detections = []
        for phrase in self.target_phrases:
            if self._detect_phrase(combined_text, phrase.lower()):
                if phrase not in self.detected_phrases:
                    self.detected_phrases.append(phrase)
                    new_detections.append(phrase)
                    logger.info(f"Detected phrase: '{phrase}'")
                    
        return new_detections
        
    def _detect_phrase(self, text, phrase):
        """
        Detect if a phrase is in the text.
        
        This uses a more flexible matching approach to account for
        transcription errors and variations.
        
        Args:
            text: Text to search in
            phrase: Phrase to look for
            
        Returns:
            True if the phrase is detected, False otherwise
        """
        # Exact match
        if phrase in text:
            return True
            
        # Word-by-word fuzzy match
        phrase_words = phrase.split()
        text_words = text.split()
        
        # For short phrases, require all words to be present
        if len(phrase_words) <= 2:
            return all(word in text_words for word in phrase_words)
            
        # For longer phrases, allow some words to be missing
        match_threshold = 0.75  # 75% of words must match
        matches = sum(1 for word in phrase_words if word in text_words)
        return matches / len(phrase_words) >= match_threshold
        
    def reset(self):
        """Reset the detector state."""
        self.transcript_history.clear()
        self.detected_phrases = []
        
    def get_detected_phrases(self):
        """Get all detected phrases so far."""
        return self.detected_phrases.copy() 