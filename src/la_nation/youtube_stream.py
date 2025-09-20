import os
import time
import subprocess
import tempfile
from urllib.parse import parse_qs, urlparse
import cv2
import pytube
import yt_dlp
import streamlink
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YouTubeStream:
    def __init__(self, url):
        self.url = url
        self.video_id = self._extract_video_id(url)
        self.stream = None
        self.cap = None
        self.audio_file = None
        self.is_live = False
        
    def _extract_video_id(self, url):
        """Extract the video ID from a YouTube URL."""
        if 'youtu.be' in url:
            return url.split('/')[-1]
        query = parse_qs(urlparse(url).query)
        return query.get('v', [None])[0]
    
    def setup(self):
        """Set up the YouTube stream for processing."""
        try:
            logger.info(f"Setting up YouTube stream for video ID: {self.video_id}")
            
            # Try to create a YouTube object with additional options to handle live streams
            yt = pytube.YouTube(self.url, use_oauth=False, allow_oauth_cache=True)
            
            # Check if it's a live stream
            try:
                self.is_live = yt.vid_info.get('videoDetails', {}).get('isLiveContent', False)
                
                if self.is_live:
                    logger.info("Detected a live stream. Attempting to process it.")
                else:
                    logger.info("The provided URL is not a live stream. Will process as a regular video.")
            except:
                logger.warning("Could not determine if the video is live. Proceeding as a regular video.")
                self.is_live = False
            
            # Try to get the best stream with both video and audio
            try:
                self.stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
                
                if not self.stream:
                    # If no progressive stream is available, get the best video-only stream
                    self.stream = yt.streams.filter(only_video=True).order_by('resolution').desc().first()
                
                if not self.stream:
                    # Last resort: try to get any available stream
                    self.stream = yt.streams.first()
                    
                if not self.stream:
                    raise Exception("No suitable stream found")
            except Exception as stream_error:
                logger.error(f"Error getting stream: {str(stream_error)}")
                
                # Fallback: Try to use a different approach for live streams
                if self.is_live:
                    logger.info("Attempting alternative method for live stream...")
                    try:
                        # For demonstration purposes - in a real implementation, 
                        # you might use youtube-dl or yt-dlp as a fallback
                        raise Exception("Live stream processing requires additional tools")
                    except Exception as live_error:
                        logger.error(f"Failed to process live stream: {str(live_error)}")
                        return False
                else:
                    return False
                
            # Create a temporary file for the audio
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            self.audio_file = audio_temp.name
            audio_temp.close()
            
            logger.info(f"Stream setup complete. Using resolution: {self.stream.resolution}")
            return True
        except Exception as e:
            logger.error(f"Error setting up YouTube stream: {str(e)}")
            
            # Provide more helpful error message
            if "is streaming live and cannot be loaded" in str(e):
                logger.error("This appears to be a live stream which pytube cannot process directly.")
                logger.error("Consider using a recorded video for testing or implementing a different library like yt-dlp.")
            
            return False
    
    def start_video_capture(self):
        """Start capturing the video stream."""
        try:
            # For live streams, we'll use the stream URL directly with OpenCV
            if self.is_live:
                stream_url = self.stream.url
                self.cap = cv2.VideoCapture(stream_url)
            else:
                # For non-live videos, download to a temporary file and read from there
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                temp_path = temp_file.name
                temp_file.close()
                
                self.stream.download(output_path=os.path.dirname(temp_path), filename=os.path.basename(temp_path))
                self.cap = cv2.VideoCapture(temp_path)
            
            if not self.cap.isOpened():
                raise Exception("Failed to open video capture")
                
            logger.info("Video capture started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting video capture: {str(e)}")
            return False
    
    def extract_audio(self):
        """Extract audio from the stream for transcription."""
        try:
            if self.is_live:
                # For live streams, we'll use ffmpeg to capture audio in real-time
                cmd = [
                    'ffmpeg',
                    '-i', self.stream.url,
                    '-vn',  # No video
                    '-acodec', 'pcm_s16le',  # PCM format
                    '-ar', '44100',  # Sample rate
                    '-ac', '2',  # Stereo
                    '-f', 'wav',
                    self.audio_file
                ]
                
                # Run in background
                subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Give ffmpeg a moment to start
                time.sleep(2)
            else:
                # For non-live videos, extract audio using ffmpeg
                video_path = self.stream.download(output_path=tempfile.gettempdir())
                
                cmd = [
                    'ffmpeg',
                    '-i', video_path,
                    '-vn',
                    '-acodec', 'pcm_s16le',
                    '-ar', '44100',
                    '-ac', '2',
                    '-f', 'wav',
                    self.audio_file
                ]
                
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Clean up the video file
                os.unlink(video_path)
            
            logger.info(f"Audio extracted to {self.audio_file}")
            return self.audio_file
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return None
    
    def get_frame(self):
        """Get the current frame from the video stream."""
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return frame
    
    def release(self):
        """Release all resources."""
        if self.cap:
            self.cap.release()
        
        if self.audio_file and os.path.exists(self.audio_file):
            try:
                os.unlink(self.audio_file)
            except:
                pass 