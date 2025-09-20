#!/usr/bin/env python3
"""
Enhanced YouTube API Handler with multiple fallback strategies
Based on YouTube Data API v3 best practices
"""

import os
import time
import logging
import subprocess
import tempfile
from typing import Optional, Dict, Any, List
import yt_dlp
import streamlink
import requests
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

class YouTubeAPIHandler:
    """
    Multi-strategy YouTube handler that tries different approaches
    to overcome API restrictions and access limitations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube_service = None
        self.setup_youtube_service()
        
    def setup_youtube_service(self):
        """Setup YouTube Data API v3 service if API key is available."""
        if self.api_key:
            try:
                self.youtube_service = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("✅ YouTube Data API v3 service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize YouTube API: {e}")
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get comprehensive video information using multiple strategies."""
        info = {
            'id': video_id,
            'is_live': False,
            'title': '',
            'description': '',
            'status': 'unknown',
            'stream_url': None,
            'audio_url': None,
            'strategy_used': None
        }
        
        # Strategy 1: YouTube Data API v3 (Most reliable)
        if self.youtube_service:
            try:
                api_info = self._get_info_via_api(video_id)
                if api_info:
                    info.update(api_info)
                    info['strategy_used'] = 'youtube_data_api'
                    return info
            except Exception as e:
                logger.warning(f"API strategy failed: {e}")
        
        # Strategy 2: yt-dlp with enhanced options
        try:
            ytdlp_info = self._get_info_via_ytdlp(video_id)
            if ytdlp_info:
                info.update(ytdlp_info)
                info['strategy_used'] = 'yt_dlp_enhanced'
                return info
        except Exception as e:
            logger.warning(f"yt-dlp strategy failed: {e}")
        
        # Strategy 3: Streamlink for live streams
        try:
            streamlink_info = self._get_info_via_streamlink(video_id)
            if streamlink_info:
                info.update(streamlink_info)
                info['strategy_used'] = 'streamlink'
                return info
        except Exception as e:
            logger.warning(f"Streamlink strategy failed: {e}")
        
        # Strategy 4: Alternative extractors
        try:
            alt_info = self._get_info_via_alternatives(video_id)
            if alt_info:
                info.update(alt_info)
                info['strategy_used'] = 'alternative_extractor'
                return info
        except Exception as e:
            logger.warning(f"Alternative strategy failed: {e}")
        
        info['strategy_used'] = 'none_successful'
        return info
    
    def _get_info_via_api(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Strategy 1: Use YouTube Data API v3 for metadata."""
        try:
            # Get video details
            response = self.youtube_service.videos().list(
                part='snippet,liveStreamingDetails,status',
                id=video_id
            ).execute()
            
            if not response['items']:
                return None
            
            video = response['items'][0]
            snippet = video['snippet']
            
            info = {
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'is_live': 'liveStreamingDetails' in video,
                'status': 'available'
            }
            
            # Check for live streaming details
            if 'liveStreamingDetails' in video:
                live_details = video['liveStreamingDetails']
                info['is_live'] = True
                info['live_status'] = live_details.get('actualStartTime') is not None
                
                # Try to get live stream URL using alternative methods
                info['stream_url'] = self._extract_live_stream_url(video_id)
            
            logger.info(f"✅ Successfully got video info via YouTube API: {info['title']}")
            return info
            
        except Exception as e:
            logger.error(f"YouTube API error: {e}")
            return None
    
    def _get_info_via_ytdlp(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Strategy 2: Enhanced yt-dlp with multiple configurations."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Try different yt-dlp configurations
        configs = [
            # Standard configuration
            {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            },
            # Configuration for live streams
            {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'live_from_start': True,
                'wait_for_video': (1, 10),
            },
            # Configuration with different extractor
            {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
            }
        ]
        
        for i, config in enumerate(configs):
            try:
                with yt_dlp.YoutubeDL(config) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    result = {
                        'title': info.get('title', ''),
                        'description': info.get('description', ''),
                        'is_live': info.get('is_live', False),
                        'status': 'available'
                    }
                    
                    # Get best audio format
                    formats = info.get('formats', [])
                    audio_formats = [f for f in formats if f.get('acodec') != 'none']
                    if audio_formats:
                        best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
                        result['audio_url'] = best_audio.get('url')
                    
                    logger.info(f"✅ Successfully extracted via yt-dlp config {i+1}: {result['title']}")
                    return result
                    
            except Exception as e:
                logger.warning(f"yt-dlp config {i+1} failed: {e}")
                continue
        
        return None
    
    def _get_info_via_streamlink(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Strategy 3: Use Streamlink for live stream access."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            # Use streamlink to get available streams
            result = subprocess.run(
                ['streamlink', '--json', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                info = {
                    'title': data.get('metadata', {}).get('title', ''),
                    'is_live': True,  # Streamlink primarily handles live streams
                    'status': 'available',
                    'stream_url': url  # Streamlink can handle this URL
                }
                
                logger.info(f"✅ Successfully detected stream via Streamlink: {info['title']}")
                return info
                
        except Exception as e:
            logger.warning(f"Streamlink extraction failed: {e}")
        
        return None
    
    def _get_info_via_alternatives(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Strategy 4: Use alternative methods and extractors."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Try youtube-dl as fallback
        try:
            result = subprocess.run(
                ['youtube-dl', '--dump-json', '--no-warnings', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                info = {
                    'title': data.get('title', ''),
                    'description': data.get('description', ''),
                    'is_live': data.get('is_live', False),
                    'status': 'available'
                }
                
                logger.info(f"✅ Successfully extracted via youtube-dl: {info['title']}")
                return info
                
        except Exception as e:
            logger.warning(f"youtube-dl extraction failed: {e}")
        
        return None
    
    def _extract_live_stream_url(self, video_id: str) -> Optional[str]:
        """Extract live stream URL using various methods."""
        # This would implement advanced stream URL extraction
        # For now, return the basic YouTube URL
        return f"https://www.youtube.com/watch?v={video_id}"
    
    def get_working_test_videos(self) -> List[Dict[str, str]]:
        """Get a list of test videos that are known to work."""
        return [
            {
                'url': 'https://www.youtube.com/watch?v=Ks-_Mh1QhMc',
                'title': 'Sample Video 1',
                'type': 'regular'
            },
            {
                'url': 'https://www.youtube.com/watch?v=21X5lGlDOfg',
                'title': 'NASA Live Stream',
                'type': 'live'
            },
            {
                'url': 'https://www.youtube.com/watch?v=w_Ma8oQLmSM',
                'title': 'Lofi Study Stream',
                'type': 'live'
            }
        ]

# Test function
def test_youtube_handler():
    """Test the YouTube handler with different strategies."""
    handler = YouTubeAPIHandler()
    
    test_videos = [
        'uZkaJ3e9nfY',  # User's live stream
        'dQw4w9WgXcQ',  # Rick Roll (reliable test video)
        'Ks-_Mh1QhMc',  # Another test video
    ]
    
    for video_id in test_videos:
        print(f"\n🧪 Testing video ID: {video_id}")
        info = handler.get_video_info(video_id)
        print(f"📊 Strategy used: {info['strategy_used']}")
        print(f"📺 Title: {info['title']}")
        print(f"🔴 Is Live: {info['is_live']}")
        print(f"✅ Status: {info['status']}")
        
        if info['strategy_used'] != 'none_successful':
            print(f"✅ SUCCESS with {info['strategy_used']}")
            break
    
    return info

if __name__ == "__main__":
    test_youtube_handler()
