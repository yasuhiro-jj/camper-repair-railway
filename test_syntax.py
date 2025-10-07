#!/usr/bin/env python3
import ast
import sys

def check_syntax(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to parse the file
        ast.parse(source, filename)
        print(f"✅ {filename} syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return False

if __name__ == "__main__":
    check_syntax("app.py")
