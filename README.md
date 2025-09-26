# 📚 Book Creator - AI-Powered Book Generation System

A comprehensive, AI-powered book creation system that generates complete books using Claude (Anthropic API) with multiple styling options, mathematical equation support, and optional RAG enhancement.

## 🌟 Features

✅ **AI-Powered Writing** - Intelligent content generation with Claude  
✅ **Multiple Book Styles** - Academic, Modern, Compact, E-book, Minimal  
✅ **Mathematical Equations** - MathJax support for LaTeX equations  
✅ **Professional HTML** - Beautiful, responsive book layouts  
✅ **Cost Tracking** - Real-time API usage and cost monitoring  
✅ **Timestamped Output** - Organized file structure with timestamps  
✅ **Configuration-Driven** - Environment-based settings  

## 🚀 Complete Setup Guide

### Step 1: Project Setup
```bash
# Navigate to the project directory
cd book_creator

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Step 2: Environment Configuration
```bash
# Load your API key from .env file
source .env

# Verify API key is loaded
echo $ANTHROPIC_API_KEY
```

### Step 3: Server Management
```bash
# Kill any existing server processes
pkill -f "python start_server.py"

# Start the server
python start_server.py
```

**Expected output:**
```
🚀 Starting Book Creator Server...
==================================================
📋 Server Configuration:
   🔍 RAG Enhancement: ✅ Enabled
   📝 Enhanced Logging: ✅ Enabled
   📄 PDF Generation: ✅ Enabled

🌐 Server starting on http://127.0.0.1:8000
📚 Ready to generate books!
==================================================
```

### Step 4: Test System Health
**Open a new terminal** and run:
```bash
cd book_creator
source .venv/bin/activate
python scripts/cli.py health
```

**Expected output:**
```
✓ API is healthy
Version: 4.0.0

📋 Available Features:
Feature                Status
─────────────────────────────
Rag Enabled           ✅ Enabled
Enhanced Logging       ✅ Enabled
Pdf Generation         ✅ Enabled
```

## 📖 Complete Usage Example (No RAG)

Here's a detailed walkthrough of generating a complete book without using RAG:

### Example: Generate a Technical Book

```bash
# Generate a technical book with 4 chapters
python scripts/cli.py simple "Introduction to Machine Learning" --chapters 4 --words-per-chapter 800

# Generate with source content for more focused results
python scripts/cli.py simple "AI Foundations" --chapters 7 --words-per-chapter 800 --source-file ai_foundations.md
```

**This will create:**
```
exports/introduction_to_machine_learning_20241221_143052/
├── introduction_to_machine_learning_20241221_143052.md
├── introduction_to_machine_learning_20241221_143052.html
├── introduction_to_machine_learning_20241221_143052_academic.html
├── introduction_to_machine_learning_20241221_143052_modern.html
├── introduction_to_machine_learning_20241221_143052_compact.html
└── introduction_to_machine_learning_20241221_143052_ebook.html
```

### Example: Generate with Custom Styling

```bash
# Generate book with specific style preferences
python scripts/cli.py generate-book "Python Data Science Guide" \
  --chapters 5 \
  --target-pages 15 \
  --book-style academic \
  --font-family "Times New Roman" \
  --line-height "1.4" \
  --color-scheme "blue"
```

## 📁 File Structure After Generation

```
book_creator/
├── exports/                           # Generated books
│   └── [topic]_[timestamp]/           # Timestamped folders
│       ├── [topic]_[timestamp].md     # Markdown source
│       ├── [topic]_[timestamp].html   # Main styled HTML
│       ├── [topic]_[timestamp]_academic.html
│       ├── [topic]_[timestamp]_modern.html
│       ├── [topic]_[timestamp]_compact.html
│       └── [topic]_[timestamp]_ebook.html
├── backend/                           # Core system
├── scripts/cli.py                     # Command interface
└── start_server.py                    # Server launcher
```

## 🎨 Available Book Styles

| Style | Description | Font | Use Case |
|-------|-------------|------|----------|
| **Academic** | Formal, tight spacing | Times New Roman | Research papers, academic texts |
| **Modern** | Clean, generous spacing | System fonts | General books, blogs |  
| **Compact** | Space-efficient | Helvetica | Technical manuals, references |
| **E-book** | Mobile-optimized | Georgia | E-readers, mobile devices |
| **Minimal** | Clean, content-focused | Arial | Presentations, clean design |

## 🔧 Detailed Command Reference

### Basic Generation Commands

```bash
# Simple workflow (recommended for beginners)
python scripts/cli.py simple "Your Topic" --chapters 3 --words-per-chapter 500

# Simple workflow with source content from uploads folder
python scripts/cli.py simple "AI Foundations" --chapters 7 --words-per-chapter 800 --source-file ai_foundations.md

# Advanced generation with custom options
python scripts/cli.py generate-book "Your Book Title" \
  --chapters 5 \
  --target-pages 20 \
  --book-style modern \
  --font-family "Georgia" \
  --line-height "1.6" \
  --color-scheme "blue"
```

### System Management Commands

```bash
# Check system health and configuration
python scripts/cli.py health
python scripts/cli.py config

# View available styles
python scripts/cli.py styles

# Generate outline only
python scripts/cli.py outline "Your Topic" --target-pages 10
```

### Using Source Content

```bash
# Step 1: Place your source content in uploads folder
echo "Your research material here..." > uploads/my_content.md

# Step 2: Generate book using that content as context
python scripts/cli.py simple "Book Topic" --chapters 5 --source-file my_content.md

# The AI will use your source content to inform the chapter generation
# Works with any text file: .md, .txt, or any readable format
```

### Advanced Options

```bash
# Custom styling options
--book-style [academic|modern|compact|ebook|minimal]
--font-family ["Times New Roman"|"Arial"|"Georgia"|"Monaco"|"Helvetica"]
--line-height ["1.2"|"1.3"|"1.4"|"1.5"|"1.6"|"1.7"]
--color-scheme [default|dark|sepia|blue]
--max-width ["600px"|"700px"|"800px"|"900px"|"100%"]

# Source content option (for simple workflow)
--source-file [filename.md|filename.txt] # File from uploads/ folder
```

## 💡 Mathematical Equations Support

The system supports mathematical equations using MathJax:

### Inline Math
```markdown
The equation $E = mc^2$ is Einstein's famous formula.
```

### Display Math
```markdown
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

### LaTeX Support
```markdown
The derivative of $f(x) = x^2$ is $f'(x) = 2x$.

$$
\frac{d}{dx}\left(\int_a^x f(t)dt\right) = f(x)
$$
```

## 🔧 Working with Source Content (Optional)

If you have source material, place it in the `uploads/` directory:

```bash
# Create or edit source content
echo "Your research content here..." > uploads/my_research.md

# The AI will use this for context (if RAG is enabled)
python scripts/cli.py upload uploads/my_research.md
python scripts/cli.py generate-book "Research Summary" --rag
```

## 📊 Cost Tracking and Performance

The system provides real-time cost tracking:

- **Token usage**: Input/output tokens for each chapter
- **Cost estimation**: Real-time cost calculation
- **Performance metrics**: Generation time and success rates

Example output:
```
✅ Chapter 2 completed - Cost: $0.0156
💰 Total cost: $0.0623
🔤 Tokens: 1,234 input, 2,456 output
⏱️  Generation time: 45.3 seconds
```

## 🛠️ Project Structure

```bash
book_creator/
├── .env                    # Your API key configuration
├── start_server.py         # Server launcher script
├── backend/                # Core AI system
│   ├── main.py            # Unified server
│   ├── llm.py             # Claude integration
│   ├── writer.py          # Content generation
│   ├── book_styles.py     # Styling system
│   └── config.py          # Configuration management
├── scripts/
│   └── cli.py             # Command-line interface
├── exports/               # Generated books (timestamped folders)
├── uploads/               # Source content (optional)
└── requirements.txt       # Python dependencies
```

## 🎛️ Configuration Options

The system uses environment variables and feature flags for configuration:

### Core Features
- `RAG_ENABLED` - Enable/disable RAG functionality (default: true)
- `ENHANCED_LOGGING` - Detailed logging (default: true)  
- `PDF_GENERATION` - PDF export capability (default: true)

### Generation Settings
- `DEFAULT_TARGET_PAGES` - Default page count (default: 10)
- `DEFAULT_WORDS_PER_CHAPTER` - Words per chapter (default: 2000)
- `MAX_CHAPTERS` - Maximum chapters allowed (default: 50)

### RAG Settings
- `RAG_CHUNK_SIZE` - Document chunk size (default: 1000)
- `RAG_TOP_K` - Number of relevant docs to retrieve (default: 6)

## 🔧 Usage Examples

### Command Line Interface

```bash
# Check system status and features
python scripts/cli.py health

# Generate with different styles
python scripts/cli.py generate-book "Python Guide" --book-style academic
python scripts/cli.py generate-book "Web Development" --book-style modern

# Custom styling
python scripts/cli.py generate-book "Technical Manual" \
  --font-family "Monaco" --line-height "1.3" --color-scheme "blue"

# RAG-enhanced generation (if RAG enabled)
python scripts/cli.py upload source_document.pdf
python scripts/cli.py rag-stats
python scripts/cli.py generate-book "Research Summary" \
  --rag --rag-query "specific topic keywords"

# Agent-based generation
python scripts/cli.py agent "Create a 5-chapter book about quantum computing"
```

### Python Generator Script

```bash
# Different generation modes
python generators/book_generator.py --mode simple --topic "AI Basics"
python generators/book_generator.py --mode complete --topic "Data Science" --chapters 10
python generators/book_generator.py --mode demo  # Demo all styles
python generators/book_generator.py --mode rag --upload research.pdf
```

### API Usage

```python
import requests

# Generate book via API
response = requests.post("http://localhost:8000/generate-book", json={
    "title": "My Book",
    "chapters": 8,
    "target_pages": 20,
    "book_style": "modern",
    "use_rag": True  # If RAG is enabled
})

book_data = response.json()
```

## 🎨 Available Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **Academic** | Formal, tight spacing, Times New Roman | Research papers, academic texts |
| **Modern** | Clean, generous spacing, system fonts | General books, blogs |  
| **Compact** | Space-efficient, Helvetica | Technical manuals, references |
| **E-book** | Mobile-optimized, responsive | E-readers, mobile devices |
| **Minimal** | Clean, content-focused | Presentations, clean design |

Plus full custom styling with fonts, spacing, colors, and layout options.

## 🧪 Testing

```bash
# Run comprehensive test suite
python tests/test_unified.py

# Specific test types
python tests/test_unified.py --type api
python tests/test_unified.py --type imports  
python tests/test_unified.py --type filesystem

# Include RAG tests
python tests/test_unified.py --rag --verbose
```

## 🔍 RAG Enhancement (Optional)

When enabled, RAG provides:

- **Document Upload** - PDF, DOCX, TXT, MD support
- **Smart Chunking** - Optimal text segmentation with overlap
- **Context-Aware Generation** - Books informed by your sources
- **Source Tracking** - Citations and attribution
- **Flexible Queries** - Custom search terms for relevance

```bash
# RAG workflow
python scripts/cli.py upload research_paper.pdf
python scripts/cli.py rag-stats
python scripts/cli.py rag-query "machine learning algorithms" 
python scripts/cli.py generate-book "ML Guide" --rag
```

## 💰 Cost Estimation

The system provides detailed cost tracking:

- **Outline Generation**: ~$0.01
- **Chapter Writing**: ~$0.01-0.02 per chapter  
- **10-chapter book**: ~$0.10-0.20 total
- **RAG queries**: Minimal additional cost

## 📊 What's New in v4.0

### ✨ Major Improvements
- **Unified Architecture** - Single server handles all features
- **Configuration System** - Environment-based feature control
- **Enhanced Logging** - Comprehensive request/response tracking
- **Consolidated CLI** - One interface for all functionality
- **Unified Generator** - Single script replaces multiple demos
- **Comprehensive Testing** - Complete test coverage

### 🗑️ Removed Redundancy
- **25+ duplicate files removed** - Cleaner codebase
- **Backup files eliminated** - Single source of truth
- **Demo scripts consolidated** - One unified generator
- **Test files merged** - Comprehensive test suite
- **40% code reduction** - Easier maintenance

### 🔧 Technical Improvements
- **Feature detection** - CLI adapts to server capabilities
- **Graceful degradation** - Works with or without RAG
- **Error handling** - Better error messages and recovery
- **Performance** - Optimized request handling

## 🛠️ Development

### Running the Server
```bash
# Standard mode
python -m backend.main

# With specific features
RAG_ENABLED=false python -m backend.main
ENHANCED_LOGGING=false python -m backend.main
```

### Adding New Features
1. Add feature flag to `backend/config.py`
2. Implement feature with configuration checks
3. Update CLI to detect feature availability
4. Add tests to `tests/test_unified.py`

## 🆘 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Server Won't Start
```bash
# Check for processes using port 8000
pkill -f "python start_server.py"
pkill -f "backend.main"

# Restart server
python start_server.py
```

#### 2. API Key Issues
```bash
# Check if API key is loaded
echo $ANTHROPIC_API_KEY

# If empty, reload environment
source .env
echo $ANTHROPIC_API_KEY
```

#### 3. Missing Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install specific missing packages
pip install anthropic python-dotenv
```

#### 4. Generation Fails
```bash
# Test system health first
python scripts/cli.py health

# Try simple generation
python scripts/cli.py simple "Test" --chapters 2 --words-per-chapter 200

# Check server logs in the server terminal
```

#### 5. Empty Content Generated
- ✅ **Check API key is valid**
- ✅ **Verify server logs show token usage**
- ✅ **Ensure server and CLI are using same environment**

#### 6. Style Issues
```bash
# List available styles
python scripts/cli.py styles

# Test with default style
python scripts/cli.py simple "Test" --chapters 1
```

### Quick Diagnostic Commands

```bash
# Full system check
python scripts/cli.py health
python scripts/cli.py config
python scripts/cli.py styles

# Test minimal generation
python scripts/cli.py simple "Diagnostic Test" --chapters 1 --words-per-chapter 100
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass: `python tests/test_unified.py`
5. Submit a pull request

---

## 🚀 Quick Start Example

**Ready to create your first book?** Follow this 30-second guide:

```bash
# 1. Ensure you're in the right environment
cd book_creator
source .venv/bin/activate
source .env

# 2. Kill any existing server and start fresh
pkill -f "python start_server.py"
python start_server.py

# 3. In a new terminal, test the system
cd book_creator
source .venv/bin/activate
python scripts/cli.py health

# 4. Generate your first book!
python scripts/cli.py simple "Introduction to AI" --chapters 3 --words-per-chapter 600

# Optional: Use source content for more focused generation
echo "Your AI research notes..." > uploads/ai_notes.md
python scripts/cli.py simple "AI Foundations" --chapters 7 --words-per-chapter 800 --source-file ai_notes.md
```

**That's it!** Check the `exports/` folder for your timestamped book with multiple style variations.

## 📱 Next Steps

- 📖 **View your book**: Open the HTML files in your browser
- 🎨 **Try different styles**: Use `--book-style academic` or `--book-style compact`
- 📊 **Monitor costs**: Check the server logs for token usage
- 🔧 **Customize**: Add `--font-family "Times New Roman"` and other options

**Happy book creation!** ✨ 