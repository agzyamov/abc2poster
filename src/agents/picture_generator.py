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
        Generate a prompt for DALL-E image generation with ultra-specific Cyrillic character instructions.
        
        Args:
            letter: The Russian letter to feature
            word: The Russian word starting with the letter
            
        Returns:
            Detailed prompt for DALL-E 3 with pixel-level Cyrillic specifications
        """
        
        # Ultra-specific Cyrillic character pixel descriptions
        pixel_descriptions = {
            'Г': '''Russian letter Г: Vertical line on left, horizontal line at top (like upside-down L)
                    EXACT SHAPE: |‾ (vertical bar with horizontal line on top-right only)
                    NOT: L, T, F, or any Latin letter''',
            'А': '''Russian letter А: Two diagonal lines meeting at top, horizontal crossbar in middle
                    EXACT SHAPE: /\\\ with horizontal line through middle
                    Similar to English A but wider at top''',
            'Б': '''Russian letter Б: Vertical line on left, horizontal line at top, curved bottom part
                    EXACT SHAPE: Like number 6 but with top horizontal line
                    NOT English B (which has two bumps)''',
            'В': '''Russian letter В: Vertical line on left, two horizontal bumps (upper smaller than lower)
                    EXACT SHAPE: Similar to English B but different proportions
                    Upper bump smaller, lower bump larger''',
            'Д': '''Russian letter Д: Triangle shape with two legs extending below
                    EXACT SHAPE: Like upside-down U with extended legs
                    Base extends beyond the triangle''',
            'Е': '''Russian letter Е: Exactly identical to English letter E
                    EXACT SHAPE: Vertical line with three horizontal lines (top, middle, bottom)''',
            'Ж': '''Russian letter Ж: Like asterisk or three lines crossing at center
                    EXACT SHAPE: * but with straight lines, like ><|
                    Three lines meeting at center point''',
            'З': '''Russian letter З: Exactly like English number 3
                    EXACT SHAPE: Two curves opening to the left
                    Like backwards C stacked''',
            'И': '''Russian letter И: Like backwards English N
                    EXACT SHAPE: Two vertical lines connected by diagonal (bottom-left to top-right)
                    Mirror image of English N''',
            'К': '''Russian letter К: Exactly identical to English letter K
                    EXACT SHAPE: Vertical line with two diagonal lines meeting at middle''',
            'Л': '''Russian letter Л: Like upside-down V with small feet
                    EXACT SHAPE: /\\ but with small horizontal extensions at bottom
                    Like lambda (λ) but upright''',
            'М': '''Russian letter М: Exactly identical to English letter M
                    EXACT SHAPE: Two vertical lines connected by inverted V at top''',
            'Н': '''Russian letter Н: Exactly identical to English letter H
                    EXACT SHAPE: Two vertical lines connected by horizontal crossbar''',
            'О': '''Russian letter О: Exactly identical to English letter O
                    EXACT SHAPE: Perfect circle or oval''',
            'П': '''Russian letter П: Like Greek Pi (π) but squared
                    EXACT SHAPE: Two vertical lines connected by horizontal line at top
                    Like upside-down U but with sharp corners''',
            'Р': '''Russian letter Р: Exactly identical to English letter P
                    EXACT SHAPE: Vertical line with horizontal bump at top''',
            'С': '''Russian letter С: Exactly identical to English letter C
                    EXACT SHAPE: Circle with opening on right side''',
            'Т': '''Russian letter Т: Exactly identical to English letter T
                    EXACT SHAPE: Horizontal line at top with vertical line down the center''',
            'У': '''Russian letter У: Like English letter Y
                    EXACT SHAPE: Two diagonal lines meeting at center, continuing down as single line''',
            'Ф': '''Russian letter Ф: Circle with vertical line through center
                    EXACT SHAPE: O with | through middle, like Φ (phi)
                    Line extends above and below circle''',
            'Х': '''Russian letter Х: Exactly identical to English letter X
                    EXACT SHAPE: Two diagonal lines crossing at center''',
            'Ц': '''Russian letter Ц: Like Russian И but with small tail at bottom-right
                    EXACT SHAPE: И + small horizontal line at bottom-right corner''',
            'Ч': '''Russian letter Ч: Like number 4
                    EXACT SHAPE: Vertical line on right, horizontal line connecting to shorter vertical on left''',
            'Ш': '''Russian letter Ш: Like English W but with straight vertical lines
                    EXACT SHAPE: Three vertical lines connected by horizontal line at bottom
                    NOT curved like English W''',
            'Щ': '''Russian letter Щ: Like Ш but with small tail at bottom-right
                    EXACT SHAPE: Ш + small horizontal line extending right from bottom-right''',
            'Ъ': '''Russian letter Ъ (hard sign): Like lowercase b with horizontal line
                    EXACT SHAPE: Vertical line + horizontal line + small curve at bottom''',
            'Ы': '''Russian letter Ы: Like bl connected together
                    EXACT SHAPE: Vertical line, gap, then vertical line with small curve (like ь)''',
            'Ь': '''Russian letter Ь (soft sign): Like small lowercase b
                    EXACT SHAPE: Vertical line with small horizontal line and curve at bottom''',
            'Э': '''Russian letter Э: Like backwards C with horizontal line through middle
                    EXACT SHAPE: Backwards C + horizontal line through center''',
            'Ю': '''Russian letter Ю: Like letters I and O connected
                    EXACT SHAPE: Vertical line connected to circle by horizontal line''',
            'Я': '''Russian letter Я: Like backwards English R
                    EXACT SHAPE: Mirror image of English R, opens to the left'''
        }
        
        # Get specific pixel description for this letter
        char_description = pixel_descriptions.get(letter, f'Russian letter {letter}')
        
        prompt = f"""
        Create a Russian children's educational alphabet card.

        🚨 CRITICAL CHARACTER SPECIFICATIONS:

        LETTER "{letter}" REQUIREMENTS:
        {char_description}
        
        FONT SPECIFICATIONS FOR "{letter}":
        • Use basic Arial or Times New Roman style
        • Completely BLACK color (#000000) on WHITE background
        • Size: ENORMOUS - takes up 25% of image height  
        • Placement: TOP CENTER of image
        • NO artistic styling, NO decorations, NO shadows
        • Shape must be EXACTLY as described above

        WORD "{word}" REQUIREMENTS:
        • Each letter must be perfect standard Russian Cyrillic
        • Completely BLACK color (#000000) on WHITE background
        • Font: Basic sans-serif (Arial/Helvetica style)
        • Size: LARGE - takes up 15% of image height
        • Placement: BOTTOM CENTER of image
        • Perfect letter spacing for readability

        ILLUSTRATION REQUIREMENTS:
        • Simple, clean illustration of {word} in center
        • Child-friendly cartoon style
        • Bright colors for the illustration only
        • NO text overlaid on the illustration

        LAYOUT:
        [TOP 30%]: Giant letter "{letter}" - black on white/bright background
        [MIDDLE 40%]: Simple illustration of {word}
        [BOTTOM 30%]: Word "{word}" - black on white/bright background

        CRITICAL SUCCESS CRITERIA:
        • Letter "{letter}" must be recognizable by Russian text recognition software
        • Word "{word}" must be readable by Russian OCR systems
        • Use only standard typography (no decorative fonts)
        • Maximum text contrast (black on white/bright)

        Create a professional Russian educational poster with perfect Cyrillic typography.
        """
        
        return prompt.strip()
    
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
        Generate an enhanced prompt with aggressive Cyrillic-specific improvements based on OCR validation failures.
        Uses advanced prompt engineering to force DALL-E 3 to generate proper Russian characters.
        
        Args:
            letter: The target letter
            word: The target word
            ocr_result: OCR validation results
            attempt: Current attempt number (1-based)
            
        Returns:
            Improved prompt string with advanced Cyrillic text generation techniques
        """
        
        # Advanced Cyrillic character descriptions for DALL-E 3
        cyrillic_descriptions = {
            'А': 'Russian А (triangle-like, wider at top than English A)',
            'Б': 'Russian Б (has horizontal line at top and curved bottom, NOT English B)', 
            'В': 'Russian В (similar to English B but different proportions)',
            'Г': 'Russian Г (shaped like upside-down L or Greek Gamma)',
            'Д': 'Russian Д (like triangle with legs extending below)',
            'Е': 'Russian Е (identical to English E)',
            'Ё': 'Russian Ё (like Е with two dots above)',
            'Ж': 'Russian Ж (like asterisk or snowflake pattern)',
            'З': 'Russian З (like English number 3)',
            'И': 'Russian И (like backwards English N)',
            'Й': 'Russian Й (like И with curved breve above)',
            'К': 'Russian К (identical to English K)',
            'Л': 'Russian Л (like upside-down V with feet)',
            'М': 'Russian М (identical to English M)',
            'Н': 'Russian Н (identical to English H)',
            'О': 'Russian О (identical to English O)',
            'П': 'Russian П (like Greek Pi)',
            'Р': 'Russian Р (identical to English P)',
            'С': 'Russian С (identical to English C)',
            'Т': 'Russian Т (identical to English T)',
            'У': 'Russian У (like English Y)',
            'Ф': 'Russian Ф (like circle with vertical line through center)',
            'Х': 'Russian Х (identical to English X)',
            'Ц': 'Russian Ц (like И with small tail at bottom right)',
            'Ч': 'Russian Ч (like number 4)',
            'Ш': 'Russian Ш (like English W but with vertical straight lines)',
            'Щ': 'Russian Щ (like Ш with small tail at bottom right)',
            'Ъ': 'Russian Ъ (hard sign - like b with horizontal line)',
            'Ы': 'Russian Ы (like bl connected together)',
            'Ь': 'Russian Ь (soft sign - like small b)',
            'Э': 'Russian Э (like backwards C with horizontal line in middle)',
            'Ю': 'Russian Ю (like IO connected together)',
            'Я': 'Russian Я (like backwards R)'
        }
        
        # Progressive intensity based on attempt
        if attempt == 2:
            intensity = "CYRILLIC EMERGENCY MODE"
            urgency = "EXTREMELY CRITICAL"
        elif attempt == 3:
            intensity = "MAXIMUM CYRILLIC ENFORCEMENT"
            urgency = "ABSOLUTELY CRITICAL - FINAL ATTEMPT"
        else:
            intensity = "CYRILLIC FOCUS MODE"
            urgency = "IMPORTANT"
        
        # Get specific character descriptions
        letter_desc = cyrillic_descriptions.get(letter, f'Russian letter {letter}')
        
        # Build ultra-aggressive Cyrillic prompt
        improved_prompt = f"""
        {intensity}: {urgency} - Russian educational card with PERFECT CYRILLIC TYPOGRAPHY (Attempt {attempt}/3)

        PREVIOUS FAILURE ANALYSIS:
        OCR failed to detect proper Cyrillic: {ocr_result.get('detected_text', [])}
        REQUIRED: Russian letter "{letter}" and word "{word}"

        🚨 CRITICAL CYRILLIC INSTRUCTIONS FOR DALL-E 3:

        1. LETTER GENERATION - "{letter}":
        • Generate authentic {letter_desc}
        • Use STANDARD Russian textbook typography (ГОСТ 2.304-81)
        • BLACK text on WHITE/bright background for maximum contrast
        • Size: HUGE - minimum 25% of total image height
        • Font: Basic, undecorated, standard Russian school font
        • NO Latin substitutes: avoid B≠В, P≠Р, H≠Н, etc.

        2. WORD GENERATION - "{word}":
        • Each character must be perfect Cyrillic from Russian alphabet
        • Use elementary school Russian textbook font style
        • BLACK text on WHITE/bright background
        • Size: LARGE - minimum 15% of total image height
        • Clear spacing between letters for OCR readability

        3. ANTI-DECORATIVE RULES:
        • NO artistic fonts, NO stylization, NO decorative elements on text
        • NO shadows, gradients, or effects on the Cyrillic text
        • Text must look like Russian government document or textbook
        • Prioritize TEXT READABILITY over visual beauty

        4. LAYOUT REQUIREMENTS:
        [TOP 30%]: Giant Russian letter "{letter}" - plain black on white/bright
        [MIDDLE 40%]: Simple illustration of {word} 
        [BOTTOM 30%]: Russian word "{word}" - plain black on white/bright

        5. OCR OPTIMIZATION:
        • Text contrast ratio minimum 7:1 (black on white ideal)
        • Use fonts similar to: Arial, Times New Roman, or basic sans-serif
        • NO cursive, handwriting, or decorative fonts
        • Letters must be perfectly formed according to Russian standards

        REFERENCE STANDARD: Russian elementary school ABC books (букварь)
        TARGET: Text readable by Russian OCR software with 99% accuracy
        STYLE: Professional Russian educational poster, not artistic

        Generate a Russian educational card that prioritizes TEXT CLARITY above all else.
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