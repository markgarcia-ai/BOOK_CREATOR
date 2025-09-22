#!/usr/bin/env python3
"""
Test script to verify the book creator setup
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from backend.settings import ANTHROPIC_API_KEY, ROOT, BOOK
        print("✓ Settings imported")
    except Exception as e:
        print(f"✗ Settings import failed: {e}")
        return False
    
    try:
        from backend.llm import chat, complete_json
        print("✓ LLM module imported")
    except Exception as e:
        print(f"✗ LLM import failed: {e}")
        return False
    
    try:
        from backend.tools import write_file, build_book
        print("✓ Tools imported")
    except Exception as e:
        print(f"✗ Tools import failed: {e}")
        return False
    
    try:
        from rag.retrieve import fact_pack
        print("✓ RAG retrieve imported")
    except Exception as e:
        print(f"✗ RAG retrieve import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist"""
    print("\nTesting directories...")
    
    required_dirs = [
        "book", "book/chapters", "book/assets/img", 
        "exports", "data", "logs", "rag/db"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} (missing)")
            all_exist = False
    
    return all_exist

def test_api_key():
    """Test API key configuration"""
    print("\nTesting API key...")
    
    if os.getenv("ANTHROPIC_API_KEY"):
        print("✓ ANTHROPIC_API_KEY is set")
        return True
    else:
        print("✗ ANTHROPIC_API_KEY not found")
        print("  Please set your API key:")
        print("  export ANTHROPIC_API_KEY='your_key_here'")
        print("  or create a .env file with ANTHROPIC_API_KEY=your_key_here")
        return False

def main():
    """Run all tests"""
    print("Book Creator Setup Test")
    print("=" * 30)
    
    tests = [
        test_imports,
        test_directories,
        test_api_key
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 30)
    if all(results):
        print("✓ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Set your ANTHROPIC_API_KEY in .env file")
        print("2. Run: python -m backend.main (to start API)")
        print("3. Run: python scripts/cli.py health (to test CLI)")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
