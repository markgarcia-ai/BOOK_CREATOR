#!/usr/bin/env python3
"""
Unified Book Generator
Consolidates functionality from various demo and generator scripts
"""

import requests
import json
import time
import sys
from pathlib import Path
from datetime import datetime
import argparse
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from backend.book_styles import get_style, create_custom_style

class BookGenerator:
    """Unified book generator with multiple generation modes"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_connection(self) -> bool:
        """Test if server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def find_server(self) -> Optional[str]:
        """Find running server on different ports"""
        for port in range(8000, 8010):
            try:
                url = f"http://127.0.0.1:{port}"
                response = self.session.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Found server on port {port}")
                    return url
            except:
                continue
        return None
    
    def get_server_features(self) -> Dict[str, Any]:
        """Get server features and configuration"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("features", {}), data.get("config", {})
        except:
            pass
        return {}, {}
    
    def generate_simple_book(
        self,
        topic: str,
        chapters: int = 8,
        words_per_chapter: int = 2000,
        style: str = "modern"
    ) -> Dict[str, Any]:
        """Generate a simple book using the simple workflow"""
        
        print(f"📚 Generating simple book: {topic}")
        print(f"   Chapters: {chapters}")
        print(f"   Words per chapter: {words_per_chapter}")
        print(f"   Style: {style}")
        
        request_data = {
            "topic": topic,
            "chapters": chapters,
            "words_per_chapter": words_per_chapter
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/simple-workflow", 
                json=request_data, 
                timeout=600
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Simple book generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_complete_book(
        self,
        title: str,
        target_audience: str = "General audience",
        style: str = "informative",
        target_pages: int = 10,
        chapters: int = 8,
        book_style: str = "modern",
        custom_style: Optional[Dict[str, str]] = None,
        use_rag: bool = False,
        rag_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete book with all features"""
        
        print(f"📚 Generating complete book: {title}")
        print(f"   Target audience: {target_audience}")
        print(f"   Style: {style}")
        print(f"   Pages: {target_pages}")
        print(f"   Chapters: {chapters}")
        print(f"   Book style: {book_style}")
        if use_rag:
            print(f"   RAG enhanced: Yes")
            if rag_query:
                print(f"   RAG query: {rag_query}")
        
        request_data = {
            "title": title,
            "target_audience": target_audience,
            "style": style,
            "target_pages": target_pages,
            "chapters": chapters,
            "book_style": book_style,
            "use_rag": use_rag
        }
        
        # Add custom style options if provided
        if custom_style:
            for key, value in custom_style.items():
                if value:
                    request_data[key] = value
        
        if rag_query:
            request_data["rag_query"] = rag_query
        
        try:
            print("\n🚀 Starting book generation...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/generate-book", 
                json=request_data, 
                timeout=900
            )
            response.raise_for_status()
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            result = response.json()
            result["generation_time"] = generation_time
            
            return result
            
        except Exception as e:
            print(f"❌ Complete book generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """Upload file for RAG processing"""
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                response = self.session.post(f"{self.base_url}/upload", files=files, timeout=300)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG collection statistics"""
        try:
            response = self.session.get(f"{self.base_url}/rag/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def demo_styles(self, topic: str = "Artificial Intelligence") -> None:
        """Demo all available book styles"""
        print("🎨 Demonstrating all book styles...")
        
        styles = ["academic", "modern", "compact", "ebook", "minimal"]
        
        for style in styles:
            print(f"\n📖 Generating book with {style} style...")
            
            result = self.generate_complete_book(
                title=f"{topic} - {style.title()} Style",
                style="informative",
                target_pages=5,
                chapters=3,
                book_style=style
            )
            
            if result.get("success"):
                print(f"   ✅ {style} style book generated")
                files = result.get("files", {})
                if files.get("html"):
                    print(f"   📄 HTML: {files['html']}")
            else:
                print(f"   ❌ {style} style failed: {result.get('error', 'Unknown error')}")
            
            time.sleep(2)  # Brief pause between generations
    
    def demo_custom_styles(self, topic: str = "Python Programming") -> None:
        """Demo custom style options"""
        print("🎨 Demonstrating custom styles...")
        
        custom_configs = [
            {
                "name": "Technical",
                "font_family": "Monaco",
                "line_height": "1.3",
                "paragraph_spacing": "0.8em",
                "color_scheme": "blue"
            },
            {
                "name": "Academic", 
                "font_family": "Times New Roman",
                "line_height": "1.4",
                "paragraph_spacing": "1.2em",
                "max_width": "700px"
            },
            {
                "name": "Modern",
                "font_family": "Arial",
                "line_height": "1.6", 
                "paragraph_spacing": "1.5em",
                "max_width": "900px",
                "color_scheme": "default"
            }
        ]
        
        for config in custom_configs:
            style_name = config.pop("name")
            print(f"\n📖 Generating book with {style_name} custom style...")
            
            result = self.generate_complete_book(
                title=f"{topic} - {style_name} Custom",
                style="technical",
                target_pages=5,
                chapters=3,
                book_style="modern",
                custom_style=config
            )
            
            if result.get("success"):
                print(f"   ✅ {style_name} custom style book generated")
                files = result.get("files", {})
                if files.get("html"):
                    print(f"   📄 HTML: {files['html']}")
            else:
                print(f"   ❌ {style_name} custom style failed: {result.get('error', 'Unknown error')}")
    
    def demo_rag_enhanced(self, topic: str = "Machine Learning") -> None:
        """Demo RAG-enhanced generation"""
        features, _ = self.get_server_features()
        
        if not features.get("rag_enabled", False):
            print("❌ RAG functionality not available")
            return
        
        print("🔍 Demonstrating RAG-enhanced generation...")
        
        # Check RAG stats
        stats = self.get_rag_stats()
        if stats.get("document_count", 0) == 0:
            print("⚠️  No documents in RAG collection. Consider uploading some source material first.")
        else:
            print(f"📊 RAG Collection: {stats.get('document_count', 0)} documents")
        
        # Generate RAG-enhanced book
        result = self.generate_complete_book(
            title=f"{topic} with RAG Enhancement",
            style="technical",
            target_pages=8,
            chapters=5,
            book_style="academic",
            use_rag=True,
            rag_query=f"{topic} algorithms techniques applications"
        )
        
        if result.get("success"):
            print("✅ RAG-enhanced book generated")
            if result.get("rag_enhanced"):
                print("🔍 RAG enhancement was used")
            files = result.get("files", {})
            for file_type, file_path in files.items():
                if file_path:
                    print(f"📄 {file_type.title()}: {file_path}")
        else:
            print(f"❌ RAG-enhanced generation failed: {result.get('error', 'Unknown error')}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Unified Book Generator")
    parser.add_argument("--server", default="http://127.0.0.1:8000", help="Server URL")
    parser.add_argument("--topic", default="Artificial Intelligence", help="Book topic")
    parser.add_argument("--mode", choices=["simple", "complete", "demo", "styles", "custom", "rag"], 
                       default="complete", help="Generation mode")
    parser.add_argument("--chapters", type=int, default=8, help="Number of chapters")
    parser.add_argument("--pages", type=int, default=10, help="Target pages")
    parser.add_argument("--style", default="informative", help="Writing style")
    parser.add_argument("--book-style", default="modern", help="Book visual style")
    parser.add_argument("--audience", default="General audience", help="Target audience")
    parser.add_argument("--rag", action="store_true", help="Use RAG enhancement")
    parser.add_argument("--upload", help="Upload file for RAG before generation")
    
    args = parser.parse_args()
    
    # Create generator
    generator = BookGenerator(args.server)
    
    # Test connection
    if not generator.test_connection():
        print(f"❌ Cannot connect to server at {args.server}")
        alternative = generator.find_server()
        if alternative:
            generator.base_url = alternative
        else:
            print("💡 Make sure the server is running with: python -m backend.main")
            sys.exit(1)
    
    print(f"✅ Connected to server at {generator.base_url}")
    
    # Upload file if specified
    if args.upload:
        print(f"📤 Uploading file: {args.upload}")
        upload_result = generator.upload_file(args.upload)
        if upload_result.get("success"):
            print(f"✅ File uploaded and processed")
        else:
            print(f"❌ Upload failed: {upload_result.get('error')}")
    
    # Execute based on mode
    if args.mode == "simple":
        result = generator.generate_simple_book(
            topic=args.topic,
            chapters=args.chapters,
            words_per_chapter=2000
        )
        
    elif args.mode == "complete":
        result = generator.generate_complete_book(
            title=args.topic,
            target_audience=args.audience,
            style=args.style,
            target_pages=args.pages,
            chapters=args.chapters,
            book_style=args.book_style,
            use_rag=args.rag
        )
        
    elif args.mode == "demo":
        generator.demo_styles(args.topic)
        return
        
    elif args.mode == "styles":
        generator.demo_styles(args.topic)
        return
        
    elif args.mode == "custom":
        generator.demo_custom_styles(args.topic)
        return
        
    elif args.mode == "rag":
        generator.demo_rag_enhanced(args.topic)
        return
    
    # Print results
    if result.get("success"):
        print(f"\n🎉 Book generation completed!")
        print(f"📚 Title: {result.get('title', args.topic)}")
        if "chapters" in result:
            print(f"📄 Chapters: {result['chapters']}")
        if "total_cost" in result:
            print(f"💰 Cost: ${result['total_cost']:.4f}")
        if "generation_time" in result:
            print(f"⏱️  Time: {result['generation_time']:.1f} seconds")
        
        files = result.get("files", {})
        if files:
            print(f"\n📁 Generated files:")
            for file_type, file_path in files.items():
                if file_path:
                    print(f"  {file_type.title()}: {file_path}")
    else:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 