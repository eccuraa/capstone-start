#!/usr/bin/env python3
"""
Enhanced YouTube Stream Handler with Multiple Strategies
Uses the working approaches discovered through testing
"""

import os
import time
import subprocess
import tempfile
import json
from urllib.parse import parse_qs, urlparse
import cv2
import yt_dlp
import logging

logger = logging.getLogger(__name__)

class EnhancedYouTubeStream:
    """
    Enhanced YouTube stream handler that uses multiple strategies
    to overcome API restrictions and access limitations.
    """
    
    def __init__(self, url):
        self.url = url
        self.video_id = self._extract_video_id(url)
        self.stream = None
        self.stream_url = None
        self.cap = None
        self.audio_file = None
        self.is_live = False
        self.title = ''
        self.format_info = None
        self.stream_quality = None
        self.successful_strategy = None
        
    def _extract_video_id(self, url):
        """Extract the video ID from a YouTube URL."""
        if 'youtu.be' in url:
            return url.split('/')[-1]
        query = parse_qs(urlparse(url).query)
        return query.get('v', [None])[0]
    
    def setup(self):
        """Set up the YouTube stream for processing using multiple strategies."""
        logger.info(f"🎬 Setting up enhanced YouTube stream for video ID: {self.video_id}")
        
        # Strategy 1: Try yt-dlp (most reliable for live streams)
        if self._setup_with_ytdlp():
            self.successful_strategy = 'yt-dlp'
            logger.info("✅ Successfully set up with yt-dlp")
            return True
        
        # Strategy 2: Try streamlink (good for live streams)
        if self._setup_with_streamlink():
            self.successful_strategy = 'streamlink'
            logger.info("✅ Successfully set up with streamlink")
            return True
        
        # Strategy 3: Try direct extraction
        if self._setup_with_direct_extraction():
            self.successful_strategy = 'direct_extraction'
            logger.info("✅ Successfully set up with direct extraction")
            return True
        
        logger.error("❌ All enhanced setup strategies failed")
        return False
    
    def _setup_with_ytdlp(self):
        """Strategy 1: Use yt-dlp for stream setup."""
        try:
            logger.info("🧪 Trying yt-dlp strategy...")
            
            # Configure yt-dlp for live streams
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'format': 'best[height<=720]/best',  # Prefer reasonable quality
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                self.is_live = info.get('is_live', False)
                self.title = info.get('title', 'Unknown Video')
                
                # Get the best audio/video stream
                formats = info.get('formats', [])
                if formats:
                    # For live streams, find a suitable format
                    if self.is_live:
                        logger.info("📡 Processing live stream...")
                        # Look for audio-only or low-resolution streams for live
                        audio_formats = [f for f in formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
                        if audio_formats:
                            best_format = max(audio_formats, key=lambda x: x.get('abr', 0))
                            logger.info("🎵 Selected audio-only format for live stream")
                        else:
                            # Fallback to lowest resolution video
                            video_formats = [f for f in formats if f.get('height', 0) > 0]
                            if video_formats:
                                best_format = min(video_formats, key=lambda x: x.get('height', 999))
                                logger.info("📹 Selected low-resolution video format for live stream")
                            else:
                                best_format = formats[0]
                                logger.info("📺 Using fallback format for live stream")
                    else:
                        logger.info("🎞️ Processing regular video...")
                        # For regular videos, get best quality
                        best_format = formats[0]
                    
                    # Store the stream info
                    self.stream_url = best_format.get('url')
                    self.format_info = best_format
                    
                    logger.info(f"✅ yt-dlp found stream: {best_format.get('format_note', 'Unknown quality')}")
                    logger.info(f"🔴 Live stream: {self.is_live}")
                    logger.info(f"📺 Title: {self.title}")
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"❌ yt-dlp strategy failed: {e}")
            return False
    
    def _setup_with_streamlink(self):
        """Strategy 2: Use streamlink for live stream setup."""
        try:
            logger.info("🧪 Trying streamlink strategy...")
            
            # Use streamlink to get stream info
            result = subprocess.run(
                ['streamlink', '--json', self.url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                self.is_live = True  # Streamlink primarily handles live streams
                self.title = data.get('metadata', {}).get('title', 'Live Stream')
                streams = data.get('streams', {})
                
                if streams:
                    # Prefer medium quality for processing
                    preferred_qualities = ['720p', '480p', '360p', 'best']
                    selected_quality = None
                    
                    for quality in preferred_qualities:
                        if quality in streams:
                            selected_quality = quality
                            break
                    
                    if not selected_quality:
                        selected_quality = list(streams.keys())[0]
                    
                    self.stream_quality = selected_quality
                    logger.info(f"✅ Streamlink found stream: {selected_quality}")
                    logger.info(f"🎞️ Available qualities: {list(streams.keys())}")
                    logger.info(f"📺 Title: {self.title}")
                    
                    return True
            else:
                logger.warning(f"❌ Streamlink returned error: {result.stderr}")
            
            return False
            
        except Exception as e:
            logger.warning(f"❌ Streamlink strategy failed: {e}")
            return False
    
    def _setup_with_direct_extraction(self):
        """Strategy 3: Direct metadata extraction."""
        try:
            logger.info("🧪 Trying direct extraction strategy...")
            
            import requests
            
            # Simple HTTP request to check if video exists and get basic info
            response = requests.get(self.url, timeout=10)
            
            if response.status_code == 200:
                # Look for basic metadata in the page
                if 'videoDetails' in response.text:
                    # Extract title using simple parsing
                    if '"title":"' in response.text:
                        title_start = response.text.find('"title":"') + 9
                        title_end = response.text.find('"', title_start)
                        self.title = response.text[title_start:title_end]
                    
                    # Check for live stream indicators
                    self.is_live = '"isLive":true' in response.text or '"isLiveContent":true' in response.text
                    
                    logger.info(f"✅ Direct extraction successful")
                    logger.info(f"📺 Title: {self.title}")
                    logger.info(f"🔴 Live: {self.is_live}")
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"❌ Direct extraction failed: {e}")
            return False
    
    def download_audio(self, output_dir="temp_audio"):
        """Download audio from the stream using the successful strategy."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if self.successful_strategy == 'yt-dlp' and self.stream_url:
            return self._download_audio_ytdlp(output_dir)
        elif self.successful_strategy == 'streamlink' and self.stream_quality:
            return self._download_audio_streamlink(output_dir)
        else:
            logger.warning("No valid strategy available for audio download")
            return None
    
    def _download_audio_ytdlp(self, output_dir):
        """Download audio using yt-dlp."""
        try:
            logger.info("🎵 Downloading audio with yt-dlp...")
            
            output_template = os.path.join(output_dir, f"{self.video_id}.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            # Find the downloaded file
            for file in os.listdir(output_dir):
                if file.startswith(self.video_id):
                    audio_file = os.path.join(output_dir, file)
                    logger.info(f"✅ Audio downloaded: {audio_file}")
                    return audio_file
            
            return None
            
        except Exception as e:
            logger.error(f"❌ yt-dlp audio download failed: {e}")
            return None
    
    def _download_audio_streamlink(self, output_dir):
        """Download audio using streamlink."""
        try:
            logger.info("🎵 Downloading audio with streamlink...")
            
            output_file = os.path.join(output_dir, f"{self.video_id}_stream.mp4")
            
            # Use streamlink to capture stream
            result = subprocess.run([
                'streamlink',
                '--output', output_file,
                '--force',
                self.url,
                self.stream_quality
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_file):
                logger.info(f"✅ Stream captured: {output_file}")
                return output_file
            else:
                logger.error(f"❌ Streamlink capture failed: {result.stderr}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Streamlink audio capture failed: {e}")
            return None
    
    def get_info_summary(self):
        """Get a summary of the extracted stream information."""
        return {
            'video_id': self.video_id,
            'title': self.title,
            'is_live': self.is_live,
            'url': self.url,
            'strategy_used': self.successful_strategy,
            'stream_quality': getattr(self, 'stream_quality', None),
            'has_stream_url': bool(self.stream_url),
            'format_info': getattr(self, 'format_info', None)
        }
    
    def extract_audio(self, duration_seconds=30):
        """
        Extract audio from the stream (compatibility method for main processor).
        
        Args:
            duration_seconds: How long to capture audio for
            
        Returns:
            Path to the extracted audio file
        """
        logger.info(f"🎵 Extracting audio for {duration_seconds} seconds...")
        
        if self.successful_strategy == 'yt-dlp' and self.stream_url:
            return self._extract_audio_ytdlp(duration_seconds)
        elif self.successful_strategy == 'streamlink':
            return self._extract_audio_streamlink(duration_seconds)
        else:
            logger.warning("⚠️ No audio extraction method available for current strategy")
            return None
    
    def _extract_audio_ytdlp(self, duration_seconds):
        """Extract audio using yt-dlp method."""
        try:
            output_dir = "temp_audio_extraction"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_template = os.path.join(output_dir, f"{self.video_id}_%(timestamp)s.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            # For live streams, limit the duration
            if self.is_live:
                ydl_opts['external_downloader_args'] = ['-t', str(duration_seconds)]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            # Find the downloaded file
            for file in os.listdir(output_dir):
                if file.startswith(self.video_id) and file.endswith('.mp3'):
                    audio_file = os.path.join(output_dir, file)
                    logger.info(f"✅ Audio extracted: {audio_file}")
                    return audio_file
            
            logger.warning("⚠️ Audio file not found after extraction")
            return None
            
        except Exception as e:
            logger.error(f"❌ Audio extraction failed: {e}")
            return None
    
    def _extract_audio_streamlink(self, duration_seconds):
        """Extract audio using streamlink method."""
        try:
            output_dir = "temp_audio_extraction"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            output_file = os.path.join(output_dir, f"{self.video_id}_stream.mp4")
            
            # Use streamlink to capture stream for specified duration
            result = subprocess.run([
                'streamlink',
                '--output', output_file,
                '--force',
                '--retry-max', '3',
                self.url,
                self.stream_quality or 'best'
            ], capture_output=True, text=True, timeout=duration_seconds + 10)
            
            if os.path.exists(output_file):
                logger.info(f"✅ Stream captured: {output_file}")
                return output_file
            else:
                logger.warning("⚠️ Stream file not created")
                return None
            
        except subprocess.TimeoutExpired:
            logger.info(f"⏰ Stream capture timed out after {duration_seconds} seconds (expected)")
            # Check if file was created
            output_file = os.path.join("temp_audio_extraction", f"{self.video_id}_stream.mp4")
            if os.path.exists(output_file):
                return output_file
            return None
        except Exception as e:
            logger.error(f"❌ Streamlink audio capture failed: {e}")
            return None
    
    def start_video_capture(self):
        """
        Start video capture (compatibility method for main processor).
        
        Returns:
            OpenCV VideoCapture object or None if not possible
        """
        logger.info("🎥 Starting video capture...")
        
        if self.successful_strategy == 'yt-dlp' and self.stream_url:
            return self._start_video_capture_ytdlp()
        elif self.successful_strategy == 'streamlink':
            return self._start_video_capture_streamlink()
        else:
            logger.warning("⚠️ No video capture method available for current strategy")
            return None
    
    def _start_video_capture_ytdlp(self):
        """Start video capture using yt-dlp stream URL."""
        try:
            import cv2
            
            if self.stream_url:
                logger.info(f"🎥 Opening video stream with yt-dlp URL...")
                cap = cv2.VideoCapture(self.stream_url)
                
                if cap.isOpened():
                    logger.info("✅ Video capture started successfully")
                    self.cap = cap
                    return cap
                else:
                    logger.warning("⚠️ Failed to open video stream")
                    return None
            else:
                logger.warning("⚠️ No stream URL available")
                return None
            
        except Exception as e:
            logger.error(f"❌ Video capture failed: {e}")
            return None
    
    def _start_video_capture_streamlink(self):
        """Start video capture using streamlink."""
        try:
            import cv2
            
            # For streamlink, we can try to use the direct URL
            logger.info(f"🎥 Starting streamlink video capture...")
            
            # Use streamlink to get stream URL
            result = subprocess.run(
                ['streamlink', '--stream-url', self.url, self.stream_quality or 'best'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                cap = cv2.VideoCapture(stream_url)
                
                if cap.isOpened():
                    logger.info("✅ Streamlink video capture started successfully")
                    self.cap = cap
                    return cap
                else:
                    logger.warning("⚠️ Failed to open streamlink video stream")
                    return None
            else:
                logger.warning(f"⚠️ Streamlink URL extraction failed: {result.stderr}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Streamlink video capture failed: {e}")
            return None
    
    def stop_video_capture(self):
        """Stop video capture and release resources."""
        if hasattr(self, 'cap') and self.cap is not None:
            logger.info("🛑 Stopping video capture...")
            self.cap.release()
            self.cap = None
            logger.info("✅ Video capture stopped")
    
    def release(self):
        """Release all resources (compatibility method for main processor)."""
        logger.info("🛑 Releasing all enhanced stream resources...")
        self.stop_video_capture()
        
        # Clean up any temporary files
        if hasattr(self, 'audio_file') and self.audio_file and os.path.exists(self.audio_file):
            try:
                os.remove(self.audio_file)
                logger.info(f"🗑️ Cleaned up audio file: {self.audio_file}")
            except Exception as e:
                logger.warning(f"⚠️ Could not clean up audio file: {e}")
        
        logger.info("✅ Enhanced stream resources released")

# Test function
def test_enhanced_stream(video_id='uL9q9fO4g6w'):
    """Test the enhanced stream handler."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    print(f"🧪 Testing Enhanced YouTube Stream Handler")
    print(f"🎯 Video ID: {video_id}")
    print(f"🔗 URL: {url}")
    print("-" * 50)
    
    stream = EnhancedYouTubeStream(url)
    
    if stream.setup():
        info = stream.get_info_summary()
        print("✅ Stream setup successful!")
        print(f"📺 Title: {info['title']}")
        print(f"🔴 Live: {info['is_live']}")
        print(f"🔧 Strategy: {info['strategy_used']}")
        print(f"🎞️ Quality: {info['stream_quality']}")
        
        return stream
    else:
        print("❌ Stream setup failed!")
        return None

if __name__ == "__main__":
    test_enhanced_stream()
