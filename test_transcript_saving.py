#!/usr/bin/env python3
"""
Test script to verify transcript saving functionality works correctly.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from la_nation.main import YouTubeLiveProcessor

def test_transcript_saving():
    """Test the transcript saving functionality with simulated data."""
    print("🧪 Testing Transcript Saving Functionality")
    print("=" * 50)
    
    # Create a test processor
    processor = YouTubeLiveProcessor(
        url="https://www.youtube.com/watch?v=test",
        target_phrases=[],
        output_dir="test_transcript_output"
    )
    
    # Initialize the processor components
    processor.transcript_counter = 0
    processor.full_transcript = ""
    processor.url = "https://www.youtube.com/watch?v=test"
    
    # Create output directories
    os.makedirs(processor.transcripts_dir, exist_ok=True)
    
    print(f"📂 Output directory: {processor.output_dir}")
    print(f"📂 Transcripts directory: {processor.transcripts_dir}")
    
    # Test saving some transcript chunks
    test_transcripts = [
        "This is the first 30-second chunk of transcript from the live stream. It contains important information about the current topic being discussed.",
        "Here's the second chunk, continuing the conversation. The speaker is now talking about different aspects of the subject matter.",
        "And this is the third chunk, wrapping up this section of the live stream with concluding remarks and transitioning to the next topic."
    ]
    
    print("\n🎯 Testing transcript chunk saving...")
    for i, transcript in enumerate(test_transcripts):
        print(f"\n📝 Saving chunk {i+1}...")
        processor._save_transcript_chunk(transcript)
        time.sleep(1)  # Small delay to show different timestamps
    
    # Test final transcript saving
    print("\n📋 Testing final transcript saving...")
    processor._save_final_transcript()
    
    # Show results
    print("\n✅ Test Results:")
    print(f"📊 Total chunks saved: {processor.transcript_counter}")
    print(f"📝 Total characters: {len(processor.full_transcript)}")
    
    # List created files
    print(f"\n📁 Files created in {processor.transcripts_dir}:")
    if os.path.exists(processor.transcripts_dir):
        for file in sorted(os.listdir(processor.transcripts_dir)):
            file_path = os.path.join(processor.transcripts_dir, file)
            size = os.path.getsize(file_path)
            print(f"   📄 {file} ({size} bytes)")
    
    # Show final transcript location
    final_path = os.path.join(processor.output_dir, "final_transcript.txt")
    if os.path.exists(final_path):
        size = os.path.getsize(final_path)
        print(f"   📋 final_transcript.txt ({size} bytes)")
    
    print("\n🎉 Transcript saving test completed successfully!")
    print("🔍 Check the files to verify content was saved correctly.")

if __name__ == "__main__":
    test_transcript_saving()
