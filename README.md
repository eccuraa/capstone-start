# La Nation - YouTube Live Stream Processor

A sophisticated AI-powered system that processes YouTube videos, transcribes audio in real-time, detects specific phrases, and analyzes visual content using advanced machine learning APIs.

## 🚀 Features

- **🎵 Audio Transcription**: Real-time audio transcription using Deepgram's advanced AI API
- **🔍 Phrase Detection**: Intelligent detection of specified phrases in transcriptions
- **📸 Screenshot Capture**: Automatic screenshot capture when target phrases are detected
- **🤖 AI Vision Analysis**: Advanced image analysis using Google's Gemini Vision API
- **📊 Contextual Analysis**: Links visual content to transcript context for enhanced insights
- **🎬 YouTube Integration**: Seamless integration with YouTube videos and streams

## 📋 Requirements

- **Python 3.8+**
- **Google Gemini API Key** (for vision analysis)
- **Deepgram API Key** (for audio transcription)

### ⚠️ **Audio Processing Requirements**
For live audio streaming, additional system dependencies are required:
- **FFmpeg** (for audio/video processing)
- **PortAudio** (for real-time audio)
- **PyAudio** (Python audio library)

**Note:** Core functionality (phrase detection, vision analysis) works without these dependencies.

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "La Nation"
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Google Gemini API Key for vision analysis
GEMINI_API_KEY=your_gemini_api_key_here

# Deepgram API Key for transcription
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# YouTube Data API v3 Key for enhanced stream access
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

## 🔑 Getting API Keys

### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### Deepgram API Key
1. Sign up at [Deepgram](https://deepgram.com/) (get $200 free credits)
2. Create a new project
3. Generate an API key
4. Copy the key to your `.env` file

### YouTube Data API v3 Key
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing one
3. Enable "YouTube Data API v3"
4. Go to Credentials → Create Credentials → API Key
5. Copy the key to your `.env` file

## 🎯 Usage

### Interactive Interface (Recommended)

**🎯 Simple 3-Step Process:**

```bash
# Activate virtual environment
source venv/bin/activate

# Run the interactive interface
python cli.py
```

**The program will prompt you for:**
1. 📺 **YouTube URL** - Paste your livestream or video URL
2. 🔍 **Phrases to detect** - Enter keywords separated by commas, or **press Enter** to skip
3. 💾 **Output directory** - Choose folder name, or **press Enter** for default (`livestream_analysis`)

**💡 Pro Tip:** You can press Enter for steps 2 and 3 to use defaults!

**Example interaction:**
```
🎬 La Nation - YouTube Live Stream Processor
==================================================
By Adam Ajroudi

📺 STEP 1: YouTube URL
Paste your YouTube livestream or video URL below:
YouTube URL: https://www.youtube.com/watch?v=jNQXAC9IVRw

🔍 STEP 2: Phrase Detection (Optional)
Enter keywords to detect, separated by commas:
Examples:
  • For news: 'breaking news,urgent,live update'
  • For tech: 'AI,machine learning,artificial intelligence'
  • Leave empty to skip phrase detection

Phrases:                                    # Just press Enter to skip
📝 Skipping phrase detection

💾 STEP 3: Output Location
Save results to (default: livestream_analysis):    # Just press Enter for default
✅ Results will be saved to: livestream_analysis

🚀 STARTING ANALYSIS
📺 Video: https://www.youtube.com/watch?v=jNQXAC9IVRw
⚡ Starting processor... (Press Ctrl+C to stop)
💾 Saved transcript chunk 1: 618 characters
💾 Saved transcript chunk 2: 540 characters
[Continues every 30 seconds until stopped]
```

**🔧 Key Features:**
- ✅ **Continuous Processing**: Extracts and transcribes 30-second chunks infinitely
- ✅ **Live Stream Support**: Works with YouTube live streams and regular videos  
- ✅ **Multiple Strategies**: Automatically tries yt-dlp, Streamlink, and YouTube API
- ✅ **Auto-Save**: All transcripts saved automatically to organized files
- ✅ **Easy Defaults**: Just press Enter to skip optional settings
- ⚠️ **Screenshots**: Video analysis feature (work in progress)

### Advanced Usage (Python Script)
For automation or custom integration:

```python
import sys
import os
sys.path.append('src')
from la_nation import YouTubeLiveProcessor

# Configure processor
processor = YouTubeLiveProcessor(
    url="https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    target_phrases=["keyword1", "keyword2", "keyword3"],
    output_dir="analysis_output"
)

# Start processing
processor.start()
```

## 🧪 Testing

### Quick Start Test
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run the interactive interface
python cli.py

# 3. Paste any YouTube URL when prompted
# Example: https://www.youtube.com/watch?v=8jPQjjsBbIc
```

### Test Individual Components
```bash
# Test API connections
python tests/test_apis.py

# Test Deepgram transcription
python tests/test_deepgram_http.py

# Test Gemini vision analysis  
python tests/test_gemini.py
```

## 📁 Project Structure

```
La Nation/
├── README.md                   # This file
├── LICENSE                     # Academic Research License
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── cli.py                     # Interactive command line interface
│
├── src/
│   └── la_nation/             # Main package
│       ├── __init__.py        # Package initialization
│       ├── main.py            # Main application entry point
│       ├── enhanced_youtube_stream.py # Enhanced YouTube handling
│       ├── transcription.py   # Audio transcription logic
│       ├── phrase_detector.py # Phrase detection algorithms
│       ├── screenshot_capturer.py # Image capture functionality
│       └── vision_analyzer.py # AI-powered image analysis
│
├── examples/
│   └── example.py             # Usage example
│
├── tests/
│   ├── test_apis.py           # API connectivity tests
│   ├── test_deepgram_http.py  # Deepgram API tests
│   ├── test_gemini.py         # Gemini API tests
│   └── data/                  # Test data files
│
└── docs/
    └── USAGE_GUIDE.md         # Detailed usage guide
```

## 📂 Output Directories

When you run **La Nation**, it creates organized output directories containing all analysis results:

### 🎯 **Main Output Structure**
```
your_output_directory/          # Named by you during setup
├── screenshots/                # 📸 Screenshots captured during analysis
│   ├── screenshot_001.png     # Timestamped screenshots
│   ├── screenshot_002.png     # When target phrases detected
│   └── ...
├── analysis_history.json      # 📊 Complete analysis log
└── transcripts/               # 📝 Audio transcriptions (if available)
    ├── segment_001.txt        # Transcribed audio segments
    ├── segment_002.txt        # With timestamps
    └── ...
```

### 🔍 **Additional Temporary Files**
```
temp_audio_extraction/         # 🎵 Temporary audio processing
├── video_id_timestamp.mp3    # Extracted audio files
├── video_id_timestamp_transcript.txt  # Individual transcripts
└── ...
```

### 💡 **Finding Your Results**

**Default Output Location:** `livestream_analysis/` (if you don't specify)

**Custom Output:** Whatever name you provide during setup

**Key Files to Check:**
- 📝 **Transcripts**: `your_output/transcripts/` or `temp_audio_extraction/*_transcript.txt`
- 📸 **Screenshots**: `your_output/screenshots/`
- 📊 **Analysis Log**: `your_output/analysis_history.json`

### ⚠️ **Important Notes**
- Output directories are automatically created during processing
- Temporary files in `temp_audio_extraction/` contain immediate results
- All output directories are excluded from git (see `.gitignore`)
- Results persist between runs for further analysis
- **Screenshots/Video Analysis**: This feature is currently work in progress

### ⏰ **Processing Timeline**
- **Initial Setup**: 5-15 seconds (depending on video type)
- **First Transcript**: Available after ~30 seconds
- **Continuous Processing**: New transcript every 30 seconds
- **Stopping**: Press `Ctrl+C` anytime to stop and save final results

## 🔧 Troubleshooting

### Common Issues

**ModuleNotFoundError**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**API Key Errors**
- Verify API keys are correctly set in `.env`
- Check API key permissions and quotas
- Ensure no extra spaces in API key values

**YouTube Access Issues**
- Some videos may be region-restricted
- Private videos require different access methods
- Try with public, educational content first

**Audio Processing Issues**
- **Live Audio Streaming**: Requires `pyaudio` and system audio libraries
- **Deepgram SDK**: Has typing compatibility issues with Python 3.12+
- **Workaround**: Use HTTP-based Deepgram API (see `tests/test_deepgram_http.py`)
- Ensure the YouTube video has audio
- Try with shorter videos first for testing

### Performance Tips

- **For Large Videos**: Use `--chunk-duration` to process in smaller segments
- **Memory Usage**: Set appropriate output directory with sufficient space
- **Rate Limits**: Respect API rate limits, especially during development

## 📄 License

This project is licensed under the **Academic Research License**. 

- ✅ **Educational Use**: Free for academic coursework and research
- ✅ **Collaboration**: Share freely with classmates and researchers  
- ❌ **Commercial Use**: Commercial usage requires separate licensing

See [LICENSE](LICENSE) for full terms.

## 🤝 Contributing

This is a capstone project. For academic collaboration:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For academic collaboration or questions:
- Create an issue in the repository
- Include relevant error messages and system information
- Specify Python version and operating system

---

**🎓 Capstone Project**: Advanced AI-powered media processing system combining speech recognition, natural language processing, and computer vision for intelligent content analysis. 