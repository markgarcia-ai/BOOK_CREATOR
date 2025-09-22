#!/usr/bin/env python3
"""
Test script for the complete RAG-enhanced book creation workflow
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

def test_rag_analysis_tools():
    """Test Phase 1: RAG Analysis Tools"""
    print("🧪 Testing Phase 1: RAG Analysis Tools")
    
    try:
        from backend.reasonning_agent import analyze_rag_content, generate_content_summary, explore_rag_sources
        from rag.retrieve import get_collection_stats
        
        # Test RAG stats
        stats = get_collection_stats()
        print(f"📊 RAG Stats: {stats}")
        
        # Test content analysis (will work even with empty DB)
        print("🔍 Testing content analysis...")
        analysis = analyze_rag_content("claude-3-5-haiku-20241022", sample_size=5)
        print(f"📋 Analysis result: {analysis.get('status', 'unknown')}")
        
        # Test source exploration
        print("🗂️  Testing source exploration...")
        sources = explore_rag_sources("claude-3-5-haiku-20241022", max_sources=3)
        print(f"📁 Sources result: {sources.get('status', 'unknown')}")
        
        print("✅ Phase 1 tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 test failed: {e}")
        return False

def test_rag_aware_planning():
    """Test Phase 2: RAG-Aware Planning"""
    print("\n🧪 Testing Phase 2: RAG-Aware Planning")
    
    try:
        from backend.planner import generate_rag_aware_outline, generate_outline, validate_outline
        
        # Test regular outline generation
        print("📝 Testing regular outline generation...")
        outline, metadata = generate_outline(
            "claude-3-5-haiku-20241022",
            "Machine Learning Fundamentals",
            chapters=3,
            words_per_chapter=1000
        )
        print(f"📚 Generated outline: {outline.get('title', 'No title')}")
        
        # Test outline validation
        print("✅ Testing outline validation...")
        validation = validate_outline(outline)
        print(f"🔍 Validation: {validation.get('valid', False)} - {len(validation.get('issues', []))} issues")
        
        # Test RAG-aware outline (with mock summary)
        print("🎯 Testing RAG-aware outline...")
        mock_summary = "This RAG database contains content about machine learning algorithms, data preprocessing, and model evaluation techniques."
        rag_outline, rag_metadata = generate_rag_aware_outline(
            "claude-3-5-haiku-20241022",
            "Machine Learning Fundamentals",
            mock_summary,
            chapters=3,
            words_per_chapter=1000
        )
        print(f"📚 RAG-aware outline: {rag_outline.get('title', 'No title')}")
        
        print("✅ Phase 2 tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 test failed: {e}")
        return False

def test_agent_workflow():
    """Test Phase 3: Complete Agent Workflow"""
    print("\n🧪 Testing Phase 3: Complete Agent Workflow")
    
    try:
        from backend.reasonning_agent import run_agent
        
        # Test agent with RAG analysis goal
        print("🤖 Testing agent with RAG analysis...")
        goal = "Analyze the RAG database content and create a summary of available information"
        
        # Run with limited steps for testing
        trace, result = run_agent(goal, max_steps=5)
        
        print(f"🎯 Agent result: {result}")
        print(f"📊 Agent steps: {len(trace)}")
        
        # Check if agent used RAG analysis tools
        rag_tools_used = any(
            step.get("action", {}).get("tool") in ["analyze_rag_content", "generate_content_summary", "explore_rag_sources"]
            for step in trace
        )
        print(f"🔍 RAG tools used: {rag_tools_used}")
        
        print("✅ Phase 3 tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 3 test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Complete RAG Workflow Tests")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set - some tests may fail")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
    
    # Run tests
    phase1_ok = test_rag_analysis_tools()
    phase2_ok = test_rag_aware_planning()
    phase3_ok = test_agent_workflow()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print(f"Phase 1 (RAG Analysis): {'✅ PASS' if phase1_ok else '❌ FAIL'}")
    print(f"Phase 2 (RAG Planning): {'✅ PASS' if phase2_ok else '❌ FAIL'}")
    print(f"Phase 3 (Agent Workflow): {'✅ PASS' if phase3_ok else '❌ FAIL'}")
    
    if all([phase1_ok, phase2_ok, phase3_ok]):
        print("\n🎉 ALL TESTS PASSED! RAG workflow is ready!")
        print("\n🚀 Next steps:")
        print("1. Add content to RAG: python rag/ingest.py path/to/your/document.pdf")
        print("2. Test complete workflow: python scripts/cli.py agent 'Analyze RAG content and create a book'")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return all([phase1_ok, phase2_ok, phase3_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
