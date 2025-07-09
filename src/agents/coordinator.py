#!/usr/bin/env python3
"""
Coordinator Agent - Agent 2
Orchestrates the generation process by calling Agent 1 in a loop for all A-Z letter-word pairs.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from dotenv import load_dotenv

# Import Agent 1
from hybrid_picture_generator import GPTImage1PictureGeneratorAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """Agent responsible for coordinating the generation of all A-Z letter pictures."""
    
    # Default Russian Cyrillic alphabet word pairs for Russian ABC poster
    DEFAULT_WORD_PAIRS = {
        'А': 'арбуз',      # watermelon
        'Б': 'барабан',    # drum
        'В': 'волк',       # wolf
        'Г': 'гриб',       # mushroom
        'Д': 'дом',        # house
        'Е': 'ель',        # spruce tree
        'Ё': 'ёжик',       # hedgehog
        'Ж': 'жираф',      # giraffe
        'З': 'зебра',      # zebra
        'И': 'игрушка',    # toy
        'Й': 'йогурт',     # yogurt
        'К': 'кот',        # cat
        'Л': 'лев',        # lion
        'М': 'медведь',    # bear
        'Н': 'нос',        # nose
        'О': 'облако',     # cloud
        'П': 'пингвин',    # penguin
        'Р': 'рыба',       # fish
        'С': 'солнце',     # sun
        'Т': 'тигр',       # tiger
        'У': 'утка',       # duck
        'Ф': 'флаг',       # flag
        'Х': 'хлеб',       # bread
        'Ц': 'цветок',     # flower
        'Ч': 'часы',       # clock
        'Ш': 'шар',        # ball
        'Щ': 'щенок',      # puppy
        'Ъ': 'съезд',      # съезд (gathering) - one of few words starting with ъ
        'Ы': 'сыр',        # cheese (contains ы)
        'Ь': 'конь',       # horse (ends with ь)
        'Э': 'экскаватор', # excavator
        'Ю': 'юла',        # spinning top
        'Я': 'яблоко'      # apple
    }
    
    def __init__(self, custom_word_pairs: Optional[Dict[str, str]] = None):
        """
        Initialize the Coordinator Agent.
        
        Args:
            custom_word_pairs: Optional custom letter-word pairs to use instead of defaults
        """
        self.word_pairs = custom_word_pairs or self.DEFAULT_WORD_PAIRS
        self.rate_limit_ms = int(os.getenv('RATE_LIMIT_MS', '2000'))  # Default 2 seconds
        self.storage_dir = Path(os.getenv('STORAGE_PATH', './generated_images'))
        self.output_dir = Path(os.getenv('POSTER_OUTPUT_PATH', './output'))
        
        # Initialize picture generator agent
        self.picture_agent = GPTImage1PictureGeneratorAgent()
        
        # Setup output directory
        self._setup_output_directory()
        
        logger.info(f"🎭 Coordinator Agent initialized")
        logger.info(f"📝 Will generate {len(self.word_pairs)} letter pictures")
        logger.info(f"⏱️ Rate limit: {self.rate_limit_ms}ms between requests")
    
    def _setup_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Output directory initialized: {self.output_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize output directory: {e}")
            raise
    
    def load_custom_word_pairs(self, config_file: str) -> Dict[str, str]:
        """
        Load custom word pairs from a JSON configuration file.
        
        Args:
            config_file: Path to JSON file containing letter-word pairs
            
        Returns:
            Dictionary of letter-word pairs
            
        Raises:
            Exception: If file cannot be loaded or parsed
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            with open(config_path, 'r') as f:
                custom_pairs = json.load(f)
            
            # Validate that we have all 33 Russian letters
            expected_letters = set('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
            provided_letters = set(custom_pairs.keys())
            
            if provided_letters != expected_letters:
                missing = expected_letters - provided_letters
                extra = provided_letters - expected_letters
                error_msg = []
                if missing:
                    error_msg.append(f"Missing letters: {', '.join(sorted(missing))}")
                if extra:
                    error_msg.append(f"Extra letters: {', '.join(sorted(extra))}")
                raise ValueError(f"Invalid word pairs configuration. {' '.join(error_msg)}")
            
            logger.info(f"📁 Loaded custom word pairs from: {config_file}")
            return custom_pairs
            
        except Exception as e:
            logger.error(f"❌ Failed to load custom word pairs: {e}")
            raise
    
    def save_generation_report(self, results: List[Dict]) -> Path:
        """
        Save a comprehensive generation report.
        
        Args:
            results: List of generation results from picture agent
            
        Returns:
            Path to the saved report file
        """
        report = {
            "generation_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_letters": len(self.word_pairs),
                "successful_generations": len([r for r in results if r.get("success")]),
                "cached_images": len([r for r in results if r.get("cached")]),
                "failed_generations": len([r for r in results if not r.get("success")]),
                "rate_limit_ms": self.rate_limit_ms
            },
            "word_pairs_used": self.word_pairs,
            "detailed_results": results,
            "failed_letters": [r for r in results if not r.get("success")],
            "storage_directory": str(self.storage_dir),
            "output_directory": str(self.output_dir)
        }
        
        report_path = self.output_dir / f"generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Generation report saved: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save generation report: {e}")
            raise
    
    def generate_all_pictures(self, resume_from: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Generate all letter pictures using Agent 1.
        
        Args:
            resume_from: Letter to resume from (useful if previous run was interrupted)
            limit: Maximum number of letters to generate (useful for testing)
            
        Returns:
            List of generation results
        """
        results = []
        total_letters = len(self.word_pairs)
        
        # Determine starting point
        letters_to_process = list(self.word_pairs.keys())
        if resume_from:
            try:
                start_index = letters_to_process.index(resume_from.upper())
                letters_to_process = letters_to_process[start_index:]
                logger.info(f"🔄 Resuming generation from letter: {resume_from.upper()}")
            except ValueError:
                logger.warning(f"⚠️ Resume letter '{resume_from}' not found, starting from beginning")
        
        # Apply limit if specified (for testing purposes)
        if limit and limit > 0:
            letters_to_process = letters_to_process[:limit]
            logger.info(f"🧪 Testing mode: limiting to first {limit} letters")
        
        logger.info(f"🚀 Starting generation of {len(letters_to_process)} letter pictures...")
        
        start_time = time.time()
        
        for i, letter in enumerate(letters_to_process, 1):
            word = self.word_pairs[letter]
            
            logger.info(f"📝 [{i}/{len(letters_to_process)}] Processing: {letter} - {word}")
            
            try:
                # Generate picture using Agent 1
                result = self.picture_agent.generate_picture(letter, word)  # Now uses adaptive OCR learning automatically
                results.append(result)
                
                if result.get("success"):
                    if result.get("cached"):
                        logger.info(f"⚡ Used cached image for {letter} - {word}")
                    else:
                        logger.info(f"🎨 Generated new image for {letter} - {word}")
                else:
                    logger.error(f"❌ Failed to generate {letter} - {word}: {result.get('error')}")
                
                # Rate limiting (skip for last item)
                if i < len(letters_to_process):
                    logger.debug(f"⏳ Rate limiting: waiting {self.rate_limit_ms}ms...")
                    time.sleep(self.rate_limit_ms / 1000.0)
                
            except KeyboardInterrupt:
                logger.warning(f"⚠️ Generation interrupted by user at letter {letter}")
                logger.info(f"📊 Processed {i-1} out of {len(letters_to_process)} letters")
                break
                
            except Exception as e:
                logger.error(f"💥 Unexpected error processing {letter} - {word}: {e}")
                results.append({
                    "success": False,
                    "letter": letter,
                    "word": word,
                    "error": f"Unexpected error: {str(e)}"
                })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Summary statistics
        successful = len([r for r in results if r.get("success")])
        cached = len([r for r in results if r.get("cached")])
        failed = len([r for r in results if not r.get("success")])
        
        logger.info(f"🎉 Generation completed!")
        logger.info(f"📊 Results: {successful} successful, {cached} cached, {failed} failed")
        logger.info(f"⏱️ Total time: {duration:.1f} seconds")
        
        return results
    
    def get_generation_status(self) -> Dict:
        """
        Check the current status of generated pictures.
        
        Returns:
            Dictionary with generation status information
        """
        try:
            existing_files = list(self.storage_dir.glob("*_*.png"))
            generated_letters = set()
            
            for file_path in existing_files:
                # Extract letter from filename (format: LETTER_word.png)
                filename = file_path.stem
                if '_' in filename:
                    letter = filename.split('_')[0]
                    if letter in self.word_pairs:
                        generated_letters.add(letter)
            
            all_letters = set(self.word_pairs.keys())
            missing_letters = all_letters - generated_letters
            
            status = {
                "total_letters": len(all_letters),
                "generated_count": len(generated_letters),
                "missing_count": len(missing_letters),
                "generated_letters": sorted(list(generated_letters)),
                "missing_letters": sorted(list(missing_letters)),
                "completion_percentage": (len(generated_letters) / len(all_letters)) * 100,
                "storage_directory": str(self.storage_dir)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to get generation status: {e}")
            return {"error": str(e)}
    
    def cleanup_generated_images(self, confirm: bool = False) -> None:
        """
        Clean up all generated images (useful for testing or reset).
        
        Args:
            confirm: If True, skip confirmation prompt
        """
        if not confirm:
            response = input("⚠️ This will delete all generated images. Continue? (y/N): ")
            if response.lower() != 'y':
                logger.info("🚫 Cleanup cancelled")
                return
        
        try:
            deleted_count = 0
            for file_path in self.storage_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1
            
            logger.info(f"🧹 Cleanup completed: {deleted_count} files deleted")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


def main():
    """CLI interface for the Coordinator Agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coordinate generation of all A-Z letter pictures")
    parser.add_argument('--config', '-c', type=str, help='Custom word pairs JSON file')
    parser.add_argument('--resume', '-r', type=str, help='Resume from specific letter')
    parser.add_argument('--limit', '-l', type=int, help='Limit number of letters to generate (for testing)')
    parser.add_argument('--status', '-s', action='store_true', help='Show generation status')
    parser.add_argument('--cleanup', action='store_true', help='Clean up generated images')
    
    args = parser.parse_args()
    
    try:
        # Load custom word pairs if provided
        custom_pairs = None
        if args.config:
            coordinator = CoordinatorAgent()  # Temporary instance to use load method
            custom_pairs = coordinator.load_custom_word_pairs(args.config)
        
        # Initialize coordinator
        coordinator = CoordinatorAgent(custom_word_pairs=custom_pairs)
        
        if args.status:
            # Show generation status
            status = coordinator.get_generation_status()
            print(f"\n📊 Generation Status:")
            print(f"Generated: {status['generated_count']}/{status['total_letters']} letters")
            print(f"Completion: {status['completion_percentage']:.1f}%")
            if status['missing_letters']:
                print(f"Missing: {', '.join(status['missing_letters'])}")
            return
        
        if args.cleanup:
            # Clean up generated images
            coordinator.cleanup_generated_images()
            return
        
        # Generate all pictures
        logger.info("🎭 Starting ABC Poster generation coordination...")
        results = coordinator.generate_all_pictures(resume_from=args.resume, limit=args.limit)
        
        # Save generation report
        report_path = coordinator.save_generation_report(results)
        
        # Print summary
        successful = len([r for r in results if r.get("success")])
        total = len(results)
        
        print(f"\n🎉 Coordination completed!")
        print(f"📊 Generated: {successful}/{total} letter pictures")
        print(f"📁 Report saved: {report_path}")
        
        if successful == total:
            print("✅ All letters generated successfully! Ready for Agent 3 (Poster Assembler)")
        else:
            failed_letters = [r['letter'] for r in results if not r.get("success")]
            print(f"⚠️ Failed letters: {', '.join(failed_letters)}")
            print("🔄 You can resume with: --resume <letter>")
            
    except KeyboardInterrupt:
        logger.info("⚠️ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 