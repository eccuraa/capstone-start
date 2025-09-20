"""
La Nation - YouTube Live Stream Processor

A sophisticated AI-powered system that processes YouTube videos, transcribes audio 
in real-time, detects specific phrases, and analyzes visual content using advanced 
machine learning APIs.
"""

__version__ = "1.0.0"
__author__ = "Adam Ajroudi"

# Lazy imports to avoid dependency issues
def YouTubeLiveProcessor(*args, **kwargs):
    from .main import YouTubeLiveProcessor as _YouTubeLiveProcessor
    return _YouTubeLiveProcessor(*args, **kwargs)

def PhraseDetector(*args, **kwargs):
    from .phrase_detector import PhraseDetector as _PhraseDetector
    return _PhraseDetector(*args, **kwargs)

def VisionAnalyzer(*args, **kwargs):
    from .vision_analyzer import VisionAnalyzer as _VisionAnalyzer
    return _VisionAnalyzer(*args, **kwargs)

__all__ = [
    "YouTubeLiveProcessor",
    "PhraseDetector", 
    "VisionAnalyzer"
]
