#!/usr/bin/env python3
"""
Hybrid Picture Generator Agent for Russian ABC Poster.

This agent uses a hybrid approach:
1. DALL-E 3 generates ONLY the illustration (no text)
2. Python PIL programmatically adds perfect Cyrillic text overlay

This guarantees readable Cyrillic text while keeping AI-generated beautiful illustrations.
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Literal, Union
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import io

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HybridPictureGeneratorAgent:
    """Hybrid generator that combines AI illustrations with programmatic Cyrillic text."""
    
    def __init__(self):
        """Initialize the hybrid picture generator."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('DALLE_MODEL', 'dall-e-3')
        
        # Configure image size
        size_input = os.getenv('IMAGE_SIZE', '1024x1024')
        valid_sizes: list[Literal['256x256', '512x512', '1024x1024', '1024x1792', '1792x1024']] = [
            '256x256', '512x512', '1024x1024', '1024x1792', '1792x1024'
        ]
        self.image_size: Literal['256x256', '512x512', '1024x1024', '1024x1792', '1792x1024'] = (
            size_input if size_input in valid_sizes else '1024x1024'
        )
        
        # Setup storage
        self.storage_dir = Path(os.getenv('STORAGE_PATH', 'generated_images'))
        self._setup_storage()
    
    def _setup_storage(self) -> None:
        """Setup storage directory."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Storage directory initialized: {self.storage_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to setup storage: {e}")
            raise
    
    def validate_input(self, letter: str, word: str) -> Tuple[str, str]:
        """Validate and clean input parameters."""
        if not letter or not word:
            raise ValueError("Letter and word cannot be empty")
        
        letter = letter.strip().upper()
        word = word.strip().lower()
        
        if len(letter) != 1:
            raise ValueError("Letter must be a single character")
        
        return letter, word
    
    def generate_illustration_prompt(self, word: str) -> str:
        """Generate prompt for DALL-E 3 that focuses ONLY on illustration (no text)."""
        
        prompt = f"""
        Create a beautiful children's book illustration of {word} (Russian: {word}).
        
        CRITICAL: NO TEXT OR LETTERS IN THE IMAGE.
        
        ILLUSTRATION REQUIREMENTS:
        • Simple, clean cartoon style suitable for children
        • Bright, cheerful colors
        • Educational and child-friendly design
        • Clear, recognizable depiction of {word}
        • Professional children's book illustration quality
        • White or very light background
        • Central composition with some space around the edges
        
        ABSOLUTELY NO TEXT:
        • Do not include any letters, words, or text
        • Do not include Russian or English text
        • Focus purely on the visual illustration
        • Clean illustration without any typography
        
        Style: Modern children's educational illustration, similar to picture books.
        Reference style: Simple, cute, educational cartoon illustration.
        """
        
        return prompt.strip()
    
    def generate_illustration(self, word: str) -> str:
        """Generate illustration using DALL-E 3 (text-free)."""
        try:
            logger.info(f"🎨 Generating illustration for {word} (no text)...")
            
            prompt = self.generate_illustration_prompt(word)
            
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.image_size,
                quality="standard",
                n=1,
            )
            
            if not response.data or len(response.data) == 0:
                raise Exception("No image data received from OpenAI API")
            
            image_url = response.data[0].url
            if not image_url:
                raise Exception("No image URL received from OpenAI API")
                
            logger.info(f"✅ Illustration generated successfully for {word}")
            
            return image_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate illustration for {word}: {e}")
            raise
    
    def download_illustration(self, image_url: str, letter: str, word: str) -> Image.Image:
        """Download illustration from URL and return PIL Image."""
        try:
            logger.info(f"💾 Downloading illustration for {letter} - {word}...")
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Load image into PIL
            image = Image.open(io.BytesIO(response.content))
            
            logger.info(f"✅ Illustration downloaded successfully")
            return image
            
        except Exception as e:
            logger.error(f"❌ Failed to download illustration: {e}")
            raise
    
    def get_font_path(self, font_size: int, bold: bool = True) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        """Get appropriate font for Cyrillic text."""
        # Try to find system fonts that support Cyrillic
        possible_fonts = [
            # macOS fonts
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc", 
            "/System/Library/Fonts/Times.ttc",
            # Windows fonts
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/times.ttf",
            # Linux fonts
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        
        for font_path in possible_fonts:
            try:
                if Path(font_path).exists():
                    font = ImageFont.truetype(font_path, font_size)
                    logger.info(f"📝 Using font: {font_path}")
                    return font
            except Exception:
                continue
        
        # Fallback to default font
        logger.warning("⚠️ Using default font - Cyrillic may not display correctly")
        return ImageFont.load_default()
    
    def add_cyrillic_text_overlay(self, image: Image.Image, letter: str, word: str) -> Image.Image:
        """Add perfect Cyrillic text overlay to the illustration with simplified approach."""
        try:
            logger.info(f"📝 Adding simplified Cyrillic text overlay: {letter}/{word}")
            
            # Create a copy to work with
            img_with_text = image.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            # Get image dimensions
            img_width, img_height = img_with_text.size
            
            # Font sizes for clear readability
            letter_font_size = int(img_height * 0.12)  # 12% of image height
            word_font_size = int(img_height * 0.08)    # 8% of image height
            
            # Get fonts
            letter_font = self.get_font_path(letter_font_size, bold=True)
            word_font = self.get_font_path(word_font_size, bold=True)
            
            # Simple colors for maximum contrast
            text_color = (0, 0, 0)      # Pure black
            bg_color = (255, 255, 255)  # Pure white
            
            # Add letter at top
            letter_bbox = draw.textbbox((0, 0), letter, font=letter_font)
            letter_width = letter_bbox[2] - letter_bbox[0]
            letter_height = letter_bbox[3] - letter_bbox[1]
            
            # Position letter at top center
            letter_x = (img_width - letter_width) // 2
            letter_y = int(img_height * 0.05)  # 5% from top
            
            # Draw simple background for letter
            padding = 25
            letter_bg_coords = [
                letter_x - padding,
                letter_y - padding,
                letter_x + letter_width + padding,
                letter_y + letter_height + padding
            ]
            draw.rectangle(letter_bg_coords, fill=bg_color, outline=(0, 0, 0), width=2)
            
            # Draw letter
            draw.text((letter_x, letter_y), letter, font=letter_font, fill=text_color)
            
            # Add word at bottom
            word_bbox = draw.textbbox((0, 0), word, font=word_font)
            word_width = word_bbox[2] - word_bbox[0]
            word_height = word_bbox[3] - word_bbox[1]
            
            # Position word at bottom center
            word_x = (img_width - word_width) // 2
            word_y = int(img_height * 0.88) - word_height  # 12% from bottom
            
            # Draw simple background for word
            word_bg_coords = [
                word_x - padding,
                word_y - padding,
                word_x + word_width + padding,
                word_y + word_height + padding
            ]
            draw.rectangle(word_bg_coords, fill=bg_color, outline=(0, 0, 0), width=2)
            
            # Draw word
            draw.text((word_x, word_y), word, font=word_font, fill=text_color)
            
            logger.info(f"✅ Simplified text overlay added successfully")
            return img_with_text
            
        except Exception as e:
            logger.error(f"❌ Failed to add text overlay: {e}")
            raise
    
    def save_final_image(self, image: Image.Image, letter: str, word: str) -> Path:
        """Save the final image with text overlay."""
        try:
            filename = f"{letter}_{word}.png"
            filepath = self.storage_dir / filename
            
            # Save as PNG with high quality
            image.save(filepath, "PNG", optimize=True)
            
            logger.info(f"✅ Final image saved: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save final image: {e}")
            raise
    
    def save_metadata(self, letter: str, word: str, filepath: Path, illustration_prompt: str) -> None:
        """Save generation metadata."""
        metadata = {
            "letter": letter,
            "word": word,
            "filename": filepath.name,
            "filepath": str(filepath),
            "timestamp": datetime.now().isoformat(),
            "image_size": self.image_size,
            "model": self.model,
            "generation_method": "hybrid",
            "illustration_prompt": illustration_prompt,
            "text_overlay": "programmatic_cyrillic"
        }
        
        metadata_path = self.storage_dir / f"{letter}_{word}_metadata.json"
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"📝 Metadata saved: {metadata_path.name}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save metadata: {e}")
    
    def generate_picture(self, letter: str, word: str) -> Dict:
        """Main function to generate a picture using hybrid approach."""
        try:
            # Validate input
            valid_letter, valid_word = self.validate_input(letter, word)
            
            logger.info(f"🚀 Starting hybrid generation for {valid_letter} - {valid_word}")
            
            # Check if image already exists
            expected_filename = f"{valid_letter}_{valid_word}.png"
            expected_path = self.storage_dir / expected_filename
            
            if expected_path.exists():
                logger.info(f"⚡ Image already exists: {expected_filename}")
                return {
                    "success": True,
                    "letter": valid_letter,
                    "word": valid_word,
                    "filepath": str(expected_path),
                    "cached": True,
                    "method": "hybrid"
                }
            
            # Step 1: Generate illustration (no text)
            illustration_url = self.generate_illustration(valid_word)
            
            # Step 2: Download illustration
            illustration_image = self.download_illustration(illustration_url, valid_letter, valid_word)
            
            # Step 3: Add Cyrillic text overlay
            final_image = self.add_cyrillic_text_overlay(illustration_image, valid_letter, valid_word)
            
            # Step 4: Save final image
            filepath = self.save_final_image(final_image, valid_letter, valid_word)
            
            # Step 5: Save metadata
            illustration_prompt = self.generate_illustration_prompt(valid_word)
            self.save_metadata(valid_letter, valid_word, filepath, illustration_prompt)
            
            logger.info(f"🎉 Successfully generated hybrid picture for {valid_letter} - {valid_word}")
            
            return {
                "success": True,
                "letter": valid_letter,
                "word": valid_word,
                "filepath": str(filepath),
                "cached": False,
                "method": "hybrid",
                "illustration_generated": True,
                "text_overlay_added": True
            }
            
        except Exception as e:
            logger.error(f"💥 Hybrid generation failed for {letter} - {word}: {e}")
            
            return {
                "success": False,
                "letter": letter,
                "word": word,
                "error": str(e),
                "method": "hybrid"
            }
    
    def get_generated_pictures(self) -> list[Path]:
        """Get list of generated picture files."""
        try:
            picture_files = list(self.storage_dir.glob("*.png"))
            return picture_files
        except Exception as e:
            logger.error(f"❌ Failed to list generated pictures: {e}")
            return []
    
    def cleanup(self) -> None:
        """Clean up generated files (useful for testing or reset)."""
        try:
            for file_path in self.storage_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            logger.info("🧹 Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


def main():
    """CLI interface for the Hybrid Picture Generator Agent."""
    if len(sys.argv) < 3:
        print("Usage: python hybrid_picture_generator.py <letter> <word>")
        print("Example: python hybrid_picture_generator.py А арбуз")
        sys.exit(1)
    
    letter = sys.argv[1]
    word = sys.argv[2]
    
    try:
        agent = HybridPictureGeneratorAgent()
        result = agent.generate_picture(letter, word)
        
        if result["success"]:
            print("✅ Hybrid generation completed successfully!")
            print(f"📁 File saved: {result['filepath']}")
            print(f"🔧 Method: {result['method']}")
            if result.get("cached"):
                print("⚡ Used cached image")
            else:
                print("🎨 Generated new illustration + text overlay")
        else:
            print("❌ Hybrid generation failed!")
            print(f"💥 Error: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 