import sys
import os
import json
import logging
import platform
from pathlib import Path

# Handle Windows console encoding
if platform.system() == 'Windows':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_documentation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DocTest')

# Replace special characters for Windows console
class SafeLogFilter(logging.Filter):
    def filter(self, record):
        if platform.system() == 'Windows':
            if hasattr(record, 'msg'):
                record.msg = record.msg.replace('✓', '[OK]').replace('⚠️', '[WARN]').replace('✗', '[ERROR]')
        return True

# Apply the filter to all handlers
for handler in logging.root.handlers:
    handler.addFilter(SafeLogFilter())

def test_documentation_files():
    """Verify that all required documentation files exist."""
    logger.info("\n=== Testing Documentation Files ===")
    
    required_files = [
        'script/docs.py',
        'lang/en.json',
        'lang/it.json'
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.error(f"[ERROR] Missing file: {file_path}")
            all_files_exist = False
        else:
            logger.info(f"[OK] Found file: {file_path}")
    
    return all_files_exist

def test_translations():
    """Test the translation functionality."""
    logger.info("\n=== Testing Translation System ===")
    
    try:
        # Test English translations
        with open('lang/en.json', 'r', encoding='utf-8') as f:
            en_translations = json.load(f)
            logger.info(f"Loaded {len(en_translations)} English translations")
            
            # Test some key translations
            test_keys = [
                'docs.window_title',
                'docs.error.directory_not_found',
                'docs.error.initialization_failed',
                'docs.error.initialization_failed_message',
                'docs.init_success'
            ]
            
            missing_keys = []
            for key in test_keys:
                if key in en_translations:
                    logger.info(f"[OK] Found translation for '{key}'")
                else:
                    logger.warning(f"[WARN] Missing translation for key: {key}")
                    missing_keys.append(key)
            
            if missing_keys:
                logger.warning(f"[WARN] Missing {len(missing_keys)} out of {len(test_keys)} required translations")
        
        # Test Italian translations
        with open('lang/it.json', 'r', encoding='utf-8') as f:
            it_translations = json.load(f)
            logger.info(f"Loaded {len(it_translations)} Italian translations")
            
            # Check if all required keys are present
            missing_keys = [k for k in en_translations if k not in it_translations]
            if missing_keys:
                logger.warning(f"[WARN] Missing {len(missing_keys)} Italian translations")
                for i, key in enumerate(missing_keys[:3], 1):
                    logger.warning(f"  {i}. {key}")
                if len(missing_keys) > 3:
                    logger.warning(f"  ... and {len(missing_keys) - 3} more")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Translation test failed: {e}", exc_info=True)
        return False

def test_documentation_content():
    """Test the content of the documentation."""
    logger.info("\n=== Testing Documentation Content ===")
    
    try:
        with open('script/docs.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for required sections
            sections = [
                'class DocsDialog',
                'def _get_english_help',
                'def _get_italian_help',
                'def load_documentation',
                'def _get_docs_directory',
                'def init_ui',
                'def retranslate_ui'
            ]
            
            all_sections_found = True
            for section in sections:
                if section in content:
                    logger.info(f"[OK] Found section: {section}")
                else:
                    logger.warning(f"[WARN] Missing section: {section}")
                    all_sections_found = False
            
            # Check for required methods in the class
            class_methods = [
                '__init__',
                'tr',
                'load_documentation',
                'change_language',
                'closeEvent'
            ]
            
            for method in class_methods:
                if f'def {method}(' in content:
                    logger.info(f"[OK] Found method: {method}")
                else:
                    logger.warning(f"[WARN] Missing method: {method}")
                    all_sections_found = False
            
            return all_sections_found
            
    except Exception as e:
        logger.error(f"[ERROR] Documentation content test failed: {e}")
        return False

def main():
    """Run all documentation tests."""
    logger.info("Starting Documentation Tests")
    
    # Run tests
    tests = [
        ("Documentation Files", test_documentation_files),
        ("Translation System", test_translations),
        ("Documentation Content", test_documentation_content)
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