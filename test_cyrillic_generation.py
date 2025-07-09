#!/usr/bin/env python3
"""
Test script for GPT-4.1 Cyrillic text generation capabilities.
"""

import sys
import requests
from pathlib import Path
from .hybrid_picture_generator import HybridPictureGeneratorAgent
from PIL import Image
import io

def test_cyrillic_generation(letter: str, word: str):
    """Test GPT-4.1's ability to generate Cyrillic text in images."""
    print(f"🧪 Testing Cyrillic text generation for {letter} - {word}")
    
    # Initialize agent
    agent = HybridPictureGeneratorAgent()
    
    try:
        # Test Cyrillic text generation
        image_url = agent.test_cyrillic_text_generation(letter, word)
        
        # Download and save the test image
        print(f"💾 Downloading test image...")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Save test image
        test_filename = f"cyrillic_test_{letter}_{word}.png"
        test_path = Path("generated_images") / test_filename
        
        image = Image.open(io.BytesIO(response.content))
        image.save(test_path, "PNG")
        
        print(f"✅ Cyrillic test image saved: {test_filename}")
        print(f"📁 Path: {test_path}")
        
        return test_path
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

def main():
    """Run Cyrillic text generation tests."""
    if len(sys.argv) < 3:
        print("Usage: python test_cyrillic_generation.py <letter> <word>")
        print("Example: python test_cyrillic_generation.py А арбуз")
        sys.exit(1)
    
    letter = sys.argv[1]
    word = sys.argv[2]
    
    result = test_cyrillic_generation(letter, word)
    
    if result:
        print(f"\n🎉 Test completed! Check the generated image to see how well GPT-4.1 handled Cyrillic text generation.")
        print(f"🔍 Compare with our programmatic text overlay approach to see the difference.")
    else:
        print(f"\n💥 Test failed!")

if __name__ == "__main__":
    main() 