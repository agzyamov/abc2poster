#!/usr/bin/env python3
"""
Poster Assembler Agent - Agent 3
Assembles all generated letter pictures into a final ABC poster.
Creates placeholders for missing letters.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PosterAssemblerAgent:
    """Agent responsible for assembling all letter pictures into a final poster."""
    
    # Default Russian Cyrillic alphabet word pairs (same as coordinator for placeholders)
    DEFAULT_WORD_PAIRS = {
        'А': 'арбуз', 'Б': 'барабан', 'В': 'волк', 'Г': 'гриб', 'Д': 'дом',
        'Е': 'ель', 'Ё': 'ёжик', 'Ж': 'жираф', 'З': 'зебра', 'И': 'игрушка',
        'Й': 'йогурт', 'К': 'кот', 'Л': 'лев', 'М': 'медведь', 'Н': 'нос',
        'О': 'облако', 'П': 'пингвин', 'Р': 'рыба', 'С': 'солнце', 'Т': 'тигр',
        'У': 'утка', 'Ф': 'флаг', 'Х': 'хлеб', 'Ц': 'цветок', 'Ч': 'часы',
        'Ш': 'шар', 'Щ': 'щенок', 'Ъ': 'съезд', 'Ы': 'сыр', 'Ь': 'конь',
        'Э': 'экскаватор', 'Ю': 'юла', 'Я': 'яблоко'
    }
    
    def __init__(self):
        """Initialize the Poster Assembler Agent."""
        self.storage_dir = Path(os.getenv('STORAGE_PATH', './generated_images'))
        self.output_dir = Path(os.getenv('POSTER_OUTPUT_PATH', './output'))
        
        # Poster configuration
        self.grid_cols = int(os.getenv('POSTER_COLS', '6'))  # 6 columns
        self.grid_rows = int(os.getenv('POSTER_ROWS', '6'))  # 6 rows (36 total, 33 Russian letters + 3 extras)
        self.cell_size = int(os.getenv('CELL_SIZE', '400'))  # Each cell is 400x400 pixels
        self.margin = int(os.getenv('POSTER_MARGIN', '50'))  # 50px margin around poster
        self.cell_padding = int(os.getenv('CELL_PADDING', '10'))  # 10px padding between cells
        
        # Colors for placeholders
        self.placeholder_bg_color = (240, 240, 240)  # Light gray
        self.placeholder_text_color = (100, 100, 100)  # Dark gray
        self.poster_bg_color = (255, 255, 255)  # White
        
        self._setup_output_directory()
        
        logger.info(f"🎨 Poster Assembler Agent initialized")
        logger.info(f"📐 Grid: {self.grid_cols}x{self.grid_rows}, Cell: {self.cell_size}px")
    
    def _setup_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Output directory initialized: {self.output_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize output directory: {e}")
            raise
    
    def scan_available_pictures(self) -> Dict[str, Path]:
        """
        Scan the storage directory for available letter pictures.
        
        Returns:
            Dictionary mapping letters to their image file paths
        """
        available_pictures = {}
        
        try:
            # Look for PNG files in format: LETTER_word.png
            for file_path in self.storage_dir.glob("*_*.png"):
                filename = file_path.stem
                if '_' in filename:
                    letter = filename.split('_')[0].upper()
                    if letter in self.DEFAULT_WORD_PAIRS:
                        available_pictures[letter] = file_path
            
            logger.info(f"📊 Found {len(available_pictures)} letter pictures")
            logger.info(f"✅ Available letters: {', '.join(sorted(available_pictures.keys()))}")
            
            missing_letters = set(self.DEFAULT_WORD_PAIRS.keys()) - set(available_pictures.keys())
            if missing_letters:
                logger.info(f"❌ Missing letters: {', '.join(sorted(missing_letters))}")
            
            return available_pictures
            
        except Exception as e:
            logger.error(f"💥 Failed to scan pictures: {e}")
            return {}
    
    def create_placeholder_image(self, letter: str, word: str) -> Image.Image:
        """
        Create a placeholder image for a missing letter.
        
        Args:
            letter: The letter to create placeholder for
            word: The word associated with the letter
            
        Returns:
            PIL Image object
        """
        try:
            # Create base image
            img = Image.new('RGB', (self.cell_size, self.cell_size), self.placeholder_bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fall back to default if not available
            try:
                # Try to find system fonts
                font_size_large = self.cell_size // 4
                font_size_small = self.cell_size // 8
                
                # For letter
                font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_large)
                # For word and placeholder text
                font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size_small)
            except (OSError, IOError):
                # Fall back to default font
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Draw letter
            letter_bbox = draw.textbbox((0, 0), letter, font=font_large)
            letter_width = letter_bbox[2] - letter_bbox[0]
            letter_height = letter_bbox[3] - letter_bbox[1]
            letter_x = (self.cell_size - letter_width) // 2
            letter_y = self.cell_size // 4
            
            draw.text((letter_x, letter_y), letter, fill=self.placeholder_text_color, font=font_large)
            
            # Draw word
            word_bbox = draw.textbbox((0, 0), word, font=font_small)
            word_width = word_bbox[2] - word_bbox[0]
            word_x = (self.cell_size - word_width) // 2
            word_y = letter_y + letter_height + 20
            
            draw.text((word_x, word_y), word, fill=self.placeholder_text_color, font=font_small)
            
            # Draw placeholder indicator
            placeholder_text = "(placeholder)"
            placeholder_bbox = draw.textbbox((0, 0), placeholder_text, font=font_small)
            placeholder_width = placeholder_bbox[2] - placeholder_bbox[0]
            placeholder_x = (self.cell_size - placeholder_width) // 2
            placeholder_y = word_y + 40
            
            draw.text((placeholder_x, placeholder_y), placeholder_text, 
                     fill=(150, 150, 150), font=font_small)
            
            # Draw border
            border_width = 3
            draw.rectangle(
                [border_width//2, border_width//2, 
                 self.cell_size - border_width//2, self.cell_size - border_width//2],
                outline=(200, 200, 200), width=border_width
            )
            
            logger.debug(f"📋 Created placeholder for {letter} - {word}")
            return img
            
        except Exception as e:
            logger.error(f"💥 Failed to create placeholder for {letter}: {e}")
            # Return a simple gray square as fallback
            return Image.new('RGB', (self.cell_size, self.cell_size), (128, 128, 128))
    
    def load_and_resize_image(self, image_path: Path) -> Image.Image:
        """
        Load and resize an image to fit the cell size.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object resized to cell_size
        """
        try:
            img = Image.open(image_path)
            # Convert to RGB if necessary (handles RGBA, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to fit cell size while maintaining aspect ratio
            img.thumbnail((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
            
            # Create a new image with exact cell size and paste the resized image centered
            final_img = Image.new('RGB', (self.cell_size, self.cell_size), (255, 255, 255))
            
            # Calculate position to center the image
            x_offset = (self.cell_size - img.width) // 2
            y_offset = (self.cell_size - img.height) // 2
            
            final_img.paste(img, (x_offset, y_offset))
            
            logger.debug(f"📷 Loaded and resized: {image_path.name}")
            return final_img
            
        except Exception as e:
            logger.error(f"💥 Failed to load image {image_path}: {e}")
            # Return placeholder on error
            letter = image_path.stem.split('_')[0] if '_' in image_path.stem else 'X'
            word = self.DEFAULT_WORD_PAIRS.get(letter, 'error')
            return self.create_placeholder_image(letter, word)
    
    def create_poster_layout(self, available_pictures: Dict[str, Path]) -> List[List[str]]:
        """
        Create the layout grid for the poster.
        
        Args:
            available_pictures: Dictionary of available letter pictures
            
        Returns:
            2D list representing the poster layout
        """
        # Create alphabetical order layout
        all_letters = sorted(self.DEFAULT_WORD_PAIRS.keys())
        layout = []
        
        letter_index = 0
        for row in range(self.grid_rows):
            row_letters = []
            for col in range(self.grid_cols):
                if letter_index < len(all_letters):
                    row_letters.append(all_letters[letter_index])
                    letter_index += 1
                else:
                    # Fill remaining cells with empty spaces
                    row_letters.append('')
            layout.append(row_letters)
        
        logger.info(f"📐 Created {self.grid_rows}x{self.grid_cols} layout")
        return layout
    
    def assemble_poster(self, title: str = "ABC Learning Poster") -> Tuple[Path, Dict]:
        """
        Assemble the final ABC poster.
        
        Args:
            title: Title for the poster
            
        Returns:
            Tuple of (poster_file_path, assembly_report)
        """
        try:
            logger.info(f"🎨 Starting poster assembly: '{title}'")
            
            # Scan available pictures
            available_pictures = self.scan_available_pictures()
            
            # Create layout
            layout = self.create_poster_layout(available_pictures)
            
            # Calculate poster dimensions
            poster_width = (self.grid_cols * self.cell_size + 
                          (self.grid_cols - 1) * self.cell_padding + 
                          2 * self.margin)
            poster_height = (self.grid_rows * self.cell_size + 
                           (self.grid_rows - 1) * self.cell_padding + 
                           2 * self.margin + 100)  # Extra space for title
            
            logger.info(f"📏 Poster dimensions: {poster_width}x{poster_height}")
            
            # Create poster canvas
            poster = Image.new('RGB', (poster_width, poster_height), self.poster_bg_color)
            draw = ImageDraw.Draw(poster)
            
            # Draw title
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            except (OSError, IOError):
                title_font = ImageFont.load_default()
            
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (poster_width - title_width) // 2
            title_y = 20
            
            draw.text((title_x, title_y), title, fill=(50, 50, 50), font=title_font)
            
            # Assembly statistics
            stats = {
                'total_cells': 0,
                'available_images': 0,
                'placeholder_images': 0,
                'empty_cells': 0
            }
            
            # Assemble grid
            current_y = self.margin + 80  # Start below title
            
            for row_idx, row in enumerate(layout):
                current_x = self.margin
                
                for col_idx, letter in enumerate(row):
                    if letter:  # Not an empty cell
                        stats['total_cells'] += 1
                        
                        if letter in available_pictures:
                            # Load existing image
                            img = self.load_and_resize_image(available_pictures[letter])
                            stats['available_images'] += 1
                            logger.debug(f"✅ Added {letter} from file")
                        else:
                            # Create placeholder
                            word = self.DEFAULT_WORD_PAIRS[letter]
                            img = self.create_placeholder_image(letter, word)
                            stats['placeholder_images'] += 1
                            logger.debug(f"📋 Added placeholder for {letter}")
                        
                        # Paste image onto poster
                        poster.paste(img, (current_x, current_y))
                    else:
                        stats['empty_cells'] += 1
                    
                    current_x += self.cell_size + self.cell_padding
                
                current_y += self.cell_size + self.cell_padding
            
            # Save poster
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            poster_filename = f"abc_poster_{timestamp}.png"
            poster_path = self.output_dir / poster_filename
            
            poster.save(poster_path, 'PNG', quality=95)
            
            # Create assembly report
            report = {
                'poster_info': {
                    'filename': poster_filename,
                    'filepath': str(poster_path),
                    'title': title,
                    'timestamp': datetime.now().isoformat(),
                    'dimensions': f"{poster_width}x{poster_height}",
                    'grid_size': f"{self.grid_cols}x{self.grid_rows}",
                    'cell_size': self.cell_size
                },
                'assembly_stats': stats,
                'available_letters': sorted(available_pictures.keys()),
                'missing_letters': sorted(set(self.DEFAULT_WORD_PAIRS.keys()) - set(available_pictures.keys())),
                'layout': layout
            }
            
            # Save assembly report
            report_path = self.output_dir / f"assembly_report_{timestamp}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"🎉 Poster assembly completed!")
            logger.info(f"📁 Poster saved: {poster_path}")
            logger.info(f"📊 Report saved: {report_path}")
            logger.info(f"📈 Stats: {stats['available_images']} real, {stats['placeholder_images']} placeholders")
            
            return poster_path, report
            
        except Exception as e:
            logger.error(f"💥 Poster assembly failed: {e}")
            raise
    
    def create_preview_grid(self, max_items: int = 10) -> Optional[Path]:
        """
        Create a preview grid showing available images.
        
        Args:
            max_items: Maximum number of items to show in preview
            
        Returns:
            Path to the preview image
        """
        try:
            available_pictures = self.scan_available_pictures()
            
            if not available_pictures:
                logger.warning("⚠️ No pictures available for preview")
                return None
            
            # Limit items for preview
            items = list(available_pictures.items())[:max_items]
            
            # Calculate preview grid (try to make it roughly square)
            cols = min(5, len(items))
            rows = (len(items) + cols - 1) // cols
            
            # Smaller cell size for preview
            preview_cell_size = 200
            preview_width = cols * preview_cell_size + (cols - 1) * 10 + 40
            preview_height = rows * preview_cell_size + (rows - 1) * 10 + 80
            
            preview = Image.new('RGB', (preview_width, preview_height), (255, 255, 255))
            draw = ImageDraw.Draw(preview)
            
            # Title
            draw.text((20, 20), f"Preview: {len(items)} images", fill=(50, 50, 50))
            
            # Grid
            y = 60
            for row in range(rows):
                x = 20
                for col in range(cols):
                    idx = row * cols + col
                    if idx < len(items):
                        letter, img_path = items[idx]
                        img = self.load_and_resize_image(img_path)
                        img = img.resize((preview_cell_size, preview_cell_size))
                        preview.paste(img, (x, y))
                    x += preview_cell_size + 10
                y += preview_cell_size + 10
            
            # Save preview
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            preview_path = self.output_dir / f"preview_{timestamp}.png"
            preview.save(preview_path)
            
            logger.info(f"👀 Preview created: {preview_path}")
            return preview_path
            
        except Exception as e:
            logger.error(f"💥 Preview creation failed: {e}")
            return None


def main():
    """CLI interface for the Poster Assembler Agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Assemble letter pictures into an ABC poster")
    parser.add_argument('--title', '-t', type=str, default="ABC Learning Poster", 
                       help='Title for the poster')
    parser.add_argument('--preview', '-p', action='store_true', 
                       help='Create a preview grid of available images')
    parser.add_argument('--scan', '-s', action='store_true', 
                       help='Scan and report available pictures')
    
    args = parser.parse_args()
    
    try:
        assembler = PosterAssemblerAgent()
        
        if args.scan:
            # Just scan and report
            available = assembler.scan_available_pictures()
            print(f"\n📊 Available Pictures: {len(available)}")
            for letter in sorted(available.keys()):
                print(f"  ✅ {letter} - {available[letter].name}")
            
            missing = set(assembler.DEFAULT_WORD_PAIRS.keys()) - set(available.keys())
            if missing:
                print(f"\n❌ Missing Pictures: {len(missing)}")
                for letter in sorted(missing):
                    word = assembler.DEFAULT_WORD_PAIRS[letter]
                    print(f"  📋 {letter} - {word} (will use placeholder)")
            return
        
        if args.preview:
            # Create preview
            preview_path = assembler.create_preview_grid()
            if preview_path:
                print(f"👀 Preview created: {preview_path}")
            return
        
        # Assemble poster
        logger.info("🎨 Starting ABC Poster assembly...")
        poster_path, report = assembler.assemble_poster(title=args.title)
        
        # Print summary
        stats = report['assembly_stats']
        print(f"\n🎉 Poster assembly completed!")
        print(f"📁 Poster saved: {poster_path}")
        print(f"📊 Statistics:")
        print(f"  ✅ Real images: {stats['available_images']}")
        print(f"  📋 Placeholders: {stats['placeholder_images']}")
        print(f"  📐 Total cells: {stats['total_cells']}")
        
        if stats['placeholder_images'] > 0:
            print(f"\n💡 Tip: Generate missing letters and re-run to replace placeholders")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Assembly interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 