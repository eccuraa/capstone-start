#!/usr/bin/env python3
"""
Interactive CLI for La Nation YouTube Live Stream Processor.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header():
    """Print the application header."""
    print()
    print("🎬 La Nation - YouTube Live Stream Processor")
    print("=" * 50)
    print("By Adam Ajroudi")
    print()

def get_youtube_url():
    """Get and validate YouTube URL from user."""
    print("📺 STEP 1: YouTube URL")
    print("Paste your YouTube livestream or video URL below:")
    print("Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print()
    
    while True:
        url = input("YouTube URL: ").strip()
        
        if not url:
            print("❌ Error: URL cannot be empty!")
            continue
        
        # Basic URL validation
        if "youtube.com" in url or "youtu.be" in url:
            return url
        else:
            print("⚠️  Warning: This doesn't look like a YouTube URL")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm == 'y':
                return url
            print("Please enter a valid YouTube URL.")

def get_phrases():
    """Get phrases to detect from user."""
    print("\n🔍 STEP 2: Phrase Detection (Optional)")
    print("Enter keywords to detect, separated by commas:")
    print("Examples:")
    print("  • For news: 'breaking news,urgent,live update'")
    print("  • For tech: 'AI,machine learning,artificial intelligence'")
    print("  • For sports: 'goal,touchdown,winner'")
    print("  • Leave empty to skip phrase detection")
    print()
    
    phrases_input = input("Phrases: ").strip()
    
    if phrases_input:
        target_phrases = [p.strip() for p in phrases_input.split(",") if p.strip()]
        print(f"✅ Will detect: {', '.join(target_phrases)}")
        return target_phrases
    else:
        print("📝 Skipping phrase detection")
        return []

def get_output_dir():
    """Get output directory from user."""
    print("\n💾 STEP 3: Output Location")
    default_dir = "livestream_analysis"
    output_dir = input(f"Save results to (default: {default_dir}): ").strip()
    
    if not output_dir:
        output_dir = default_dir
    
    print(f"✅ Results will be saved to: {output_dir}")
    return output_dir

def start_processing(url, target_phrases, output_dir):
    """Start the YouTube processing."""
    print("\n🚀 STARTING ANALYSIS")
    print("=" * 30)
    print(f"📺 Video: {url}")
    print(f"🔍 Detecting: {target_phrases if target_phrases else 'No phrases'}")
    print(f"💾 Output: {output_dir}")
    print()
    print("⚡ Starting processor... (Press Ctrl+C to stop)")
    print("-" * 50)
    
    try:
        # Import and run the processor
        from la_nation import YouTubeLiveProcessor
        
        processor = YouTubeLiveProcessor(
            url=url,
            target_phrases=target_phrases,
            output_dir=output_dir
        )
        
        processor.start()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Processing stopped by user")
        print("Results saved to:", output_dir)
    except ImportError as e:
        print(f"\n\n❌ Import Error: {str(e)}")
        print("\n💡 This might be due to missing audio dependencies.")
        print("The core APIs work - check tests with: python tests/test_apis.py")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        print("\n💡 Troubleshooting Tips:")
        print("- Ensure API keys are set in .env file")
        print("- Check if the YouTube URL is accessible")
        print("- Try a different video if this one is private/restricted")
        print("- Run 'python tests/test_apis.py' to verify setup")

def main():
    """Main interactive CLI function."""
    try:
        print_header()
        
        # Step 1: Get YouTube URL
        url = get_youtube_url()
        
        # Step 2: Get phrases to detect
        target_phrases = get_phrases()
        
        # Step 3: Get output directory
        output_dir = get_output_dir()
        
        # Step 4: Start processing
        start_processing(url, target_phrases, output_dir)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except EOFError:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()
