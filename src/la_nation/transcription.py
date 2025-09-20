import os
import time
import wave
import threading
import queue
import logging
import tempfile
import asyncio
import requests
import speech_recognition as sr
from pydub import AudioSegment
import pyaudio
from dotenv import load_dotenv
# Import Deepgram SDK with fallback to HTTP for Python 3.12 compatibility
DEEPGRAM_SDK_AVAILABLE = False
try:
    from deepgram import (
        DeepgramClient,
        PrerecordedOptions,
        FileSource,
    )
    # Test if we can actually instantiate the client to catch typing.Union errors
    test_key = "test"
    test_client = DeepgramClient(test_key)
    # Force HTTP API for Python 3.12 compatibility
    import sys
    if sys.version_info >= (3, 12):
        DEEPGRAM_SDK_AVAILABLE = False
        print("🔄 Python 3.12+ detected: Forcing Deepgram HTTP API for compatibility")
    else:
        DEEPGRAM_SDK_AVAILABLE = True
        print("✅ Deepgram SDK loaded and tested successfully")
except Exception as e:
    DEEPGRAM_SDK_AVAILABLE = False
    print(f"⚠️ Deepgram SDK not available (using HTTP fallback): {e}")
    # Import requests for HTTP fallback

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up Deepgram API key
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


class LiveTranscriber:
    def __init__(self, audio_file=None, chunk_duration=5):
        """
        Initialize the transcriber.
        
        Args:
            audio_file: Path to the audio file to transcribe (for non-live mode)
            chunk_duration: Duration of each audio chunk in seconds
        """
        self.audio_file = audio_file
        self.chunk_duration = chunk_duration
        self.recognizer = sr.Recognizer()  # Keep for fallback
        self.transcript_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.is_live = audio_file is not None
        self.current_transcript = ""
        
        # Initialize Deepgram client
        if DEEPGRAM_API_KEY:
            self.deepgram = DeepgramClient(DEEPGRAM_API_KEY)
            self.use_deepgram = True
        else:
            logger.warning(
                "Deepgram API key not found. Falling back to Google Speech."
            )
            self.use_deepgram = False
        
    def start_live_transcription(self):
        """Start transcribing audio in real-time."""
        threading.Thread(target=self._process_audio_stream, daemon=True).start()
        
    def _process_audio_stream(self):
        """Process the audio stream in chunks."""
        try:
            if self.audio_file and os.path.exists(self.audio_file):
                # Process existing audio file
                self._process_file()
            else:
                # Process microphone input
                self._process_microphone()
        except Exception as e:
            logger.error(f"Error in audio processing: {str(e)}")
            
    def _process_file(self):
        """Process an audio file in chunks."""
        try:
            # Load the audio file
            audio = AudioSegment.from_file(self.audio_file)
            chunk_size_ms = self.chunk_duration * 1000
            
            # Process the audio in chunks
            for i in range(0, len(audio), chunk_size_ms):
                if self.stop_event.is_set():
                    break
                    
                # Extract a chunk
                chunk = audio[i:i+chunk_size_ms]
                
                # Save the chunk to a temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.wav'
                )
                chunk.export(temp_file.name, format="wav")
                temp_file.close()
                
                # Transcribe the chunk
                transcript = self._transcribe_audio_file(temp_file.name)
                
                if transcript:
                    self.current_transcript += " " + transcript
                    self.transcript_queue.put(transcript)
                
                # Clean up
                os.unlink(temp_file.name)
                
                # Simulate real-time processing
                time.sleep(self.chunk_duration / 2)
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            
    def _process_microphone(self):
        """Process microphone input in real-time."""
        # Set up PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=1024)
        
        frames = []
        start_time = time.time()
        
        try:
            while not self.stop_event.is_set():
                # Read audio data
                data = stream.read(1024)
                frames.append(data)
                
                # Check if we've reached the chunk duration
                if time.time() - start_time >= self.chunk_duration:
                    # Save the audio chunk to a temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False, suffix='.wav'
                    )
                    temp_file.close()
                    
                    # Write the WAV file
                    with wave.open(temp_file.name, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(16000)
                        wf.writeframes(b''.join(frames))
                    
                    # Transcribe the chunk
                    transcript = self._transcribe_audio_file(temp_file.name)
                    
                    if transcript:
                        self.current_transcript += " " + transcript
                        self.transcript_queue.put(transcript)
                    
                    # Clean up
                    os.unlink(temp_file.name)
                    
                    # Reset for the next chunk
                    frames = []
                    start_time = time.time()
        finally:
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()
            
    def _transcribe_audio_file(self, audio_file):
        """
        Transcribe an audio file using Deepgram API or fallback to Google.
        
        Args:
            audio_file: Path to the audio file to transcribe
            
        Returns:
            The transcribed text
        """
        if self.use_deepgram:
            return self._transcribe_with_deepgram(audio_file)
        else:
            return self._transcribe_with_google(audio_file)
    
    def _transcribe_with_deepgram(self, audio_file):
        """
        Transcribe using Deepgram API (with HTTP fallback for Python 3.12 compatibility).
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            if DEEPGRAM_SDK_AVAILABLE:
                # Use SDK if available
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self._async_deepgram_transcribe(audio_file)
                )
                loop.close()
                return result
            else:
                # Use HTTP fallback for Python 3.12 compatibility
                return self._transcribe_with_deepgram_http(audio_file)
        except Exception as e:
            logger.error(f"Deepgram transcription error: {str(e)}")
            # Fall back to Google if Deepgram fails
            return self._transcribe_with_google(audio_file)
    
    def _transcribe_with_deepgram_http(self, audio_file):
        """
        Transcribe using Deepgram HTTP API (Python 3.12 compatible).
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            logger.info("🌐 Using Deepgram HTTP API (Python 3.12 compatible)")
            
            url = "https://api.deepgram.com/v1/listen"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/mpeg"
            }
            
            # Read the audio file
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            # Make the API request
            response = requests.post(
                url,
                headers=headers,
                data=audio_data,
                params={
                    'model': 'nova-2',
                    'smart_format': 'true',
                    'punctuate': 'true'
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
                logger.info(f"✅ Deepgram HTTP transcription successful: {len(transcript)} characters")
                return transcript
            else:
                logger.error(f"❌ Deepgram HTTP API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Deepgram HTTP transcription failed: {e}")
            return ""
    
    async def _async_deepgram_transcribe(self, audio_file):
        """
        Async function to call Deepgram API.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            # Configure options
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                language="en",
                punctuate=True
            )
            
            # Open the audio file
            with open(audio_file, "rb") as file:
                buffer_data = file.read()
            
            # Send to Deepgram
            source = FileSource(buffer=buffer_data)
            response = await self.deepgram.listen.prerecorded.v("1").transcribe_file(
                source, options
            )
            
            # Extract transcript
            if response and response.results:
                transcript = response.results.channels[0].alternatives[0].transcript
                return transcript
            return None
        except Exception as e:
            logger.error(f"Deepgram transcription error: {str(e)}")
            return None
    
    def _transcribe_with_google(self, audio_file):
        """
        Fallback transcription using Google's Speech Recognition API.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            with sr.AudioFile(audio_file) as source:
                # Record audio from the file
                audio_data = self.recognizer.record(source)
                
                # Use Google's Speech Recognition API
                transcript = self.recognizer.recognize_google(audio_data)
                
            return transcript
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(
                f"Could not request results from Google Speech Recognition: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Error transcribing audio with Google: {str(e)}")
            return None
            
    def get_transcript(self):
        """Get the latest transcript chunk."""
        try:
            return self.transcript_queue.get_nowait()
        except queue.Empty:
            return None
            
    def get_full_transcript(self):
        """Get the full transcript so far."""
        return self.current_transcript
        
    def stop(self):
        """Stop the transcription process."""
        self.stop_event.set() 