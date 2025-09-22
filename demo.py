#!/usr/bin/env python3
"""
Demo script showing the book creator in action
"""
import os
import sys
from pathlib import Path

def create_demo_content():
    """Create some demo content to test with"""
    print("Creating demo content...")
    
    # Create a demo research file
    demo_research = """
# Machine Learning Research Notes

## Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. The key concepts include:

1. **Supervised Learning**: Learning with labeled examples
2. **Unsupervised Learning**: Finding patterns in unlabeled data  
3. **Reinforcement Learning**: Learning through interaction and feedback

## Key Algorithms

### Linear Regression
Linear regression is used for predicting continuous values. It finds the best line through data points.

### Decision Trees
Decision trees make decisions by asking a series of yes/no questions about the data.

### Neural Networks
Neural networks are inspired by the human brain and can learn complex patterns.

## Applications

Machine learning is used in:
- Image recognition
- Natural language processing
- Recommendation systems
- Autonomous vehicles
- Medical diagnosis

## Future Trends

The field is rapidly evolving with advances in:
- Deep learning
- Transfer learning
- Explainable AI
- Edge computing
"""
    
    # Save demo research
    research_file = Path("data/demo_research.md")
    research_file.parent.mkdir(exist_ok=True)
    research_file.write_text(demo_research)
    
    print(f"✓ Created demo research: {research_file}")
    return str(research_file)

def run_demo():
    """Run a complete demo"""
    print("Book Creator Demo")
    print("=" * 40)
    
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set!")
        print("Please set your API key:")
        print("export ANTHROPIC_API_KEY='your_key_here'")
        print("or create a .env file")
        return False
    
    # Create demo content
    research_file = create_demo_content()
    
    print("\n🚀 Demo Commands to Try:")
    print("=" * 40)
    
    print("\n1. Start the API server (in one terminal):")
    print("   python -m backend.main")
    
    print("\n2. Test the system (in another terminal):")
    print("   python scripts/cli.py health")
    
    print("\n3. Ingest the demo research:")
    print(f"   python scripts/cli.py ingest {research_file}")
    
    print("\n4. Create a simple book:")
    print("   python scripts/cli.py simple 'Machine Learning Basics' --chapters 3 --words-per-chapter 1500")
    
    print("\n5. Or use the agent for more control:")
    print("   python scripts/cli.py agent 'Create a 3-chapter book about machine learning using the demo research, include examples, and export to PDF'")
    
    print("\n6. Check what was created:")
    print("   python scripts/cli.py status")
    
    print("\n7. Build the book:")
    print("   python scripts/cli.py build pdf")
    
    print("\n" + "=" * 40)
    print("🎉 The system is ready! Follow the commands above to create your first AI-generated book.")
    
    return True

if __name__ == "__main__":
    run_demo()
