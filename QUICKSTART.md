# Book Creator - Quick Start Guide

## 🚀 Complete AI-Powered Book Creation System

This system uses **Anthropic Claude** to create complete books with:
- **Intelligent Planning**: AI-generated outlines and structure
- **RAG-Powered Writing**: Fact-checked content using your sources
- **Quality Control**: Automated checks and validation
- **Multiple Formats**: PDF, EPUB, DOCX export
- **Cost Tracking**: Monitor API usage and costs

## ⚡ Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
# Already done if you followed the setup
source .venv/bin/activate
pip install anthropic python-dotenv
```

### 2. Set Your API Key
```bash
# Create .env file with your Anthropic API key
echo "ANTHROPIC_API_KEY=your_actual_api_key_here" > .env
```

### 3. Test the System
```bash
# Test everything is working
python test_setup.py

# Start the API server
python -m backend.main

# In another terminal, test the CLI
python scripts/cli.py health
```

## 📚 How to Create Your Book

### Method 1: Simple Workflow (Recommended for beginners)
```bash
# Create a complete book in one command
python scripts/cli.py simple "Machine Learning Fundamentals" --chapters 5 --words-per-chapter 2000
```

### Method 2: Step-by-Step Workflow
```bash
# 1. Create project
python scripts/cli.py create "My Book Title" --chapters 8

# 2. Add your research materials
python scripts/cli.py ingest path/to/your/research.pdf
python scripts/cli.py ingest path/to/your/notes.md

# 3. Generate outline
python scripts/cli.py outline "Machine Learning" --chapters 8 --words-per-chapter 2500

# 4. Use agent to write and build
python scripts/cli.py agent "Write Chapter 1 using the uploaded research and export to PDF"
```

### Method 3: Advanced Agent Commands
```bash
# Complex multi-step tasks
python scripts/cli.py agent "Create a complete book about Python programming with 6 chapters, include code examples, and export to both PDF and EPUB"

# Specific chapter writing
python scripts/cli.py agent "Draft Chapter 3 about data structures using the uploaded research papers, include 2 diagrams, and save to chapters/03-data-structures.md"
```

## 🔧 Available Commands

### Core Commands
- `health` - Check system status
- `status` - Get project status
- `create` - Create new book project
- `outline` - Generate book outline
- `agent` - Run reasoning agent
- `simple` - Complete workflow in one command
- `build` - Build book to PDF/EPUB/DOCX
- `ingest` - Add files to RAG system
- `retrieve` - Search your sources

### Examples
```bash
# Check everything is working
python scripts/cli.py health

# See what's in your project
python scripts/cli.py status

# Create a book about AI
python scripts/cli.py simple "Artificial Intelligence" --chapters 6

# Build existing content
python scripts/cli.py build pdf
python scripts/cli.py build epub
```

## 📁 Project Structure
```
book_creator/
├── backend/           # Core AI system
│   ├── llm.py        # Claude integration
│   ├── tools.py      # File operations
│   ├── writer.py     # Content generation
│   ├── planner.py    # Outline generation
│   └── reasonning_agent.py  # Orchestration
├── rag/              # Knowledge system
│   ├── ingest.py     # Add sources
│   └── retrieve.py   # Search sources
├── book/             # Your book content
│   ├── chapters/     # Generated chapters
│   ├── config.yml    # Book metadata
│   └── toc.yaml      # Table of contents
├── exports/          # Final books (PDF, EPUB, etc.)
└── scripts/cli.py    # Command interface
```

## 🎯 Testing with Your Own Content

### Step 1: Prepare Your Sources
```bash
# Add your research materials
python scripts/cli.py ingest "path/to/your/research.pdf"
python scripts/cli.py ingest "path/to/your/notes.txt"
python scripts/cli.py ingest "https://relevant-article.com"
```

### Step 2: Create Your Book
```bash
# Simple approach - let AI do everything
python scripts/cli.py simple "Your Book Topic" --chapters 5 --words-per-chapter 2000

# Or step by step
python scripts/cli.py create "Your Book Title"
python scripts/cli.py outline "Your Topic" --chapters 5
python scripts/cli.py agent "Write all chapters using my uploaded sources and build PDF"
```

### Step 3: Review and Export
```bash
# Check what was created
python scripts/cli.py status

# Build different formats
python scripts/cli.py build pdf
python scripts/cli.py build epub
python scripts/cli.py build docx
```

## 💡 Tips for Best Results

1. **Start Simple**: Use the `simple` command first to see how it works
2. **Add Good Sources**: Upload high-quality research materials
3. **Be Specific**: Give clear goals to the agent
4. **Check Progress**: Use `status` to see what's been created
5. **Iterate**: Run multiple agent commands to refine content

## 🚨 Troubleshooting

### API Key Issues
```bash
# Make sure your .env file exists and has the right key
cat .env
# Should show: ANTHROPIC_API_KEY=your_key_here
```

### Import Errors
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate
python test_setup.py
```

### Build Errors
```bash
# Make sure Pandoc is installed
brew install pandoc  # macOS
# or
sudo apt install pandoc  # Ubuntu
```

## 🎉 You're Ready!

The system is now complete and ready to create your book. Start with:

```bash
python scripts/cli.py simple "Your Book Topic" --chapters 5
```

This will create a complete book with AI-generated content, proper citations, and export it to PDF. The system handles everything automatically!
