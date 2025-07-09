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
from typing import Dict, Literal
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
        
        # Cost optimization settings (configurable via environment variables)
        image_size_str = os.getenv('IMAGE_SIZE', '1024x1024')  # Options: 1024x1024, 1024x1536, 1536x1024, auto
        image_quality_str = os.getenv('IMAGE_QUALITY', 'high')  # Options: high, medium, low, auto
        
        # Define valid literal types (based on actual gpt-image-1 API)
        valid_sizes = ['1024x1024', '1024x1536', '1536x1024', 'auto']
        valid_qualities = ['high', 'medium', 'low', 'auto']
        
        # Validate and set size
        if image_size_str in valid_sizes:
            self.image_size: Literal['1024x1024', '1024x1536', '1536x1024', 'auto'] = image_size_str  # type: ignore
        else:
            logger.warning(f"⚠️ Invalid IMAGE_SIZE '{image_size_str}', using default '1024x1024'")
            self.image_size = '1024x1024'
            
        # Validate and set quality  
        if image_quality_str in valid_qualities:
            self.image_quality: Literal['high', 'medium', 'low', 'auto'] = image_quality_str  # type: ignore
        else:
            logger.warning(f"⚠️ Invalid IMAGE_QUALITY '{image_quality_str}', using default 'high'")
            self.image_quality = 'high'
        
        # Log cost optimization settings
        logger.info(f"💰 Cost settings: {self.image_size} @ {self.image_quality} quality")
        
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
            
            BACKGROUND REQUIREMENTS:
            • MUST have clean WHITE or very light cream background
            • NO dark or black backgrounds
            • Bright, cheerful, child-friendly appearance
            • Light background for educational flashcard style
            
            EXTREME MARGIN ENFORCEMENT - ABSOLUTELY NO CUTOFF ALLOWED:
            • MANDATORY: Leave 40% completely empty white space at the very top
            • MANDATORY: Leave 40% completely empty white space at the very bottom
            • The letter "{valid_letter}" must be positioned FAR FROM the top edge
            • The word "{valid_word}" must be positioned FAR FROM the bottom edge
            • Position letter "{valid_letter}" starting at 40% down from the top edge minimum
            • Position word "{valid_word}" ending at 40% up from the bottom edge minimum
            • All text must be MICROSCOPIC to ensure complete containment
            • NEVER let any part of any letter touch or approach any edge
            
            ULTRA-EXTREME LAYOUT ZONES - RIGID BOUNDARIES:
            • TOP MARGIN (0%-40%): Absolutely EMPTY white space - ZERO content
            • LETTER ZONE (40%-50%): Letter "{valid_letter}" centered, MICROSCOPIC size
            • ILLUSTRATION ZONE (50%-50%): Tiny illustration of {valid_word}
            • WORD ZONE (50%-60%): Word "{valid_word}" centered, MICROSCOPIC size
            • BOTTOM MARGIN (60%-100%): Absolutely EMPTY white space - ZERO content
            
            TEXT SIZING - MAKE TEXT INCREDIBLY SMALL:
            • Make letter "{valid_letter}" MICROSCOPIC - smaller than you think possible
            • Make word "{valid_word}" MICROSCOPIC - smaller than you think possible
            • Text should be so small it's almost hard to see but still readable
            • Better to have barely visible text than ANY cutoff whatsoever
            • Prioritize ZERO cutoff over ALL other considerations including readability
            • Text must look tiny and be positioned well within the center zones
            
            POSITIONING RULES - ABSOLUTE CONSTRAINTS:
            • Letter "{valid_letter}": Must be completely within 40%-50% zone with generous padding
            • Word "{valid_word}": Must be completely within 50%-60% zone with generous padding
            • Enormous empty space above letter (40% of entire image height)
            • Enormous empty space below word (40% of entire image height)
            • Text should appear very small and safely positioned in center of image
            • NO part of any text should ever approach the edges
            
            REPETITIVE SAFETY INSTRUCTIONS:
            • DO NOT let "{valid_letter}" touch the top edge
            • DO NOT let "{valid_word}" touch the bottom edge
            • Keep text EXTREMELY small
            • Keep text positioned in the CENTER of the image
            • Leave MASSIVE margins on all sides
            • Make text so small that cutoff is impossible
            
            VISUAL STYLE:
            • Clean WHITE background (not black!)
            • Bright, colorful text (red, blue, or similar bright colors)
            • IMPORTANT: Letter "{valid_letter}" must be ONE SINGLE COLOR
            • Simple, child-friendly illustration of {valid_word} in center
            • High contrast dark text on light background
            • Educational flashcard appearance
            • Ultra-microscopic text sizing throughout
            
            FINAL ABSOLUTE REQUIREMENTS:
            • WHITE background only
            • 40% clear margin at top (ABSOLUTELY NO EXCEPTIONS)
            • 40% clear margin at bottom (ABSOLUTELY NO EXCEPTIONS)
            • Text so small it's guaranteed to fit within bounds
            • Never allow text to approach any edge whatsoever
            • Bright, child-friendly educational style
            
            Generate with EXTREME caution - ZERO tolerance for any cutoff. Make the text TINY and position it in the CENTER.
            """
            
            # Generate with gpt-image-1
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=self.image_size,
                quality=self.image_quality
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