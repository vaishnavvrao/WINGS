#!/usr/bin/env python3
"""
Script to find all instances where vaex is being imported or referenced
in the WINGS repository.

Usage:
    python scripts/find_vaex_imports.py

This script searches for:
- import vaex
- from vaex import ...
- Any other references to vaex in code

It searches in:
- All Python (.py) files
- All Jupyter notebooks (.ipynb)
"""

import os
import re
import json
import sys
from pathlib import Path


def search_python_file(filepath):
    """Search for vaex imports in Python files."""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            in_docstring = False
            docstring_char = None
            
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()
                
                # Track docstrings to exclude them from search
                if '"""' in stripped or "'''" in stripped:
                    if not in_docstring:
                        in_docstring = True
                        docstring_char = '"""' if '"""' in stripped else "'''"
                    elif docstring_char in stripped:
                        in_docstring = False
                        docstring_char = None
                        continue
                
                # Skip comments and docstrings
                if in_docstring or stripped.startswith('#'):
                    continue
                
                # Look for actual import statements (not in comments)
                if re.search(r'^(import\s+vaex|from\s+vaex)', stripped):
                    results.append({
                        'file': str(filepath),
                        'line': line_num,
                        'content': line.strip(),
                        'type': 'import'
                    })
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
    return results


def search_notebook(filepath):
    """Search for vaex in Jupyter notebooks."""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        for cell_idx, cell in enumerate(notebook.get('cells', [])):
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                for line_num, line in enumerate(source.split('\n'), 1):
                    if re.search(r'\b(import\s+vaex|from\s+vaex)', line):
                        results.append({
                            'file': str(filepath),
                            'cell': cell_idx,
                            'line': line_num,
                            'content': line.strip(),
                            'type': 'import'
                        })
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
    return results


def main():
    """Main function to search for vaex imports."""
    # Get repository root (parent of scripts directory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    print(f"Searching for vaex imports in: {repo_root}")
    print("=" * 80)
    
    all_results = []
    python_files_count = 0
    notebook_files_count = 0
    
    # Search Python files and notebooks
    for root, dirs, files in os.walk(repo_root):
        # Skip .git directory
        dirs[:] = [d for d in dirs if d != '.git']
        
        for file in files:
            filepath = Path(root) / file
            
            if file.endswith('.py'):
                python_files_count += 1
                results = search_python_file(filepath)
                all_results.extend(results)
            elif file.endswith('.ipynb'):
                notebook_files_count += 1
                results = search_notebook(filepath)
                all_results.extend(results)
    
    # Print summary
    print(f"Files searched:")
    print(f"  Python files (.py): {python_files_count}")
    print(f"  Jupyter notebooks (.ipynb): {notebook_files_count}")
    print()
    
    # Print results
    if not all_results:
        print("✓ No vaex imports found in the repository.")
        return 0
    else:
        print(f"✗ Found {len(all_results)} vaex import(s):")
        print("=" * 80)
        
        for result in all_results:
            if 'cell' in result:
                print(f"\nFile: {result['file']}")
                print(f"  Location: Cell {result['cell']}, Line {result['line']}")
                print(f"  Content: {result['content']}")
            else:
                print(f"\nFile: {result['file']}")
                print(f"  Line: {result['line']}")
                print(f"  Content: {result['content']}")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
