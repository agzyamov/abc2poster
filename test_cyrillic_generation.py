#!/usr/bin/env python3
"""
Тестовый скрипт для проверки возможностей DALL-E 3 в генерации кириллического текста.
Проверяем разные стратегии промптинга для кириллических символов.
"""

import os
import time
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import pytesseract
from PIL import Image

# Загружаем переменные окружения
load_dotenv()

class CyrillicGenerationTester:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.test_dir = Path("cyrillic_test_results")
        self.test_dir.mkdir(exist_ok=True)
        
    def test_prompt_strategy(self, strategy_name: str, prompt: str, test_id: str) -> dict:
        """Тестирует конкретную стратегию промптинга"""
        print(f"🧪 Тестируем стратегию: {strategy_name}")
        print(f"📝 Промпт: {prompt[:100]}...")
        
        try:
            # Генерируем изображение
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            if not response.data or len(response.data) == 0:
                raise Exception("No image data received from OpenAI API")
            
            image_url = response.data[0].url
            if not image_url:
                raise Exception("No image URL received from OpenAI API")
            
            # Скачиваем изображение
            filename = f"{test_id}_{strategy_name.replace(' ', '_')}.png"
            filepath = self.test_dir / filename
            
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            
            print(f"✅ Изображение сохранено: {filename}")
            
            # Анализируем с помощью OCR
            time.sleep(1)  # Небольшая пауза перед OCR
            ocr_result = self.analyze_with_ocr(filepath)
            
            return {
                "strategy": strategy_name,
                "success": True,
                "filepath": str(filepath),
                "ocr_result": ocr_result
            }
            
        except Exception as e:
            print(f"❌ Ошибка в стратегии {strategy_name}: {e}")
            return {
                "strategy": strategy_name,
                "success": False,
                "error": str(e),
                "ocr_result": {"detected_text": [], "success": False}
            }
    
    def analyze_with_ocr(self, filepath: Path) -> dict:
        """Анализирует изображение с помощью OCR"""
        try:
            with Image.open(filepath) as img:
                # Пробуем разные настройки OCR
                detected_text_rus = pytesseract.image_to_string(
                    img, lang='rus', config='--psm 6'
                ).strip()
                
                detected_text_eng = pytesseract.image_to_string(
                    img, lang='eng', config='--psm 6'
                ).strip()
                
                detected_text_combined = pytesseract.image_to_string(
                    img, lang='rus+eng', config='--psm 6'
                ).strip()
                
                # Обрабатываем результаты
                detected_lines_rus = [line.strip() for line in detected_text_rus.split('\n') if line.strip()]
                detected_lines_eng = [line.strip() for line in detected_text_eng.split('\n') if line.strip()]
                detected_lines_combined = [line.strip() for line in detected_text_combined.split('\n') if line.strip()]
                
                print(f"📖 OCR (русский): {detected_lines_rus}")
                print(f"📖 OCR (английский): {detected_lines_eng}")
                print(f"📖 OCR (комбинированный): {detected_lines_combined}")
                
                # Проверяем наличие кириллических символов
                cyrillic_found = any(
                    any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in line)
                    for line in detected_lines_combined
                )
                
                return {
                    "detected_text_rus": detected_lines_rus,
                    "detected_text_eng": detected_lines_eng, 
                    "detected_text_combined": detected_lines_combined,
                    "cyrillic_found": cyrillic_found,
                    "success": len(detected_lines_combined) > 0
                }
                
        except Exception as e:
            print(f"❌ Ошибка OCR: {e}")
            return {
                "detected_text_rus": [],
                "detected_text_eng": [],
                "detected_text_combined": [],
                "cyrillic_found": False,
                "success": False,
                "error": str(e)
            }
    
    def run_cyrillic_tests(self):
        """Запускает серию тестов для кириллических символов"""
        print("🚀 Начинаем тестирование генерации кириллицы DALL-E 3")
        print("=" * 60)
        
        # Простые тестовые случаи
        test_cases = [
            {
                "letter": "А",
                "word": "арбуз",
                "description": "Простая буква, идентичная английской A"
            },
            {
                "letter": "Б", 
                "word": "барабан",
                "description": "Уникальная кириллическая буква"
            },
            {
                "letter": "Г",
                "word": "гриб", 
                "description": "Проблемная буква (как перевернутая L)"
            }
        ]
        
        # Разные стратегии промптинга
        strategies = {
            "базовая": lambda letter, word: f"Russian letter {letter} and word {word}",
            
            "образовательная": lambda letter, word: f"""
            Create a Russian educational card with letter {letter} and word {word}.
            Use clear, readable Cyrillic text.
            """,
            
            "типографская": lambda letter, word: f"""
            Generate Russian letter {letter} and word {word} using standard typography.
            Use Arial or Times New Roman font style.
            Black text on white background.
            Text must be clearly readable.
            """,
            
            "техническая": lambda letter, word: f"""
            Create image with Russian Cyrillic letter {letter} and word {word}.
            CRITICAL: Use only standard Russian typography (ГОСТ 2.304-81).
            Letter {letter} must be recognizable by OCR software.
            Word {word} must be readable by Russian text recognition.
            Font: basic sans-serif, black color, high contrast.
            """,
            
            "геометрическая": lambda letter, word: self.get_geometric_description(letter, word)
        }
        
        all_results = []
        
        for test_case in test_cases:
            letter = test_case["letter"]
            word = test_case["word"]
            description = test_case["description"]
            
            print(f"\n🎯 ТЕСТ: {letter}/{word} - {description}")
            print("-" * 40)
            
            test_results = []
            
            for strategy_name, prompt_func in strategies.items():
                prompt = prompt_func(letter, word)
                test_id = f"{letter}_{word}"
                
                result = self.test_prompt_strategy(strategy_name, prompt, test_id)
                test_results.append(result)
                
                # Пауза между запросами к API
                time.sleep(3)
            
            # Анализируем результаты для этой буквы
            print(f"\n📊 РЕЗУЛЬТАТЫ ДЛЯ {letter}/{word}:")
            success_count = sum(1 for r in test_results if r.get('ocr_result', {}).get('cyrillic_found', False))
            print(f"Успешных генераций кириллицы: {success_count}/{len(strategies)}")
            
            all_results.extend(test_results)
            print("\n" + "="*60)
        
        # Общая сводка
        self.print_summary(all_results)
        return all_results
    
    def get_geometric_description(self, letter: str, word: str) -> str:
        """Возвращает геометрическое описание буквы"""
        descriptions = {
            'А': 'Triangle shape with horizontal crossbar',
            'Б': 'Vertical line with horizontal top line and curved bottom',
            'Г': 'Vertical line with horizontal line at top (upside-down L shape)',
        }
        
        char_desc = descriptions.get(letter, f'Russian letter {letter}')
        
        return f"""
        Generate Russian letter {letter} with exact geometric specification:
        {char_desc}
        
        And Russian word {word} in standard Cyrillic typography.
        
        GEOMETRIC REQUIREMENTS:
        - Letter {letter}: {char_desc}
        - Use basic geometric shapes
        - Black lines on white background
        - Clear, simple design
        - No decorative elements
        """
    
    def print_summary(self, results: list):
        """Выводит сводку результатов"""
        print("\n🎯 ОБЩАЯ СВОДКА ТЕСТИРОВАНИЯ:")
        print("=" * 50)
        
        # Группируем по стратегиям
        by_strategy = {}
        for result in results:
            strategy = result['strategy']
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(result)
        
        # Анализируем каждую стратегию
        for strategy, strategy_results in by_strategy.items():
            success_count = sum(1 for r in strategy_results 
                              if r.get('ocr_result', {}).get('cyrillic_found', False))
            total_count = len(strategy_results)
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            
            print(f"\n📈 {strategy.upper()}:")
            print(f"   Успешность: {success_count}/{total_count} ({success_rate:.1f}%)")
            
            # Показываем примеры распознанного текста
            for r in strategy_results:
                if r.get('ocr_result', {}).get('cyrillic_found', False):
                    detected = r['ocr_result']['detected_text_combined']
                    print(f"   ✅ Найдена кириллица: {detected}")
                    break
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        best_strategy = max(by_strategy.items(), 
                           key=lambda x: sum(1 for r in x[1] 
                                           if r.get('ocr_result', {}).get('cyrillic_found', False)))
        
        print(f"   Лучшая стратегия: {best_strategy[0]}")
        print(f"   Рекомендация: {'DALL-E 3 справляется с кириллицей' if best_strategy else 'Требуется альтернативное решение'}")


def main():
    """Главная функция"""
    print("🇷🇺 ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ КИРИЛЛИЦЫ DALL-E 3")
    print("Проверяем возможности модели в создании русского текста")
    print()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Ошибка: Не найден OPENAI_API_KEY")
        print("Установите ключ в файле .env")
        return
    
    tester = CyrillicGenerationTester()
    results = tester.run_cyrillic_tests()
    
    print(f"\n✅ Тестирование завершено!")
    print(f"📁 Результаты сохранены в: {tester.test_dir}")
    print(f"🔍 Проверьте сгенерированные изображения для визуальной оценки")


if __name__ == "__main__":
    main() 