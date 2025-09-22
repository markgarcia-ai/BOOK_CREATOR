# 📚 Book Creator - Complete User Guide

## 🎯 Overview

The Book Creator is an AI-powered system that generates complete books using Claude (Anthropic API). You can create books from scratch, update existing books with different styles, and customize formatting to your exact preferences.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Activate virtual environment
source .venv/bin/activate

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Start the API server
python -m backend.main &
```

### 2. Check System Status
```bash
# Verify API is running
python scripts/cli.py health

# List available book styles
python scripts/cli.py styles
```

## 📖 Creating Books from Scratch

### Method 1: Using the CLI (Recommended)

#### Basic Book Generation
```bash
# Generate a simple book
python scripts/cli.py generate-book "Your Topic" \
  --target-audience "your audience" \
  --style "your style" \
  --target-pages 10
```

#### Technical Book with Custom Styling
```bash
# Generate a technical book with custom formatting
python scripts/cli.py generate-book "Advanced Python Programming" \
  --target-audience "senior developers" \
  --style "technical" \
  --target-pages 15 \
  --book-style modern \
  --font-family "Monaco" \
  --line-height "1.3" \
  --paragraph-spacing "0.8em" \
  --header-spacing "1.5em" \
  --max-width "900px" \
  --color-scheme "blue"
```

#### Academic Book with Tight Spacing
```bash
# Generate an academic book
python scripts/cli.py generate-book "Machine Learning Fundamentals" \
  --target-audience "graduate students" \
  --style "academic" \
  --target-pages 20 \
  --book-style academic
```

### Method 2: Using the Simple Generator (When Server Has Issues)

```bash
# Generate example books with all styles
python simple_book_generator.py
```

## 🎨 Book Styles Available

### Predefined Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **Academic** | Formal style with tight spacing (Times New Roman, 1.4 line height) | Research papers, academic texts |
| **Modern** | Clean style with generous spacing (System fonts, 1.6 line height) | General books, blogs |
| **Compact** | Space-efficient for maximum content (Helvetica, 1.3 line height) | Technical manuals, reference guides |
| **E-book** | Optimized for e-readers and mobile (Georgia, responsive) | E-books, mobile reading |
| **Minimal** | Clean minimal style with focus on content (Arial, 1.4 line height) | Clean presentations, minimal design |

### Custom Style Options

- **Font Families**: Arial, Times New Roman, Georgia, Helvetica, Verdana, Monaco
- **Line Heights**: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
- **Paragraph Spacing**: 0.5em, 0.8em, 1em, 1.2em, 1.5em, 2em
- **Header Spacing**: 1em, 1.5em, 2em, 2.5em, 3em
- **Max Widths**: 600px, 700px, 800px, 900px, 100%
- **Color Schemes**: default, dark, sepia, blue

## 🔄 Updating Existing Books

### Update with Predefined Styles
```bash
# Update existing book with different styles
python update_book_style.py exports/your_book.md -s academic
python update_book_style.py exports/your_book.md -s modern
python update_book_style.py exports/your_book.md -s compact
python update_book_style.py exports/your_book.md -s ebook
python update_book_style.py exports/your_book.md -s minimal
```

### Update with Custom Technical Style
```bash
# Update with custom technical formatting
python update_book_style.py exports/your_book.md \
  --font-family "Monaco" \
  --line-height "1.3" \
  --paragraph-spacing "0.8em" \
  --header-spacing "1.5em" \
  --max-width "900px" \
  --color-scheme "blue" \
  -o exports/your_book_technical.html
```

## 📋 Step-by-Step Examples

### Example 1: Create a Data Science Book

```bash
# Step 1: Generate the book
python scripts/cli.py generate-book "Data Science with Python" \
  --target-audience "data scientists" \
  --style "technical" \
  --target-pages 12 \
  --book-style modern

# Step 2: Update with different styles
python update_book_style.py exports/data_science_with_python.md -s academic
python update_book_style.py exports/data_science_with_python.md -s compact

# Step 3: View your books
open exports/data_science_with_python.html
open exports/data_science_with_python_academic.html
open exports/data_science_with_python_compact.html
```

### Example 2: Create a Programming Tutorial

```bash
# Step 1: Generate with custom technical style
python scripts/cli.py generate-book "Python Programming Tutorial" \
  --target-audience "beginners" \
  --style "educational" \
  --target-pages 8 \
  --book-style modern \
  --font-family "Monaco" \
  --line-height "1.4" \
  --paragraph-spacing "1em" \
  --color-scheme "blue"

# Step 2: Create e-book version
python update_book_style.py exports/python_programming_tutorial.md -s ebook

# Step 3: Create compact version for reference
python update_book_style.py exports/python_programming_tutorial.md -s compact
```

### Example 3: Create an Academic Paper

```bash
# Step 1: Generate academic content
python scripts/cli.py generate-book "Machine Learning Research" \
  --target-audience "researchers" \
  --style "academic" \
  --target-pages 25 \
  --book-style academic

# Step 2: Create different formats
python update_book_style.py exports/machine_learning_research.md -s academic
python update_book_style.py exports/machine_learning_research.md -s modern
```

## 🛠️ Advanced Usage

### Using the Agent System
```bash
# Run the reasoning agent for complex tasks
python scripts/cli.py agent "Create a complete book about quantum computing with 10 chapters"

# Generate outline first
python scripts/cli.py outline "Quantum Computing" --chapters 10 --audience "physicists"

# Build the book
python scripts/cli.py build html
```

### File Upload and RAG
```bash
# Upload source material
python scripts/cli.py upload path/to/your/source.md

# Ingest into RAG system
python scripts/cli.py ingest path/to/source/files/

# Retrieve relevant facts
python scripts/cli.py retrieve "machine learning algorithms" --k 5
```

## 📁 File Structure

After generating books, you'll find:

```
exports/
├── your_book.md                    # Markdown version
├── your_book.html                  # HTML version (default style)
├── your_book_academic.html         # Academic style version
├── your_book_modern.html           # Modern style version
├── your_book_compact.html          # Compact style version
├── your_book_ebook.html            # E-book style version
└── your_book_custom_technical.html # Custom technical style
```

## 🎯 Best Practices

### 1. Choose the Right Style
- **Academic**: For research papers, formal documents
- **Modern**: For general books, blogs, presentations
- **Compact**: For technical manuals, reference guides
- **E-book**: For mobile reading, e-readers
- **Minimal**: For clean, focused content

### 2. Optimize for Your Audience
- **Beginners**: Use educational style, generous spacing
- **Experts**: Use technical style, compact formatting
- **General**: Use modern style, balanced spacing

### 3. Custom Styling Tips
- **Monaco font**: Great for code-heavy technical books
- **Tight spacing**: Use for academic or reference materials
- **Generous spacing**: Use for educational or general audience books
- **Blue color scheme**: Professional, technical appearance

## 🔧 Troubleshooting

### Common Issues

#### 1. Server Not Starting
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing processes
pkill -f "python -m backend.main"

# Restart server
python -m backend.main &
```

#### 2. JSON Parsing Errors
- The server may have issues with LaTeX math in JSON
- Use the `simple_book_generator.py` as a workaround
- Or use the `update_book_style.py` utility for existing books

#### 3. Missing Dependencies
```bash
# Install missing packages
pip install python-multipart
pip install anthropic
pip install fastapi
pip install uvicorn
```

#### 4. API Key Issues
```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## 📊 Cost Estimation

The system tracks costs for each generation:

- **Outline Generation**: ~$0.01
- **Chapter Writing**: ~$0.01-0.02 per chapter
- **Total for 10-page book**: ~$0.10-0.20

## 🎉 Next Steps

### After Generating Your Book

1. **View Your Book**:
   ```bash
   open exports/your_book.html
   ```

2. **Create Additional Formats**:
   ```bash
   # PDF (requires pandoc + pdflatex)
   pandoc exports/your_book.md -o exports/your_book.pdf
   
   # EPUB
   pandoc exports/your_book.md -o exports/your_book.epub
   
   # DOCX
   pandoc exports/your_book.md -o exports/your_book.docx
   ```

3. **Customize Further**:
   - Edit the markdown file directly
   - Add images to `book/assets/img/`
   - Regenerate with different styles

4. **Share Your Book**:
   - Upload to GitHub
   - Convert to slides: `pandoc exports/your_book.md -t revealjs -s -o exports/your_book_slides.html`
   - Print or distribute as needed

## 🆘 Getting Help

### Available Commands
```bash
# List all available commands
python scripts/cli.py --help

# Get help for specific command
python scripts/cli.py generate-book --help
python update_book_style.py --help
```

### Check System Status
```bash
# Health check
python scripts/cli.py health

# Project status
python scripts/cli.py status

# Available styles
python scripts/cli.py styles
```

---

## 🎯 Summary

You now have a complete book creation system that can:

✅ Generate books from scratch using AI  
✅ Apply 5 different predefined styles  
✅ Create custom styles with full control  
✅ Update existing books with new styles  
✅ Handle mathematical equations with MathJax  
✅ Export to multiple formats  
✅ Track costs and usage  

**Start creating your first book now!** 🚀

## 🔍 RAG-Enhanced Book Generation

The system now supports **Retrieval-Augmented Generation (RAG)** to create books based on your specific source material (PDFs, DOCX, TXT, MD files).

### RAG Workflow

1. **Upload Source Material** → 2. **RAG Ingestion** → 3. **Generate Book with Context**

### Step-by-Step RAG Process

#### Step 1: Upload Your Source Material

```bash
# Upload a PDF file
python scripts/cli_with_rag.py upload path/to/your/document.pdf

# Upload a DOCX file
python scripts/cli_with_rag.py upload path/to/your/document.docx

# Upload a markdown file
python scripts/cli_with_rag.py upload path/to/your/notes.md
```

#### Step 2: Check RAG Status

```bash
# Check what's in your RAG system
python scripts/cli_with_rag.py rag-stats

# Query your RAG system
python scripts/cli_with_rag.py rag-query "machine learning algorithms"
```

#### Step 3: Generate RAG-Enhanced Book

```bash
# Generate book using your uploaded content
python scripts/cli_with_rag.py generate-book "Advanced Machine Learning" \
  --target-audience "data scientists" \
  --style "technical" \
  --target-pages 20 \
  --use-rag \
  --rag-query "machine learning deep learning neural networks"
```

### RAG Commands Reference

#### Upload and Ingest
```bash
# Upload single file (auto-ingests if supported format)
python scripts/cli_with_rag.py upload document.pdf

# Ingest entire directory
python scripts/cli_with_rag.py ingest path/to/source/documents/

# Ingest with custom chunking
python scripts/cli_with_rag.py ingest documents/ --chunk-size 1500 --overlap 300
```

#### RAG Management
```bash
# Check RAG collection status
python scripts/cli_with_rag.py rag-stats

# Search your RAG system
python scripts/cli_with_rag.py rag-query "your search terms"

# Clear all RAG data
python scripts/cli_with_rag.py rag-clear
```

#### RAG-Enhanced Book Generation
```bash
# Basic RAG generation
python scripts/cli_with_rag.py generate-book "Your Topic" --use-rag

# Advanced RAG generation with custom query
python scripts/cli_with_rag.py generate-book "Machine Learning" \
  --use-rag \
  --rag-query "supervised learning algorithms" \
  --book-style academic \
  --target-pages 25

# Disable RAG (standard generation)
python scripts/cli_with_rag.py generate-book "Your Topic" --no-rag
```

### Supported File Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| **PDF** | `.pdf` | Research papers, books, documents |
| **DOCX** | `.docx` | Microsoft Word documents |
| **Text** | `.txt` | Plain text files |
| **Markdown** | `.md` | Markdown documents |

### RAG Features

✅ **Automatic PDF Processing**: Extracts text from PDFs with page information  
✅ **Smart Chunking**: Breaks documents into optimal chunks with overlap  
✅ **Context-Aware Generation**: Uses your source material to inform book content  
✅ **Source Citations**: Tracks which sources were used for each chapter  
✅ **Flexible Queries**: Search your RAG system with custom queries  
✅ **Batch Processing**: Ingest entire directories of documents  

### Example RAG Workflow

```bash
# 1. Start the RAG-enhanced server
python -m backend.main_with_rag &

# 2. Upload your research papers
python scripts/cli_with_rag.py upload research_paper_1.pdf
python scripts/cli_with_rag.py upload research_paper_2.pdf
python scripts/cli_with_rag.py upload my_notes.md

# 3. Check what's been ingested
python scripts/cli_with_rag.py rag-stats

# 4. Search your knowledge base
python scripts/cli_with_rag.py rag-query "neural network architectures"

# 5. Generate a book using your sources
python scripts/cli_with_rag.py generate-book "Deep Learning Fundamentals" \
  --target-audience "graduate students" \
  --style "academic" \
  --target-pages 30 \
  --use-rag \
  --rag-query "deep learning neural networks" \
  --book-style academic

# 6. View your RAG-enhanced book
open exports/deep_learning_fundamentals.html
```

### RAG vs Standard Generation

| Feature | Standard Generation | RAG-Enhanced |
|---------|-------------------|--------------|
| **Source Material** | General knowledge | Your specific documents |
| **Accuracy** | General | Based on your sources |
| **Citations** | None | Source tracking |
| **Customization** | Limited | High (your content) |
| **Use Case** | General topics | Research, technical docs |

### Best Practices for RAG

1. **Upload High-Quality Sources**: Use well-written, relevant documents
2. **Organize Your Content**: Group related documents in directories
3. **Use Specific Queries**: Be specific in your RAG queries for better results
4. **Check RAG Stats**: Monitor what's been ingested successfully
5. **Test Queries**: Search your RAG system before generating books

### Troubleshooting RAG

#### Common Issues

**PDF Not Processing**:
```bash
# Check if PDF is text-based (not scanned image)
python scripts/cli_with_rag.py upload your_document.pdf
# If it fails, try converting to text first
```

**No RAG Results**:
```bash
# Check RAG stats
python scripts/cli_with_rag.py rag-stats

# Try broader queries
python scripts/cli_with_rag.py rag-query "your topic"
```

**Server Issues**:
```bash
# Use the RAG-enhanced server
python -m backend.main_with_rag &

# Check health
python scripts/cli_with_rag.py health
```

---

## 🎯 Complete RAG Workflow Example

Here's a complete example of creating a technical book using RAG:

```bash
# 1. Setup
source .venv/bin/activate
export ANTHROPIC_API_KEY="your-api-key"
python -m backend.main_with_rag &

# 2. Upload source material
python scripts/cli_with_rag.py upload machine_learning_paper.pdf
python scripts/cli_with_rag.py upload deep_learning_notes.md
python scripts/cli_with_rag.py upload statistics_handbook.pdf

# 3. Verify ingestion
python scripts/cli_with_rag.py rag-stats

# 4. Test queries
python scripts/cli_with_rag.py rag-query "gradient descent"
python scripts/cli_with_rag.py rag-query "neural network training"

# 5. Generate RAG-enhanced book
python scripts/cli_with_rag.py generate-book "Machine Learning: From Theory to Practice" \
  --target-audience "graduate students" \
  --style "academic" \
  --target-pages 40 \
  --use-rag \
  --rag-query "machine learning algorithms neural networks" \
  --book-style academic \
  --font-family "Times New Roman" \
  --line-height "1.4"

# 6. View results
open exports/machine_learning_from_theory_to_practice.html
```

**Result**: A comprehensive, academically-styled book based on your specific source material, with proper citations and context-aware content generation.

---

## 🚀 Quick Start with RAG

**For immediate RAG-enhanced book generation:**

1. **Upload a PDF**: `python scripts/cli_with_rag.py upload your_document.pdf`
2. **Generate Book**: `python scripts/cli_with_rag.py generate-book "Your Topic" --use-rag`
3. **View Result**: `open exports/your_topic.html`

**That's it!** Your book will be generated using the content from your uploaded document.

