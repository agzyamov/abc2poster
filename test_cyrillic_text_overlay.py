#!/usr/bin/env python3
"""
Simple test to verify Cyrillic text rendering and OCR recognition.
Creates a plain white image with Cyrillic text to test the fundamentals.
"""

from PIL import Image, ImageDraw, ImageFont
import pytesseract
from pathlib import Path

def test_basic_cyrillic_rendering():
    """Test basic Cyrillic text rendering and OCR."""
    print("🧪 Testing basic Cyrillic text rendering...")
    
    # Create a simple white image
    img = Image.new('RGB', (1024, 1024), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to get a good font
    font_paths = [
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    
    font = None
    for font_path in font_paths:
        try:
            if Path(font_path).exists():
                font = ImageFont.truetype(font_path, 120)  # Large size
                print(f"✅ Using font: {font_path}")
                break
        except Exception:
            continue
    
    if font is None:
        font = ImageFont.load_default()
        print("⚠️ Using default font")
    
    # Add Cyrillic text
    letter = "Г"
    word = "гриб"
    
    # Draw letter at top
    draw.text((400, 100), letter, font=font, fill='black')
    
    # Draw word at bottom
    draw.text((350, 800), word, font=font, fill='black')
    
    # Save test image
    test_file = Path("cyrillic_test.png")
    img.save(test_file)
    print(f"💾 Saved test image: {test_file}")
    
    # Run OCR
    print("🔍 Running OCR on test image...")
    
    try:
        detected_text = pytesseract.image_to_string(
            img, lang='rus+eng', config='--psm 6'
        ).strip()
        
        detected_lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
        
        print(f"📝 OCR detected: {detected_lines}")
        
        # Check results
        full_text = detected_text.upper()
        letter_found = letter.upper() in full_text
        word_found = word.upper() in full_text
        
        print(f"🔤 Letter {letter} found: {'✅' if letter_found else '❌'} {letter_found}")
        print(f"📝 Word {word} found: {'✅' if word_found else '❌'} {word_found}")
        
        if letter_found and word_found:
            print("🎉 SUCCESS: Basic Cyrillic rendering works!")
            return True
        else:
            print("❌ FAILED: Basic Cyrillic rendering has issues")
            return False
            
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        return False

def test_font_cyrillic_support():
    """Test which fonts properly support Cyrillic."""
    print("\n🔤 Testing font Cyrillic support...")
    
    test_fonts = [
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Times.ttc",
    ]
    
    for font_path in test_fonts:
        if not Path(font_path).exists():
            continue
            
        try:
            font = ImageFont.truetype(font_path, 100)
            
            # Create test image
            img = Image.new('RGB', (512, 256), color='white')
            draw = ImageDraw.Draw(img)
            
            # Test Cyrillic text
            test_text = "Г гриб АБВ"
            draw.text((50, 100), test_text, font=font, fill='black')
            
            # Test OCR
            detected = pytesseract.image_to_string(img, lang='rus').strip()
            
            # Check if any Cyrillic was detected
            cyrillic_found = any(0x0400 <= ord(char) <= 0x04FF for char in detected)
            
            print(f"Font {Path(font_path).name}: {'✅' if cyrillic_found else '❌'} - OCR: {detected}")
            
        except Exception as e:
            print(f"Font {Path(font_path).name}: ❌ Error: {e}")

if __name__ == "__main__":
    print("🇷🇺 CYRILLIC TEXT RENDERING TEST")
    print("=" * 50)
    
    # Test basic rendering
    basic_works = test_basic_cyrillic_rendering()
    
    # Test font support
    test_font_cyrillic_support()
    
    print(f"\n🎯 CONCLUSION:")
    if basic_works:
        print("✅ Basic Cyrillic rendering works - hybrid approach should succeed")
        print("🔧 Issue might be in the overlay implementation")
    else:
        print("❌ Basic Cyrillic rendering fails - font/OCR issue detected")
        print("🔧 Need to fix fundamental text rendering first") 