#!/usr/bin/env python3
"""
Book Creator Server Launcher
Unified server startup with automatic feature detection
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path
sys.path.append(str(Path(__file__).parent))

def main():
    """Start the unified Book Creator server"""
    
    print("🚀 Starting Book Creator Server...")
    print("=" * 50)
    
    # Show configuration
    rag_enabled = os.getenv("RAG_ENABLED", "true").lower() == "true"
    enhanced_logging = os.getenv("ENHANCED_LOGGING", "true").lower() == "true"
    pdf_generation = os.getenv("PDF_GENERATION", "true").lower() == "true"
    
    print("📋 Server Configuration:")
    print(f"   🔍 RAG Enhancement: {'✅ Enabled' if rag_enabled else '❌ Disabled'}")
    print(f"   📝 Enhanced Logging: {'✅ Enabled' if enhanced_logging else '❌ Disabled'}")
    print(f"   📄 PDF Generation: {'✅ Enabled' if pdf_generation else '❌ Disabled'}")
    print()
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment")
        print("   Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        print()
    
    # Start server
    try:
        print("🌐 Server starting on http://127.0.0.1:8000")
        print("📚 Ready to generate books!")
        print("=" * 50)
        
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
