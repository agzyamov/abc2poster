#!/usr/bin/env python3
"""
Picture Generator Agent - Agent 1
Generates individual letter pictures using OpenAI's DALL-E API.
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple, Literal
from datetime import datetime

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PictureGeneratorAgent:
    """Agent responsible for generating individual letter pictures."""
    
    def __init__(self):
        """Initialize the Picture Generator Agent."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.storage_dir = Path(os.getenv('STORAGE_PATH', './generated_images'))
        
        # Validate image size to be one of the accepted values
        size_input = os.getenv('IMAGE_SIZE', '1024x1024')
        valid_sizes: list[Literal['256x256', '512x512', '1024x1024', '1024x1792', '1792x1024']] = [
            '256x256', '512x512', '1024x1024', '1024x1792', '1792x1024'
        ]
        self.image_size: Literal['256x256', '512x512', '1024x1024', '1024x1792', '1792x1024'] = (
            size_input if size_input in valid_sizes else '1024x1024'  # type: ignore
        )
        
        self.model = os.getenv('DALLE_MODEL', 'dall-e-3')
        
        self._setup_storage()
    
    def _setup_storage(self) -> None:
        """Create storage directory if it doesn't exist."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Storage directory initialized: {self.storage_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize storage directory: {e}")
            raise
    
    def validate_input(self, letter: str, word: str) -> Tuple[str, str]:
        """
        Validate input parameters.
        
        Args:
            letter: The letter (A-Z)
            word: The word starting with the letter
            
        Returns:
            Tuple of (normalized_letter, normalized_word)
            
        Raises:
            ValueError: If input is invalid
        """
        if not isinstance(letter, str) or not letter:
            raise ValueError("Letter must be a valid string")
        
        if not isinstance(word, str) or not word:
            raise ValueError("Word must be a valid string")
        
        normalized_letter = letter.upper().strip()
        normalized_word = word.lower().strip()
        
        if len(normalized_letter) != 1 or not normalized_letter.isalpha():
            raise ValueError("Letter must be a single alphabetic character")
        
        # For Russian, check if word starts with the letter (case-insensitive)
        if not normalized_word.startswith(normalized_letter.lower()):
            raise ValueError(f"Word '{word}' must start with letter '{letter}'")
        
        return normalized_letter, normalized_word
    
    def generate_prompt(self, letter: str, word: str) -> str:
        """
        Generate a prompt for DALL-E image generation.
        
        Args:
            letter: The capital Cyrillic letter
            word: The Russian word to illustrate
            
        Returns:
            Formatted prompt string
        """
        return f"""Create a Russian educational alphabet card exactly like this style: a card with colored border, large letter at top, illustration in middle, and word at bottom.

EXACT LAYOUT REQUIRED (copy this style):

CARD STRUCTURE:
- Colored border frame around the entire card
- Card has a warm, child-friendly color scheme
- Square format with rounded corners

TOP SECTION (header):
- Large Cyrillic capital letter "{letter}" in bold, dark font
- Letter sits on a colored background strip at the top
- Letter should be very large and clearly readable

MIDDLE SECTION (main area - largest part):
- Large, cute cartoon illustration of a {word}
- Clean, simple cartoon style like children's books
- Bright colors on light/white background
- Illustration should fill most of the middle space
- Style similar to: drum with drumsticks, cute wolf character, red mushroom

BOTTOM SECTION (footer):
- Russian word "{word}" in clear Cyrillic letters
- Word sits on a colored background strip at the bottom
- Text should be bold and easily readable

VISUAL STYLE REQUIREMENTS:
- Copy the exact style from examples: Б/барабан (drum), В/волк (wolf), Г/гриб (mushroom)
- Simple, clean cartoon illustrations
- Warm, educational color palette
- Clear contrast between text and backgrounds
- Child-friendly, approachable design
- Professional educational card quality

CRITICAL: The letter "{letter}" and word "{word}" MUST be clearly visible with good contrast against their colored background sections."""
    
    def generate_image(self, letter: str, word: str) -> str:
        """
        Generate an image using OpenAI's DALL-E API.
        
        Args:
            letter: The letter to generate for
            word: The word to illustrate
            
        Returns:
            URL of the generated image
            
        Raises:
            Exception: If image generation fails
        """
        try:
            logger.info(f"🎨 Generating image for {letter} - {word}...")
            
            prompt = self.generate_prompt(letter, word)
            
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
                
            logger.info(f"✅ Image generated successfully for {letter} - {word}")
            
            return image_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate image for {letter} - {word}: {e}")
            raise
    
    def download_and_save_image(self, image_url: str, letter: str, word: str) -> Path:
        """
        Download and save image from URL to local storage.
        
        Args:
            image_url: The URL of the generated image
            letter: The letter for filename
            word: The word for filename
            
        Returns:
            Path to the saved image file
            
        Raises:
            Exception: If download or save fails
        """
        filename = f"{letter}_{word}.png"
        filepath = self.storage_dir / filename
        
        try:
            logger.info(f"💾 Downloading and saving image to: {filepath}")
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Image saved successfully: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Failed to save image for {letter} - {word}: {e}")
            # Clean up incomplete file
            if filepath.exists():
                filepath.unlink()
            raise
    
    def save_metadata(self, letter: str, word: str, filepath: Path) -> None:
        """
        Save generation metadata.
        
        Args:
            letter: The letter
            word: The word
            filepath: Path to saved image
        """
        metadata = {
            "letter": letter,
            "word": word,
            "filename": filepath.name,
            "filepath": str(filepath),
            "timestamp": datetime.now().isoformat(),
            "image_size": self.image_size,
            "model": self.model
        }
        
        metadata_path = self.storage_dir / f"{letter}_{word}_metadata.json"
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"📝 Metadata saved: {metadata_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save metadata: {e}")
    
    def validate_generated_image(self, filepath: Path, letter: str, word: str) -> Dict:
        """
        Validate generated image using OCR and basic checks.
        
        Args:
            filepath: Path to the generated image
            letter: Expected letter
            word: Expected word
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        ocr_results = {"detected_text": [], "letter_found": False, "word_found": False}
        
        try:
            # Check if file exists and has reasonable size
            if not filepath.exists():
                issues.append("Image file does not exist")
                return {"valid": False, "issues": issues, "ocr": ocr_results}
            
            file_size = filepath.stat().st_size
            if file_size < 10000:  # Less than 10KB is probably too small
                issues.append(f"Image file too small ({file_size} bytes)")
            elif file_size > 5000000:  # More than 5MB is probably too large
                issues.append(f"Image file very large ({file_size} bytes)")
            
            # Basic image format validation
            try:
                from PIL import Image
                with Image.open(filepath) as img:
                    width, height = img.size
                    if width < 100 or height < 100:
                        issues.append(f"Image dimensions too small: {width}x{height}")
                    if abs(width - height) > min(width, height) * 0.2:  # Not roughly square
                        issues.append(f"Image not square: {width}x{height}")
            except ImportError:
                logger.warning("PIL not available for image validation")
            except Exception as e:
                issues.append(f"Cannot open image: {e}")
            
            # OCR Validation using Tesseract
            try:
                import pytesseract
                from PIL import Image
                
                logger.info(f"🔍 Running OCR on {filepath.name}...")
                
                # Open image for OCR
                with Image.open(filepath) as img:
                    # Try OCR with Russian and English
                    detected_text = pytesseract.image_to_string(
                        img, 
                        lang='rus+eng',  # Russian + English
                        config='--psm 6'  # Treat as single uniform block
                    ).strip()
                
                # Clean and process detected text
                detected_lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
                ocr_results["detected_text"] = detected_lines
                
                # Log all detected text
                if detected_lines:
                    logger.info(f"📝 OCR detected text lines: {detected_lines}")
                else:
                    logger.warning(f"❌ OCR found no readable text in {filepath.name}")
                
                # Check for expected letter and word in detected text
                full_text_upper = detected_text.upper()
                
                # Check for expected letter
                if letter.upper() in full_text_upper:
                    ocr_results["letter_found"] = True
                    logger.info(f"✅ Found expected letter '{letter}' in OCR text")
                
                # Check for expected word (case-insensitive)
                if word.upper() in full_text_upper:
                    ocr_results["word_found"] = True
                    logger.info(f"✅ Found expected word '{word}' in OCR text")
                
                # Check for missing expected text
                if not ocr_results["letter_found"]:
                    issues.append(f"Expected letter '{letter}' not detected by OCR")
                    logger.warning(f"❌ Letter '{letter}' not found in: {detected_text}")
                
                if not ocr_results["word_found"]:
                    issues.append(f"Expected word '{word}' not detected by OCR")
                    logger.warning(f"❌ Word '{word}' not found in: {detected_text}")
                
                # Success message
                if ocr_results["letter_found"] and ocr_results["word_found"]:
                    logger.info(f"🎉 OCR validation passed: found both '{letter}' and '{word}'")
                
            except ImportError:
                logger.warning("⚠️ pytesseract not available - skipping text validation")
                issues.append("OCR validation skipped (pytesseract not available)")
            except Exception as e:
                logger.warning(f"⚠️ OCR validation failed: {e}")
                issues.append(f"OCR validation error: {e}")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "file_size": file_size,
                "ocr": ocr_results,
                "layout_check_needed": not (ocr_results["letter_found"] and ocr_results["word_found"])
            }
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
            return {"valid": False, "issues": issues, "ocr": ocr_results}
    
    def improve_prompt_based_on_ocr_failure(self, letter: str, word: str, ocr_result: Dict, attempt: int) -> str:
        """
        Generate an improved prompt based on OCR validation failures.
        
        Args:
            letter: The target letter
            word: The target word
            ocr_result: OCR validation results
            attempt: Current attempt number (1-based)
            
        Returns:
            Improved prompt string
        """
        base_improvements = []
        
        # Analyze OCR failure patterns
        if not ocr_result["letter_found"]:
            base_improvements.extend([
                f"CRITICAL: The letter '{letter}' MUST be clearly visible and readable",
                f"Place a giant, bold '{letter}' character at the very top with high contrast",
                f"Use thick, black '{letter}' on bright colored background"
            ])
        
        if not ocr_result["word_found"]:
            base_improvements.extend([
                f"CRITICAL: The word '{word}' MUST be clearly visible and readable",
                f"Place '{word}' in large, bold Cyrillic letters at the bottom",
                f"Use high contrast colors for the word '{word}' - black text on bright background"
            ])
        
        # Progressive improvements based on attempt number
        if attempt == 2:
            intensity_level = "EXTREMELY IMPORTANT"
            additional_requirements = [
                "Use maximum text contrast - black text on white/bright backgrounds",
                "Make text significantly larger than before",
                "Ensure text is the main focus, not decorative elements"
            ]
        elif attempt == 3:
            intensity_level = "ABSOLUTELY CRITICAL"
            additional_requirements = [
                "Text must be ENORMOUS and impossible to miss",
                "Use only black text on pure white backgrounds for maximum readability",
                "Minimize decorative elements that might interfere with text recognition",
                "Focus on text clarity over artistic beauty"
            ]
        else:
            intensity_level = "IMPORTANT"
            additional_requirements = ["Ensure clear, readable text placement"]
        
        # Build improved prompt
        improved_prompt = f"""
        {intensity_level}: Create a Russian educational card with PERFECT TEXT VISIBILITY (Attempt {attempt}/3).

        Previous OCR attempt detected: {ocr_result.get('detected_text', [])}
        But failed to find: {letter if not ocr_result['letter_found'] else ''} {word if not ocr_result['word_found'] else ''}

        MANDATORY TEXT REQUIREMENTS:
        {chr(10).join('- ' + req for req in base_improvements)}
        {chr(10).join('- ' + req for req in additional_requirements)}

        CARD STRUCTURE (copy reference examples exactly):
        TOP: Large Cyrillic letter "{letter}" - black, bold, huge font on colored background
        MIDDLE: Cute illustration of {word} (simple, clean cartoon style)
        BOTTOM: Russian word "{word}" - black, bold, large font on colored background

        CRITICAL SUCCESS CRITERIA:
        - OCR must be able to read letter "{letter}" clearly
        - OCR must be able to read word "{word}" clearly
        - Use fonts that OCR can easily recognize
        - Maximum contrast between text and background
        - Text size should be at least 20% of image height for each text element

        Style: Bright, child-friendly, educational card with colored border frame.
        Reference: Б/барабан, В/волк, Г/гриб examples with clear text visibility.
        """
        
        return improved_prompt.strip()
    
    def generate_picture_with_adaptive_improvement(self, letter: str, word: str, max_attempts: int = 3) -> Dict:
        """
        Generate picture with adaptive prompt improvement based on OCR validation.
        
        Args:
            letter: The target letter
            word: The target word
            max_attempts: Maximum number of generation attempts
            
        Returns:
            Dictionary containing generation result
        """
        try:
            # Validate input
            valid_letter, valid_word = self.validate_input(letter, word)
            
            logger.info(f"🚀 Starting adaptive generation for {valid_letter} - {valid_word}")
            
            # Check if image already exists
            expected_filename = f"{valid_letter}_{valid_word}.png"
            expected_path = self.storage_dir / expected_filename
            
            if expected_path.exists():
                logger.info(f"⚡ Image already exists: {expected_filename}")
                # Still validate existing image
                validation_result = self.validate_generated_image(expected_path, valid_letter, valid_word)
                return {
                    "success": True,
                    "letter": valid_letter,
                    "word": valid_word,
                    "filepath": str(expected_path),
                    "cached": True,
                    "validation": validation_result,
                    "attempts_used": 0
                }
            
            last_validation = None
            filepath = None
            
            for attempt in range(1, max_attempts + 1):
                logger.info(f"🎯 Generation attempt {attempt}/{max_attempts} for {valid_letter} - {valid_word}")
                
                try:
                    # Generate improved prompt if this is a retry
                    if attempt == 1:
                        # Use original prompt for first attempt
                        image_url = self.generate_image(valid_letter, valid_word)
                    else:
                        # Use improved prompt based on previous OCR failure
                        if last_validation is None:
                            # Fallback to original prompt if no previous validation
                            image_url = self.generate_image(valid_letter, valid_word)
                        else:
                            improved_prompt = self.improve_prompt_based_on_ocr_failure(
                                valid_letter, valid_word, last_validation["ocr"], attempt
                            )
                            logger.info(f"🔧 Using improved prompt for attempt {attempt}")
                            image_url = self.generate_image_with_custom_prompt(valid_letter, valid_word, improved_prompt)
                    
                    # Download and save image (overwrite previous attempt)
                    filepath = self.download_and_save_image(image_url, valid_letter, valid_word)
                    
                    # Validate the generated image
                    validation_result = self.validate_generated_image(filepath, valid_letter, valid_word)
                    last_validation = validation_result
                    
                    # Check if validation passed
                    if validation_result["valid"] and validation_result["ocr"]["letter_found"] and validation_result["ocr"]["word_found"]:
                        logger.info(f"🎉 SUCCESS! Generated perfect picture for {valid_letter} - {valid_word} in {attempt} attempts")
                        
                        # Save successful metadata
                        metadata = {
                            "letter": valid_letter,
                            "word": valid_word,
                            "filename": filepath.name,
                            "filepath": str(filepath),
                            "timestamp": datetime.now().isoformat(),
                            "image_size": self.image_size,
                            "model": self.model,
                            "attempts_used": attempt,
                            "ocr_validation": "passed",
                            "adaptive_improvement": "success"
                        }
                        
                        metadata_path = self.storage_dir / f"{valid_letter}_{valid_word}_metadata.json"
                        with open(metadata_path, 'w') as f:
                            json.dump(metadata, f, indent=2)
                        
                        return {
                            "success": True,
                            "letter": valid_letter,
                            "word": valid_word,
                            "filepath": str(filepath),
                            "cached": False,
                            "validation": validation_result,
                            "attempts_used": attempt,
                            "improvement_applied": attempt > 1
                        }
                    
                    else:
                        # Log what went wrong and continue to next attempt
                        missing = []
                        if not validation_result["ocr"]["letter_found"]:
                            missing.append(f"letter '{valid_letter}'")
                        if not validation_result["ocr"]["word_found"]:
                            missing.append(f"word '{valid_word}'")
                        
                        logger.warning(f"❌ Attempt {attempt} failed: OCR could not detect {', '.join(missing)}")
                        logger.warning(f"📄 OCR detected instead: {validation_result['ocr']['detected_text']}")
                        
                        if attempt < max_attempts:
                            logger.info(f"🔄 Retrying with improved prompt...")
                        else:
                            logger.warning(f"⚠️ Max attempts ({max_attempts}) reached, keeping best result")
                
                except Exception as e:
                    logger.error(f"💥 Attempt {attempt} failed with error: {e}")
                    if attempt == max_attempts:
                        raise
                    continue
            
            # If we get here, all attempts failed but we have the last result
            if last_validation and filepath is not None:
                # Save final metadata even if not perfect
                self.save_metadata(valid_letter, valid_word, filepath)
                
                return {
                    "success": True,  # File was generated, even if not perfect
                    "letter": valid_letter,
                    "word": valid_word,
                    "filepath": str(filepath),
                    "cached": False,
                    "validation": last_validation,
                    "attempts_used": max_attempts,
                    "improvement_applied": True,
                    "warning": f"Generated image after {max_attempts} attempts but OCR validation still has issues"
                }
            
            raise Exception("All generation attempts failed")
            
        except Exception as e:
            logger.error(f"💥 Adaptive generation failed for {letter} - {word}: {e}")
            
            return {
                "success": False,
                "letter": letter,
                "word": word,
                "error": str(e),
                "attempts_used": 0
            }
    
    def generate_image_with_custom_prompt(self, letter: str, word: str, custom_prompt: str) -> str:
        """
        Generate image with a custom prompt instead of the default one.
        
        Args:
            letter: The letter to generate for
            word: The word to illustrate  
            custom_prompt: Custom prompt to use
            
        Returns:
            URL of the generated image
        """
        try:
            logger.info(f"🎨 Generating image with custom prompt for {letter} - {word}...")
            
            response = self.client.images.generate(
                model=self.model,
                prompt=custom_prompt,
                size=self.image_size,
                quality="standard",
                n=1,
            )
            
            if not response.data or len(response.data) == 0:
                raise Exception("No image data received from OpenAI API")
            
            image_url = response.data[0].url
            if not image_url:
                raise Exception("No image URL received from OpenAI API")
                
            logger.info(f"✅ Image generated with custom prompt for {letter} - {word}")
            
            return image_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate image with custom prompt for {letter} - {word}: {e}")
            raise

    def generate_picture(self, letter: str, word: str) -> Dict:
        """
        Main function to generate a picture for a letter-word pair.
        Now uses adaptive improvement by default.
        
        Args:
            letter: The letter (A-Z)
            word: The word starting with the letter
            
        Returns:
            Dictionary containing generation result with filepath and metadata
        """
        return self.generate_picture_with_adaptive_improvement(letter, word)
    
    def get_generated_pictures(self) -> list[Path]:
        """
        Get list of generated picture files.
        
        Returns:
            List of paths to generated picture files
        """
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
    """CLI interface for the Picture Generator Agent."""
    if len(sys.argv) < 3:
        print("Usage: python picture_generator.py <letter> <word>")
        print("Example: python picture_generator.py A apple")
        sys.exit(1)
    
    letter = sys.argv[1]
    word = sys.argv[2]
    
    try:
        agent = PictureGeneratorAgent()
        result = agent.generate_picture(letter, word)
        
        if result["success"]:
            print("✅ Generation completed successfully!")
            print(f"📁 File saved: {result['filepath']}")
            if result.get("cached"):
                print("⚡ Used cached image")
        else:
            print("❌ Generation failed!")
            print(f"💥 Error: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 