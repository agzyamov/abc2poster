#!/usr/bin/env python3
"""
Hybrid Coordinator Agent for Russian ABC Poster Generation.

Uses the hybrid picture generator (DALL-E 3 + Python text overlay) 
to create perfect Russian alphabet cards with readable Cyrillic text.
"""

import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Import the successful hybrid picture generator
from hybrid_picture_generator import HybridPictureGeneratorAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HybridCoordinatorAgent:
    """Coordinator agent that orchestrates hybrid picture generation for the Russian alphabet."""
    
    def __init__(self):
        """Initialize the hybrid coordinator agent."""
        self.picture_agent = HybridPictureGeneratorAgent()
        self.output_dir = Path(os.getenv('POSTER_OUTPUT_PATH', 'output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Russian alphabet letter-word pairs
        self.russian_alphabet = {
            'А': 'арбуз',
            'Б': 'барабан', 
            'В': 'волк',
            'Г': 'гриб',
            'Д': 'дом',
            'Е': 'ель',
            'Ё': 'ёжик',
            'Ж': 'жираф',
            'З': 'зебра',
            'И': 'игрушка',
            'Й': 'йогурт',
            'К': 'кот',
            'Л': 'лев',
            'М': 'медведь',
            'Н': 'нос',
            'О': 'облако',
            'П': 'пингвин',
            'Р': 'рыба',
            'С': 'солнце',
            'Т': 'тигр',
            'У': 'утка',
            'Ф': 'флаг',
            'Х': 'хлеб',
            'Ц': 'цветок',
            'Ч': 'часы',
            'Ш': 'шар',
            'Щ': 'щенок',
            'Ъ': 'съезд',
            'Ы': 'сыр',
            'Ь': 'конь',
            'Э': 'экскаватор',
            'Ю': 'юла',
            'Я': 'яблоко'
        }
    
    def get_generation_progress(self) -> Dict:
        """Check which letters have already been generated."""
        generated_letters = set()
        
        for letter in self.russian_alphabet.keys():
            word = self.russian_alphabet[letter]
            expected_file = self.picture_agent.storage_dir / f"{letter}_{word}.png"
            if expected_file.exists():
                generated_letters.add(letter)
        
        return {
            "total_letters": len(self.russian_alphabet),
            "generated_count": len(generated_letters),
            "generated_letters": sorted(generated_letters),
            "remaining_letters": sorted(set(self.russian_alphabet.keys()) - generated_letters),
            "completion_percentage": (len(generated_letters) / len(self.russian_alphabet)) * 100
        }
    
    def generate_alphabet_pictures(self, limit: Optional[int] = None, resume: bool = False) -> List[Dict]:
        """Generate pictures for the Russian alphabet using hybrid approach."""
        logger.info("🚀 Starting hybrid Russian alphabet generation")
        
        # Check progress
        progress = self.get_generation_progress()
        logger.info(f"📊 Current progress: {progress['generated_count']}/{progress['total_letters']} letters ({progress['completion_percentage']:.1f}%)")
        
        if resume and progress['generated_count'] > 0:
            logger.info(f"📄 Resuming generation - skipping {progress['generated_count']} existing letters")
            letters_to_generate = progress['remaining_letters']
        else:
            letters_to_generate = list(self.russian_alphabet.keys())
        
        if limit:
            letters_to_generate = letters_to_generate[:limit]
            logger.info(f"🎯 Limited generation to {limit} letters")
        
        logger.info(f"📝 Will generate: {letters_to_generate}")
        
        results = []
        successful_generations = 0
        failed_generations = 0
        
        start_time = datetime.now()
        
        for i, letter in enumerate(letters_to_generate):
            word = self.russian_alphabet[letter]
            
            logger.info(f"\n📝 Generating {i+1}/{len(letters_to_generate)}: {letter} - {word}")
            
            try:
                # Generate picture using hybrid approach
                result = self.picture_agent.generate_picture(letter, word)
                results.append(result)
                
                if result["success"]:
                    successful_generations += 1
                    cache_status = "cached" if result.get("cached", False) else "generated"
                    logger.info(f"✅ {letter}/{word} - {cache_status}")
                else:
                    failed_generations += 1
                    logger.error(f"❌ {letter}/{word} - {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                failed_generations += 1
                error_result = {
                    "success": False,
                    "letter": letter,
                    "word": word,
                    "error": str(e),
                    "method": "hybrid"
                }
                results.append(error_result)
                logger.error(f"💥 Fatal error for {letter}/{word}: {e}")
            
            # Rate limiting between API calls
            if i < len(letters_to_generate) - 1:  # Don't sleep after the last one
                logger.info("⏳ Rate limiting: waiting 2 seconds...")
                time.sleep(2)
        
        # Final statistics
        end_time = datetime.now()
        duration = end_time - start_time
        
        final_progress = self.get_generation_progress()
        
        logger.info(f"\n🎯 HYBRID GENERATION COMPLETE!")
        logger.info(f"✅ Successful: {successful_generations}")
        logger.info(f"❌ Failed: {failed_generations}")
        logger.info(f"📊 Total progress: {final_progress['generated_count']}/{final_progress['total_letters']} letters ({final_progress['completion_percentage']:.1f}%)")
        logger.info(f"⏱️  Duration: {duration}")
        
        # Save generation report
        self.save_generation_report(results, duration, final_progress)
        
        return results
    
    def save_generation_report(self, results: List[Dict], duration, progress: Dict) -> None:
        """Save detailed generation report."""
        try:
            report = {
                "generation_method": "hybrid",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration.total_seconds(),
                "progress": progress,
                "results": results,
                "summary": {
                    "total_attempts": len(results),
                    "successful": sum(1 for r in results if r["success"]),
                    "failed": sum(1 for r in results if not r["success"]),
                    "cached": sum(1 for r in results if r.get("cached", False)),
                    "newly_generated": sum(1 for r in results if r["success"] and not r.get("cached", False))
                }
            }
            
            report_file = self.output_dir / f"hybrid_generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Generation report saved: {report_file.name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save generation report: {e}")
    
    def test_hybrid_approach(self) -> Dict:
        """Test the hybrid approach with a few sample letters."""
        logger.info("🧪 Testing hybrid approach with sample letters...")
        
        # Test with a mix of easy and difficult letters
        test_letters = ['А', 'Г', 'Ж', 'Щ']  # Mix of simple and complex Cyrillic
        
        test_results = []
        
        for letter in test_letters:
            word = self.russian_alphabet[letter]
            logger.info(f"🎯 Testing {letter}/{word}...")
            
            result = self.picture_agent.generate_picture(letter, word)
            test_results.append(result)
            
            if result["success"]:
                logger.info(f"✅ {letter}/{word} - Success")
            else:
                logger.error(f"❌ {letter}/{word} - Failed: {result.get('error')}")
            
            time.sleep(1)  # Brief pause between tests
        
        success_rate = sum(1 for r in test_results if r["success"]) / len(test_results)
        
        summary = {
            "test_letters": test_letters,
            "results": test_results,
            "success_rate": success_rate,
            "recommendation": "Proceed with full generation" if success_rate >= 0.75 else "Review and fix issues first"
        }
        
        logger.info(f"🎯 Test complete: {success_rate:.1%} success rate")
        logger.info(f"💡 Recommendation: {summary['recommendation']}")
        
        return summary


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(description="Hybrid Russian ABC Poster Generator")
    parser.add_argument("--limit", type=int, help="Limit number of letters to generate")
    parser.add_argument("--resume", action="store_true", help="Resume from existing progress")
    parser.add_argument("--test", action="store_true", help="Run test with sample letters")
    
    args = parser.parse_args()
    
    try:
        coordinator = HybridCoordinatorAgent()
        
        if args.test:
            # Run test mode
            test_results = coordinator.test_hybrid_approach()
            if test_results["success_rate"] >= 0.75:
                print(f"\n✅ Test passed! Success rate: {test_results['success_rate']:.1%}")
                print("🚀 Ready for full alphabet generation")
            else:
                print(f"\n❌ Test issues detected. Success rate: {test_results['success_rate']:.1%}")
                print("🔧 Review and fix before proceeding")
        else:
            # Run full generation
            results = coordinator.generate_alphabet_pictures(
                limit=args.limit, 
                resume=args.resume
            )
            
            success_count = sum(1 for r in results if r["success"])
            print(f"\n🎯 Generation complete!")
            print(f"✅ Successfully generated: {success_count}/{len(results)} letters")
            print(f"📁 Files saved in: {coordinator.picture_agent.storage_dir}")
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 