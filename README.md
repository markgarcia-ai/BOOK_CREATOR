# 📚 Book Creator - Unified AI Book Generation System

A comprehensive, AI-powered book creation system that generates complete books using Claude (Anthropic API) with optional RAG (Retrieval-Augmented Generation) enhancement.

## 🌟 Features

✅ **Unified Architecture** - Single codebase with feature flags  
✅ **AI-Powered Writing** - Intelligent planning, writing, and quality control  
✅ **RAG Enhancement** - Fact-checked content using your sources (optional)  
✅ **Multiple Formats** - PDF, HTML, EPUB, DOCX export  
✅ **Custom Styling** - 5 built-in styles + full customization  
✅ **Cost Tracking** - Monitor API usage and costs  
✅ **Configuration-Driven** - Feature flags and environment-based settings  

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and setup
git clone <repository>
cd book_creator
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Set your API key
echo "ANTHROPIC_API_KEY=your_actual_api_key_here" > .env

# Optional: Configure features
export RAG_ENABLED=true        # Enable RAG functionality
export ENHANCED_LOGGING=true   # Enable detailed logging
export PDF_GENERATION=true     # Enable PDF export
```

### 3. Start the Server
```bash
# Start unified server
python -m backend.main

# The server automatically detects available features
```

### 4. Generate Your First Book
```bash
# Simple generation
python scripts/cli.py generate-book "Machine Learning Fundamentals" \
  --chapters 8 --target-pages 20 --book-style modern

# With RAG enhancement (if enabled)
python scripts/cli.py upload research_paper.pdf
python scripts/cli.py generate-book "ML Research Summary" \
  --rag --rag-query "machine learning algorithms"

# Using the unified generator
python generators/book_generator.py --topic "AI Ethics" --mode complete
```

## 📁 Project Structure

```
book_creator/
├── backend/                 # Core AI system
│   ├── main.py             # 🔄 Unified server (standard + RAG)
│   ├── llm.py              # 🔄 Enhanced LLM with logging
│   ├── config.py           # ✨ New: Configuration management
│   ├── reasonning_agent.py # AI orchestration
│   ├── planner.py          # Outline generation  
│   ├── writer.py           # Content generation
│   ├── tools.py            # File operations
│   └── book_styles.py      # Styling system
├── scripts/
│   └── cli.py              # 🔄 Unified CLI (standard + RAG)
├── generators/
│   └── book_generator.py   # ✨ New: Unified generator script
├── tests/
│   └── test_unified.py     # ✨ New: Comprehensive test suite
├── rag/                    # RAG system (optional)
│   ├── retrieve.py         # Search and retrieval
│   ├── ingest.py           # Document processing
│   └── pdf_processor.py    # PDF handling
├── book/                   # Generated content
├── exports/                # Final books
└── prompts/                # AI prompts
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

## 🆘 Troubleshooting

### Server Issues
```bash
# Check server status
python scripts/cli.py health

# Verify configuration
python scripts/cli.py config

# Test with simple generation
python scripts/cli.py simple "Test Topic" --chapters 3
```

### RAG Issues
```bash
# Check RAG status
python scripts/cli.py rag-stats

# Test RAG query
python scripts/cli.py rag-query "test"

# Upload test document
python scripts/cli.py upload sample.pdf
```

### Common Solutions
- **Port conflicts**: Server tries ports 8000-8010 automatically
- **Missing dependencies**: `pip install -r requirements.txt`
- **API key issues**: Check `.env` file and `ANTHROPIC_API_KEY`
- **RAG not working**: Ensure `RAG_ENABLED=true` and dependencies installed

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass: `python tests/test_unified.py`
5. Submit a pull request

---

**Ready to create your first AI-generated book?** 🚀

```bash
python scripts/cli.py generate-book "Your Amazing Book Topic"
``` 