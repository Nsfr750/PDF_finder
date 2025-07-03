import os
import re
from pathlib import Path

def extract_strings():
    """Extract all translatable strings from Python files."""
    strings = set()
    tr_pattern = re.compile(r'(?:self\.)?tr\(["\'](.*?)["\']\)')
    
    # Find all Python files in the project
    for root, _, files in os.walk('.'):
        # Skip virtual environment and other non-source directories
        if any(skip in root for skip in ['venv', '.git', '__pycache__', 'build', 'dist']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = tr_pattern.findall(content)
                        strings.update(matches)
                except Exception as e:
                    print(f"Error processing {file}: {e}")
    
    # Filter out empty strings and very short strings
    return sorted({s for s in strings if len(s) > 1 and not s.isspace()}, key=str.lower)

def update_translation_file(file_path, strings, is_english=True):
    """Update a translation file with the given strings."""
    # Read existing translations
    existing = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract existing translations
        pattern = re.compile(
            r'<message>\s*<source>(.*?)</source>\s*<translation>(.*?)</translation>',
            re.DOTALL
        )
        existing = {m.group(1): m.group(2) for m in pattern.finditer(content)}
    
    # Create or update the translation file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<!DOCTYPE TS>\n')
        f.write('<TS version="2.1" language="en">\n' if is_english else '<TS version="2.1" language="it">\n')
        f.write('<context>\n')
        f.write('    <name>MainWindow</name>\n')
        
        for s in strings:
            translation = s if is_english else existing.get(s, '')
            f.write('    <message>\n')
            f.write(f'        <source>{s}</source>\n')
            f.write(f'        <translation>{translation}</translation>\n')
            f.write('    </message>\n')
        
        f.write('</context>\n')
        f.write('</TS>\n')

def main():
    # Get all translatable strings
    strings = extract_strings()
    print(f"Found {len(strings)} translatable strings")
    
    # Update English translations
    en_file = os.path.join('app_qt', 'translations', 'pdf_finder_en.ts')
    update_translation_file(en_file, strings, is_english=True)
    print(f"Updated {en_file}")
    
    # Update Italian translations
    it_file = os.path.join('app_qt', 'translations', 'pdf_finder_it.ts')
    update_translation_file(it_file, strings, is_english=False)
    print(f"Updated {it_file}")

if __name__ == '__main__':
    main()
