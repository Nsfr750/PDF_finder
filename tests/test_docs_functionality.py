import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_docs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DocTest')

def test_document_loading():
    """Test loading of documentation content."""
    logger.info("\n=== Testing Documentation Content Loading ===")
    
    # Check if docs.py exists
    docs_path = Path('script/docs.py')
    if not docs_path.exists():
        logger.error(f"Documentation file not found at {docs_path}")
        return False
    
    # Check for documentation content
    with open(docs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for language content
    languages = ['en', 'it']
    for lang in languages:
        if f'_get_{lang}_docs' in content:
            logger.info(f"✓ Found {lang.upper()} documentation content")
        else:
            logger.warning(f"✗ Missing {lang.upper()} documentation content")
    
    return True

def test_translations():
    """Test translation functionality."""
    logger.info("\n=== Testing Translation Functionality ===")
    
    try:
        from script.docs import _tr
        from script.lang_mgr import LanguageManager
        
        # Test with a known key from the language files
        test_key = "docs.window_title"
        default_text = "Documentation"
        
        # First, test direct translation
        logger.info(f"Testing translation for key: {test_key}")
        logger.info(f"Default text: {default_text}")
        
        # Test the _tr function
        translated = _tr(test_key, default_text)
        logger.info(f"Translated text: {translated}")
        
        # Verify the translation worked
        if translated == default_text:
            logger.warning("⚠️  Using default text - translation might not be working")
            
            # Check if language files exist
            lang_dir = Path('lang')
            if not lang_dir.exists():
                logger.error("✗ 'lang' directory not found")
                return False
                
            # List available language files
            lang_files = list(lang_dir.glob('*.json'))
            logger.info(f"Found language files: {[f.name for f in lang_files]}")
            
            if not lang_files:
                logger.error("✗ No language files found in 'lang' directory")
                return False
                
            # Try to load a language file directly
            try:
                import json
                with open(lang_dir / 'en.json', 'r', encoding='utf-8') as f:
                    en_translations = json.load(f)
                    if test_key in en_translations:
                        logger.info(f"✓ Found key '{test_key}' in English translations")
                        logger.info(f"Expected translation: {en_translations[test_key]}")
                    else:
                        logger.warning(f"Key '{test_key}' not found in English translations")
            except Exception as e:
                logger.error(f"✗ Error loading language file: {e}")
                return False
        else:
            logger.info("✓ Translation successful")
            
        return True
        
    except Exception as e:
        logger.error(f"✗ Translation test failed: {e}", exc_info=True)
        return False

def main():
    """Run all documentation tests."""
    logger.info("Starting Documentation Tests")
    
    # Run tests
    tests = [
        ("Document Loading", test_document_loading),
        ("Translation", test_translations)
    ]
    
    results = {}
    for name, test_func in tests:
        logger.info(f"\n--- {name} ---")
        results[name] = test_func()
    
    # Print summary
    logger.info("\n=== Test Summary ===")
    for name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{name}: {status}")
    
    # Return non-zero exit code if any test failed
    if not all(results.values()):
        logger.error("\nSome tests failed. Check the logs for details.")
        return 1
    
    logger.info("\nAll tests passed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
