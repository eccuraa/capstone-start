#!/usr/bin/env python3
import os
import time
import argparse
import logging
import threading
import signal
import sys
from dotenv import load_dotenv

# Import our modules
from .enhanced_youtube_stream import EnhancedYouTubeStream
from .transcription import LiveTranscriber
from .phrase_detector import PhraseDetector
from .screenshot_capturer import ScreenshotCapturer
from .vision_analyzer import VisionAnalyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("youtube_processor.log")
    ]
)
logger = logging.getLogger(__name__)

class YouTubeLiveProcessor:
    def __init__(self, url, target_phrases=None, output_dir="output"):
        """
        Initialize the YouTube Live Processor.
        
        Args:
            url: YouTube video URL
            target_phrases: List of phrases to detect
            output_dir: Directory to save outputs
        """
        self.url = url
        self.target_phrases = target_phrases or []
        self.output_dir = output_dir
        self.stop_event = threading.Event()
        
        # Create output directories
        self.screenshots_dir = os.path.join(output_dir, "screenshots")
        self.transcripts_dir = os.path.join(output_dir, "transcripts")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.transcripts_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)  # Ensure main output dir exists
        
        # Initialize components
        self.stream = EnhancedYouTubeStream(url)
        self.transcriber = None
        self.detector = PhraseDetector(target_phrases)
        self.capturer = ScreenshotCapturer(self.screenshots_dir)
        self.analyzer = VisionAnalyzer()
        
        # Initialize transcript tracking
        self.transcript_counter = 0
        self.full_transcript = ""
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, sig, frame):
        """Handle termination signals."""
        logger.info("Received termination signal. Shutting down...")
        self.stop()
    
    def _save_transcript_chunk(self, transcript_chunk):
        """
        Save a transcript chunk to file and update the full transcript.
        
        Args:
            transcript_chunk: The transcript text to save
        """
        try:
            # Increment counter and add to full transcript
            self.transcript_counter += 1
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Save individual chunk
            chunk_filename = f"segment_{self.transcript_counter:03d}_{timestamp}.txt"
            chunk_path = os.path.join(self.transcripts_dir, chunk_filename)
            
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(f"La Nation - Transcript Segment {self.transcript_counter}\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Video: {self.url}\n")
                f.write("=" * 50 + "\n\n")
                f.write(transcript_chunk)
            
            # Add to full transcript
            self.full_transcript += f"\n[{time.strftime('%H:%M:%S')}] {transcript_chunk}"
            
            # Save updated full transcript
            full_transcript_path = os.path.join(self.transcripts_dir, "full_transcript.txt")
            with open(full_transcript_path, 'w', encoding='utf-8') as f:
                f.write(f"La Nation - Complete Live Stream Transcript\n")
                f.write(f"Video: {self.url}\n")
                f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Segments processed: {self.transcript_counter}\n")
                f.write("=" * 60 + "\n")
                f.write(self.full_transcript)
            
            logger.info(f"💾 Saved transcript chunk {self.transcript_counter}: {len(transcript_chunk)} characters")
            
        except Exception as e:
            logger.error(f"❌ Failed to save transcript chunk: {e}")
            
    def _save_final_transcript(self):
        """Save the final complete transcript with summary."""
        try:
            if self.full_transcript:
                # Save final transcript with metadata
                final_path = os.path.join(self.output_dir, "final_transcript.txt")
                with open(final_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("LA NATION - LIVE STREAM ANALYSIS COMPLETE\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"🎬 Video URL: {self.url}\n")
                    f.write(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"📊 Total segments: {self.transcript_counter}\n")
                    f.write(f"📝 Total characters: {len(self.full_transcript)}\n")
                    f.write(f"🔍 Target phrases: {', '.join(self.target_phrases) if self.target_phrases else 'None'}\n")
                    f.write(f"📂 Output directory: {self.output_dir}\n\n")
                    f.write("COMPLETE TRANSCRIPT:\n")
                    f.write("=" * 60 + "\n")
                    f.write(self.full_transcript)
                
                logger.info(f"📋 Final transcript saved: {final_path}")
                print(f"\n📋 Complete transcript saved to: {final_path}")
                print(f"📊 Total processed: {self.transcript_counter} segments, {len(self.full_transcript)} characters")
            else:
                logger.warning("⚠️ No transcript content to save")
                
        except Exception as e:
            logger.error(f"❌ Failed to save final transcript: {e}")
        
    def setup(self):
        """Set up all components."""
        logger.info(f"Setting up YouTube Live Processor for URL: {self.url}")
        
        # Set up the stream
        if not self.stream.setup():
            logger.error("Failed to set up YouTube stream")
            return False
            
        # Initialize transcriber for continuous processing
        # We'll extract and process audio chunks continuously in the main loop
        self.transcriber = None
        
        # Track timing for continuous audio extraction (start immediately)
        self.last_extraction_time = 0
        
        # Start video capture
        if not self.stream.start_video_capture():
            logger.error("Failed to start video capture")
            return False
            
        logger.info("YouTube Live Processor setup complete")
        return True
        
    def start(self):
        """Start processing the YouTube stream."""
        if not self.setup():
            return False
            
        logger.info("Starting YouTube Live Processor")
        
        # Main processing loop with continuous audio extraction
        try:
            while not self.stop_event.is_set():
                # Check if it's time to extract a new 30-second audio chunk
                current_time = time.time()
                if current_time - self.last_extraction_time >= 30:  # Every 30 seconds
                    logger.info("🎵 Extracting new 30-second audio chunk...")
                    
                    # Extract 30 seconds of fresh audio from the live stream
                    audio_file = self.stream.extract_audio(duration_seconds=30)
                    
                    if audio_file:
                        # Process this audio chunk directly
                        transcript_chunk = self._process_audio_chunk_direct(audio_file)
                        
                        if transcript_chunk:
                            # Save the transcript chunk to file
                            self._save_transcript_chunk(transcript_chunk)
                        
                        # Update timing for next extraction
                        self.last_extraction_time = current_time
                    else:
                        logger.warning("⚠️ Failed to extract audio chunk, retrying...")
                
                # Small sleep to avoid high CPU usage
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in main processing loop: {str(e)}")
            return False
        finally:
            self.stop()
            
        return True

    def _process_audio_chunk_direct(self, audio_file):
        """
        Process an audio chunk directly by transcribing it synchronously.
        
        Args:
            audio_file: Path to the audio file to transcribe
            
        Returns:
            str: The transcribed text, or None if transcription failed
        """
        try:
            logger.info(f"🎧 Processing audio chunk: {audio_file}")
            
            # Import transcriber to use direct transcription method
            from .transcription import LiveTranscriber
            
            # Create a temporary transcriber instance for direct transcription
            temp_transcriber = LiveTranscriber()
            
            # Directly transcribe the audio file (synchronous)
            transcript = temp_transcriber._transcribe_audio_file(audio_file)
            
            if transcript and transcript.strip():
                logger.info(f"✅ Audio transcribed: {len(transcript)} characters")
                return transcript.strip()
            else:
                logger.warning("⚠️ No transcript generated from audio chunk")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error transcribing audio chunk: {e}")
            return None

    def _save_transcript_chunk(self, transcript_chunk):
        """
        Save a transcript chunk to file and update the full transcript.
        """
        try:
            self.transcript_counter += 1
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            chunk_filename = f"segment_{self.transcript_counter:03d}_{timestamp}.txt"
            chunk_path = os.path.join(self.transcripts_dir, chunk_filename)
            
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(f"La Nation - Transcript Segment {self.transcript_counter}\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Video: {self.url}\n")
                f.write("=" * 50 + "\n\n")
                f.write(transcript_chunk)
            
            # Update full transcript
            self.full_transcript += f"\n[{time.strftime('%H:%M:%S')}] {transcript_chunk}"
            
            # Save running full transcript
            full_transcript_path = os.path.join(self.transcripts_dir, "full_transcript.txt")
            with open(full_transcript_path, 'w', encoding='utf-8') as f:
                f.write(f"La Nation - Complete Live Stream Transcript\n")
                f.write(f"Video: {self.url}\n")
                f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Segments processed: {self.transcript_counter}\n")
                f.write("=" * 60 + "\n")
                f.write(self.full_transcript)
            
            logger.info(f"💾 Saved transcript chunk {self.transcript_counter}: {len(transcript_chunk)} characters")
        except Exception as e:
            logger.error(f"❌ Failed to save transcript chunk: {e}")

    def _save_final_transcript(self):
        """Save the final complete transcript with summary."""
        try:
            if self.full_transcript:
                final_path = os.path.join(self.output_dir, "final_transcript.txt")
                with open(final_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("LA NATION - LIVE STREAM ANALYSIS COMPLETE\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"🎬 Video URL: {self.url}\n")
                    f.write(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"📊 Total segments: {self.transcript_counter}\n")
                    f.write(f"📝 Total characters: {len(self.full_transcript)}\n")
                    f.write(f"🔍 Target phrases: {', '.join(self.target_phrases) if self.target_phrases else 'None'}\n")
                    f.write(f"📂 Output directory: {self.output_dir}\n\n")
                    f.write("COMPLETE TRANSCRIPT:\n")
                    f.write("=" * 60 + "\n")
                    f.write(self.full_transcript)
                logger.info(f"📋 Final transcript saved: {final_path}")
                print(f"\n📋 Complete transcript saved to: {final_path}")
                print(f"📊 Total processed: {self.transcript_counter} segments, {len(self.full_transcript)} characters")
            else:
                logger.warning("⚠️ No transcript content to save")
        except Exception as e:
            logger.error(f"❌ Failed to save final transcript: {e}")
        
    def stop(self):
        """Stop all processing."""
        if self.stop_event.is_set():
            return
            
        logger.info("Stopping YouTube Live Processor")
        self.stop_event.set()
        
        # Note: No transcriber to stop in continuous mode
            
        # Release stream resources
        if self.stream:
            self.stream.release()
            
        # Save final transcript
        self._save_final_transcript()
            
        # Save analysis history
        self.analyzer.save_analysis_history(
            os.path.join(self.output_dir, "analysis_history.json")
        )
        
        logger.info("YouTube Live Processor stopped")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process a YouTube live stream")
    
    parser.add_argument(
        "--url", 
        required=True,
        help="YouTube video URL"
    )
    
    parser.add_argument(
        "--phrases",
        help="Comma-separated list of phrases to detect",
        default=""
    )
    
    parser.add_argument(
        "--output-dir",
        help="Directory to save outputs",
        default="output"
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Parse phrases
    target_phrases = [p.strip() for p in args.phrases.split(",") if p.strip()]
    
    # Create processor
    processor = YouTubeLiveProcessor(
        url=args.url,
        target_phrases=target_phrases,
        output_dir=args.output_dir
    )
    
    # Start processing
    processor.start()

if __name__ == "__main__":
    main() 