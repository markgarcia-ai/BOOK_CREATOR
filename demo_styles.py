#!/usr/bin/env python3
"""
Demo script showing different book styles and formatting options
"""

import requests
import time

API = "http://127.0.0.1:8000"

def demo_book_styles():
    """Demonstrate different book styles"""
    
    print("🎨 BOOK STYLE DEMONSTRATION")
    print("=" * 50)
    
    # Get available styles
    try:
        response = requests.get(f"{API}/styles")
        styles_data = response.json()
        
        print(f"\n📚 Available Styles:")
        for style_name, description in styles_data['available_styles'].items():
            print(f"  • {style_name.title()}: {description}")
        
    except Exception as e:
        print(f"❌ Error getting styles: {e}")
        return
    
    # Demo topics for different styles
    demos = [
        {
            "topic": "Python Programming Basics",
            "style": "academic",
            "description": "Academic style with tight spacing"
        },
        {
            "topic": "Machine Learning Fundamentals", 
            "style": "modern",
            "description": "Modern style with generous spacing"
        },
        {
            "topic": "Data Science Techniques",
            "style": "compact", 
            "description": "Compact style for maximum content"
        },
        {
            "topic": "Statistics and Probability",
            "style": "ebook",
            "description": "E-book optimized style"
        },
        {
            "topic": "Web Development Guide",
            "style": "minimal",
            "description": "Clean minimal style"
        }
    ]
    
    print(f"\n🚀 Generating demo books with different styles...")
    
    for i, demo in enumerate(demos, 1):
        print(f"\n📖 Demo {i}/5: {demo['topic']} ({demo['style']} style)")
        print(f"   Description: {demo['description']}")
        
        try:
            payload = {
                "topic": demo['topic'],
                "target_audience": "students",
                "style": "educational",
                "target_pages": 5,
                "book_style": demo['style']
            }
            
            print(f"   🤖 Generating...")
            response = requests.post(f"{API}/generate-book", json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ Success! Cost: ${data.get('total_cost', 0):.4f}")
                    print(f"   📁 Files: {data['files_created']}")
                else:
                    print(f"   ❌ Generation failed")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(2)
    
    print(f"\n🎯 CUSTOM STYLE DEMONSTRATION")
    print("=" * 50)
    
    # Demo custom styling
    custom_demos = [
        {
            "topic": "Custom Academic Style",
            "custom_style": {
                "font_family": "Times New Roman",
                "line_height": "1.4",
                "paragraph_spacing": "0.8em",
                "header_spacing": "1.5em",
                "max_width": "700px",
                "color_scheme": "default"
            }
        },
        {
            "topic": "Custom Dark Theme",
            "custom_style": {
                "font_family": "Arial",
                "line_height": "1.6",
                "paragraph_spacing": "1.5em",
                "header_spacing": "2em",
                "max_width": "800px",
                "color_scheme": "dark"
            }
        }
    ]
    
    for i, demo in enumerate(custom_demos, 1):
        print(f"\n🎨 Custom Demo {i}/2: {demo['topic']}")
        print(f"   Custom Style: {demo['custom_style']}")
        
        try:
            payload = {
                "topic": demo['topic'],
                "target_audience": "developers",
                "style": "technical",
                "target_pages": 3,
                "book_style": "modern",
                "custom_style": demo['custom_style']
            }
            
            print(f"   🤖 Generating...")
            response = requests.post(f"{API}/generate-book", json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ Success! Cost: ${data.get('total_cost', 0):.4f}")
                    print(f"   📁 Files: {data['files_created']}")
                else:
                    print(f"   ❌ Generation failed")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)
    
    print(f"\n🎉 STYLE DEMONSTRATION COMPLETE!")
    print(f"📁 Check the exports/ folder for all generated books")
    print(f"🌐 Open the HTML files to see the different styles in action")

if __name__ == "__main__":
    demo_book_styles()
