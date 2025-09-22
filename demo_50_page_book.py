#!/usr/bin/env python3
"""
Demo script for generating a 50-page book from uploaded markdown source
"""

import requests
import os
from pathlib import Path

API = "http://127.0.0.1:8000"

def upload_source_file(file_path: str):
    """Upload a markdown source file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    print(f"📤 Uploading {file_path}...")
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'text/markdown')}
        response = requests.post(f"{API}/upload-source", files=files, timeout=60)
        response.raise_for_status()
    
    data = response.json()
    print(f"✅ Upload successful: {data['filename']} ({data['file_size']} bytes)")
    return data['file_path']

def generate_book_from_source(topic: str, source_file: str = None):
    """Generate a 50-page book"""
    print(f"\n🚀 Generating 50-page book on: {topic}")
    
    payload = {
        "topic": topic,
        "target_audience": "intermediate developers",
        "style": "comprehensive",
        "target_pages": 50
    }
    
    if source_file:
        payload["source_file_path"] = source_file
        print(f"📚 Using source file: {source_file}")
    
    print("🤖 AI is working... (this may take 5-10 minutes)")
    response = requests.post(f"{API}/generate-book", json=payload, timeout=1800)
    response.raise_for_status()
    
    data = response.json()
    
    if data.get("success"):
        print(f"\n🎉 SUCCESS! Generated: {data['book_title']}")
        print(f"📄 Pages: {data['estimated_pages']}")
        print(f"📑 Chapters: {data['total_chapters']}")
        print(f"💰 Cost: ${data.get('total_cost', 0):.4f}")
        
        print(f"\n📁 Files created:")
        for format_type, file_path in data['files_created'].items():
            if file_path:
                print(f"  • {format_type.upper()}: {file_path}")
        
        return data
    else:
        print("❌ Generation failed")
        return None

if __name__ == "__main__":
    print("🎯 50-Page Book Generation Demo")
    print("=" * 50)
    
    # Example 1: Generate from scratch
    print("\n📝 Example 1: Generate from scratch")
    result1 = generate_book_from_source("Advanced Python Programming")
    
    # Example 2: Upload and use source file
    print("\n📝 Example 2: Upload source file and generate")
    source_file = "uploads/sample_source.md"
    if os.path.exists(source_file):
        uploaded_path = upload_source_file(source_file)
        if uploaded_path:
            result2 = generate_book_from_source("Python Programming Guide", uploaded_path)
    
    print("\n🎯 Demo complete! Check the exports/ folder for your generated books.")
