#!/usr/bin/env python3
"""
GPT-Image-1 Picture Generator Agent for Russian ABC Poster.

This agent uses OpenAI's latest gpt-image-1 model for direct generation
of Russian alphabet cards with Cyrillic text and illustrations.
"""

import os
import sys
import json
import logging
import requests
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GPTImage1PictureGeneratorAgent:
    """GPT-Image-1 generator for Russian alphabet cards with direct Cyrillic text generation."""
    
    def __init__(self):
        """Initialize the GPT-Image-1 picture generator."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
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
    
    def validate_input(self, letter: str, word: str) -> tuple[str, str]:
        """Validate and clean input parameters."""
        if not letter or not word:
            raise ValueError("Letter and word cannot be empty")
        
        letter = letter.strip().upper()
        word = word.strip().lower()
        
        if len(letter) != 1:
            raise ValueError("Letter must be a single character")
        
        return letter, word
    
    def generate_picture(self, letter: str, word: str) -> Dict:
        """Generate Russian alphabet card using gpt-image-1 model."""
        try:
            # Validate input
            valid_letter, valid_word = self.validate_input(letter, word)
            
            logger.info(f"🚀 Starting gpt-image-1 generation for {valid_letter} - {valid_word}")
            
            # Create detailed prompt for gpt-image-1
            prompt = f"""
            Create a children's educational Russian alphabet flashcard for "{valid_letter}" and "{valid_word}".
            
            CRITICAL MARGIN REQUIREMENTS:
            • MASSIVE margins: 20% empty space at top, 20% empty space at bottom
            • Letter "{valid_letter}" must start at least 20% down from the top edge
            • Word "{valid_word}" must end at least 20% up from the bottom edge
            • All text elements must be completely inside the image frame
            • Use smaller text sizes to ensure everything fits with margins
            
            SAFE LAYOUT ZONES:
            • TOP MARGIN (0%-20%): Completely empty white space
            • LETTER ZONE (20%-35%): Letter "{valid_letter}" centered, smaller size but readable
            • ILLUSTRATION ZONE (35%-65%): Beautiful illustration of {valid_word}
            • WORD ZONE (65%-80%): Word "{valid_word}" centered, smaller size but readable  
            • BOTTOM MARGIN (80%-100%): Completely empty white space
            
            TEXT SIZING STRATEGY:
            • Make letter "{valid_letter}" SMALLER to ensure it fits completely in its zone
            • Make word "{valid_word}" SMALLER to ensure it fits completely in its zone
            • Better to have smaller readable text than large cut-off text
            • Prioritize complete visibility over large size
            
            POSITIONING RULES:
            • Center letter "{valid_letter}" horizontally and within its 15% height zone
            • Center word "{valid_word}" horizontally and within its 15% height zone
            • Leave abundant space above letter and below word
            • No text should extend beyond its allocated zone
            
            VISUAL STYLE:
            • Clean, simple design with generous white space
            • Bright, cheerful colors for text and illustration
            • Simple illustration of {valid_word} (елка/tree) in center
            • High contrast between text and background
            
            FINAL SAFETY CHECK:
            • Ensure 20% clear margin at top and bottom
            • Verify all text is completely contained
            • Use conservative sizing for guaranteed fit
            
            Generate with extreme caution to avoid ANY text cutoff.
            """
            
            # Generate with gpt-image-1
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024",
                quality="high"
            )
            
            if not response.data or len(response.data) == 0:
                raise Exception("No image data received from gpt-image-1")
            
            # Handle base64 response
            if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                image_data = response.data[0].b64_json
                image_bytes = base64.b64decode(image_data)
                logger.info(f"✅ gpt-image-1 generated image with base64 data")
            elif hasattr(response.data[0], 'url') and response.data[0].url:
                # Handle URL response (fallback)
                image_url = response.data[0].url
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                image_bytes = img_response.content
                logger.info(f"✅ gpt-image-1 generated image with URL")
            else:
                raise Exception("No image data or URL received from gpt-image-1")
            
            # Save the image
            image = Image.open(io.BytesIO(image_bytes))
            filename = f"{valid_letter}_{valid_word}.png"
            filepath = self.storage_dir / filename
            image.save(filepath, "PNG")
            
            # Save metadata
            self.save_metadata(valid_letter, valid_word, filepath, prompt)
            
            logger.info(f"🎉 Successfully generated picture for {valid_letter} - {valid_word}")
            
            return {
                "success": True,
                "letter": valid_letter,
                "word": valid_word,
                "filepath": str(filepath),
                "method": "gpt-image-1",
                "model": "gpt-image-1"
            }
            
        except Exception as e:
            logger.error(f"💥 Generation failed for {letter} - {word}: {e}")
            
            return {
                "success": False,
                "letter": letter,
                "word": word,
                "error": str(e),
                "method": "gpt-image-1"
            }
    
    def save_metadata(self, letter: str, word: str, filepath: Path, prompt: str) -> None:
        """Save generation metadata."""
        metadata = {
            "letter": letter,
            "word": word,
            "filename": filepath.name,
            "filepath": str(filepath),
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-image-1",
            "prompt": prompt
        }
        
        metadata_path = self.storage_dir / f"{letter}_{word}_metadata.json"
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"📝 Metadata saved: {metadata_path.name}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save metadata: {e}")
    
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
    """CLI interface for the GPT-Image-1 Picture Generator Agent."""
    if len(sys.argv) < 3:
        print("Usage: python hybrid_picture_generator.py <letter> <word>")
        print("Example: python hybrid_picture_generator.py А арбуз")
        print()
        print("Uses OpenAI's gpt-image-1 model for direct generation of Russian alphabet cards")
        sys.exit(1)
    
    letter = sys.argv[1]
    word = sys.argv[2]
    
    try:
        agent = GPTImage1PictureGeneratorAgent()
        result = agent.generate_picture(letter, word)
        
        if result["success"]:
            print("✅ Generation completed successfully!")
            print(f"📁 File saved: {result['filepath']}")
            print(f"🔧 Model: {result['model']}")
            print("🎨 Generated directly with gpt-image-1")
        else:
            print("❌ Generation failed!")
            print(f"💥 Error: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 