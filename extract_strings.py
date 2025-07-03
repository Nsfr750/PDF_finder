import os
import re
from pathlib import Path

def extract_strings_from_file(file_path):
    """Extract all strings wrapped in self.tr() or tr() from a Python file."""
    strings = set()
    tr_pattern = re.compile(r'(?:self\.)?tr\(["\'](.*?)["\']\)')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = tr_pattern.findall(content)
            strings.update(matches)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return strings

def find_python_files(directory):
    """Find all Python files in the given directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        # Skip virtual environment directories
        if 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Find all Python files
    python_files = find_python_files(project_root)
    
    # Extract all translatable strings
    all_strings = set()
    for file_path in python_files:
        strings = extract_strings_from_file(file_path)
        all_strings.update(strings)
    
    # Filter out empty strings and very short strings
    all_strings = {s for s in all_strings if len(s) > 1 and not s.isspace()}
    
    # Sort strings alphabetically
    sorted_strings = sorted(all_strings, key=str.lower)
    
    # Print the results
    print("Found", len(sorted_strings), "unique translatable strings:")
    print('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>')
    print('<TS version="2.1" language="en">')
    print('<context>\n    <name>MainWindow</name>')
    
    for s in sorted_strings:
        print(f'    <message>')
        print(f'        <source>{s}</source>')
        print(f'        <translation>{s}</translation>')
        print(f'    </message>')
    
    print('</context>\n</TS>')

if __name__ == '__main__':
    main()
