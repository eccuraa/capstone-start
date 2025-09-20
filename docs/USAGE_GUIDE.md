# YouTube Live Stream Processor - Usage Guide

This guide provides detailed instructions on how to use the YouTube Live Stream Processor to transcribe live streams, detect phrases, capture screenshots, and analyze them with Google's Gemini Vision API.

## Prerequisites

Before using this system, ensure you have:

1. Python 3.8 or higher installed
2. FFmpeg installed on your system (required for audio processing)
3. A Google Gemini API key with access to the Gemini Pro Vision API (for image analysis)
4. A Deepgram API key for high-quality speech transcription

## Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on the `.env.example` template:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file and add your Google Gemini API key and Deepgram API key

## Basic Usage

### Interactive Interface

The easiest way to use the system is through the interactive interface:

```bash
# Activate your virtual environment
source venv/bin/activate

# Run the interactive program
python cli.py
```

The program will guide you through:
1. **YouTube URL**: Simply paste your livestream or video URL
2. **Phrase Detection**: Enter keywords to detect (comma-separated)
3. **Output Directory**: Choose where to save results

### Example Session
```
🎬 La Nation - YouTube Live Stream Processor
==================================================
By Adam Ajroudi

📺 YouTube Livestream Setup
Paste your YouTube livestream or video URL below:
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

🔍 Phrase Detection Setup  
Enter phrases to detect (comma-separated):
Examples: 'breaking news,live update' or 'AI,machine learning'
Phrases: breaking news,urgent,live update

💾 Output Setup
Output directory (default: analysis_output): news_analysis

🚀 Starting Analysis...
📺 URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
🔍 Phrases: ['breaking news', 'urgent', 'live update']
💾 Output: news_analysis

Press Ctrl+C to stop processing
--------------------------------------------------
```

## Example Script

An example script is provided to demonstrate how to use the system programmatically:

```bash
python example.py
```

You can modify the example script to customize:
- The YouTube URL
- Target phrases to detect
- Output directory

## How It Works

1. **Stream Access**: The system connects to the YouTube live stream and extracts both video and audio.
2. **Transcription**: The audio is transcribed in real-time using Deepgram's AI-powered API, with Google Speech Recognition as a fallback.
3. **Phrase Detection**: The transcription is analyzed to detect specified phrases.
4. **Screenshot Capture**: When a target phrase is detected, a screenshot of the current video frame is captured.
5. **Vision Analysis**: The screenshot is analyzed using Google's Gemini Vision API, with context from the transcription.

## Output Files

The system generates the following outputs in the specified output directory:

- `screenshots/`: Directory containing captured screenshots
- `analysis_history.json`: JSON file with the history of image analyses
- `youtube_processor.log`: Log file with detailed information about the processing

## Advanced Usage

### Customizing Phrase Detection

The `PhraseDetector` class supports fuzzy matching to account for transcription errors. You can customize the detection sensitivity by modifying the `match_threshold` parameter in `phrase_detector.py`.

### Using Different Vision Models

By default, the system uses the "gemini-pro-vision" model for image analysis. You can change this by modifying the `model` parameter when initializing the `VisionAnalyzer` class.

### Customizing Transcription

The system uses Deepgram's "nova-2" model by default for transcription. You can modify the transcription options in the `_async_deepgram_transcribe` method in `transcription.py` to use different models or settings.

### Processing Regular Videos

While designed for live streams, the system can also process regular YouTube videos. It will automatically detect if the provided URL is a live stream or a regular video and adjust its behavior accordingly.

## Troubleshooting

### Common Issues

1. **FFmpeg Not Found**: Ensure FFmpeg is installed and available in your system PATH.
2. **API Key Issues**: Verify your Google Gemini and Deepgram API keys are correct and have access to the required models.
3. **Video Access Issues**: Some YouTube videos may have restrictions that prevent access.

### Logs

Check the `youtube_processor.log` file for detailed information about any errors or issues.

## Extending the System

The modular design makes it easy to extend the system:

1. **Custom Transcription**: Replace or enhance the Deepgram transcription with another service.
2. **Alternative Vision Analysis**: Implement different computer vision models or services.
3. **Additional Actions**: Add custom actions to trigger when phrases are detected.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 