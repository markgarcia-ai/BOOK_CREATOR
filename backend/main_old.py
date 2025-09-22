import os, json, subprocess, shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .reasonning_agent import run_agent, run_simple_workflow
from .planner import generate_outline
from .writer import write_chapter
from .llm import complete_json
from . import tools as T
from .settings import WRITER_MODEL, PLANNER_MODEL
from .book_styles import get_style, list_styles, create_custom_style

app = FastAPI(title="Book Creator API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)

class GenerateReq(BaseModel):
    title: str
    chapters: List[str]
    words_per_chapter: int = 3500

class AgentReq(BaseModel):
    goal: str
    max_steps: int = 8
    model: str = WRITER_MODEL

class OutlineReq(BaseModel):
    topic: str
    chapters: int = 10
    words_per_chapter: int = 3500
    audience: str = "General audience"
    tone: str = "Professional"

class BookGenerationReq(BaseModel):
    topic: str
    target_audience: str = "general"
    style: str = "informative"
    target_pages: int = 50
    source_file_path: Optional[str] = None
    book_style: str = "modern"  # New field for book styling
    custom_style: Optional[Dict[str, Any]] = None  # For custom styling

@app.get("/health")
def health(): 
    return {"ok": True, "status": "Book Creator API is running"}

@app.get("/status")
def get_status():
    """Get project status"""
    return T.get_project_status()

@app.get("/styles")
def get_available_styles():
    """Get all available book styles"""
    return {
        "available_styles": list_styles(),
        "default_style": "modern",
        "custom_style_options": {
            "font_families": ["Arial", "Times New Roman", "Georgia", "Helvetica", "Verdana"],
            "line_heights": ["1.2", "1.3", "1.4", "1.5", "1.6", "1.7"],
            "paragraph_spacings": ["0.5em", "0.8em", "1em", "1.2em", "1.5em", "2em"],
            "header_spacings": ["1em", "1.5em", "2em", "2.5em", "3em"],
            "max_widths": ["600px", "700px", "800px", "900px", "100%"],
            "color_schemes": ["default", "dark", "sepia", "blue"]
        }
    }

@app.post("/upload-source")
async def upload_source_file(file: UploadFile = File(...)):
    """Upload a markdown source file for book generation"""
    try:
        # Save the uploaded file
        file_path = UPLOADS / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

def create_mathjax_html_template(title: str, content: str, book_style: str = "modern", custom_style: Optional[Dict] = None) -> str:
    """Create HTML with MathJax support and customizable styling"""
    
    # Get the book style
    if custom_style:
        style_obj = create_custom_style(
            name="Custom",
            font_family=custom_style.get("font_family", "Arial"),
            line_height=custom_style.get("line_height", "1.5"),
            paragraph_spacing=custom_style.get("paragraph_spacing", "1em"),
            header_spacing=custom_style.get("header_spacing", "2em"),
            max_width=custom_style.get("max_width", "800px"),
            color_scheme=custom_style.get("color_scheme", "default")
        )
    else:
        style_obj = get_style(book_style)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Book Style: {style_obj.name} */
        {style_obj.css_styles}
        
        /* Additional styling for code and math */
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
            margin: 1em 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 1em 0;
            padding-left: 20px;
            color: #666;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .math {{
            margin: 1em 0;
            text-align: center;
        }}
        .metadata {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 2em;
            border-left: 4px solid #27ae60;
            font-size: 0.9em;
        }}
        .style-info {{
            background-color: #e8f4fd;
            padding: 10px;
            border-radius: 3px;
            margin-bottom: 1em;
            font-size: 0.8em;
            color: #2c3e50;
        }}
    </style>
    <!-- MathJax Configuration -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <div class="metadata">
        <strong>Generated Book</strong><br>
        <em>This book was automatically generated using AI</em>
    </div>
    <div class="style-info">
        <strong>Style:</strong> {style_obj.name} | 
        <strong>Font:</strong> {style_obj.font_family} | 
        <strong>Line Height:</strong> {style_obj.line_height} | 
        <strong>Max Width:</strong> {style_obj.max_width}
    </div>
    {content}
</body>
</html>"""

def convert_markdown_to_html_with_math(markdown_content: str, title: str, book_style: str = "modern", custom_style: Optional[Dict] = None) -> str:
    """Convert markdown to HTML with proper math rendering and custom styling"""
    try:
        # Use pandoc to convert markdown to HTML
        cmd = ["pandoc", "-f", "markdown", "-t", "html", "--mathjax"]
        result = subprocess.run(cmd, input=markdown_content, text=True, capture_output=True, check=True)
        html_content = result.stdout
        
        # Create full HTML document with MathJax and custom styling
        full_html = create_mathjax_html_template(title, html_content, book_style, custom_style)
        return full_html
        
    except subprocess.CalledProcessError as e:
        print(f"Pandoc conversion failed: {e}")
        # Fallback: simple HTML conversion
        html_content = markdown_content.replace('\n', '<br>\n')
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n')
        return create_mathjax_html_template(title, html_content, book_style, custom_style)

@app.post("/generate-book")
async def generate_full_book(request: BookGenerationReq):
    """Generate a complete book (up to 50 pages) from source material"""
    try:
        print(f"\n🚀 Starting book generation process...")
        print(f"📖 Topic: {request.topic}")
        print(f"👥 Audience: {request.target_audience}")
        print(f"📝 Style: {request.style}")
        print(f"📄 Target pages: {request.target_pages}")
        print(f"🎨 Book style: {request.book_style}")
        if request.custom_style:
            print(f"🎨 Custom style: {request.custom_style}")
        
        # Step 1: Generate comprehensive outline for target pages
        print(f"\n🧠 STEP 1: Generating comprehensive outline...")
        print(f"🤖 Using model: {PLANNER_MODEL}")
        
        system_prompt = "You are an expert book planner. Create comprehensive book outlines with detailed chapter structures."
        user_prompt = f"""
        Create a comprehensive book outline for a {request.target_pages}-page book on "{request.topic}".
        
        Target audience: {request.target_audience}
        Style: {request.style}
        
        The book should have:
        - 8-12 main chapters
        - Each chapter should be 4-6 pages long
        - Include detailed subtopics for each chapter
        - Ensure comprehensive coverage of the topic
        """
        
        print(f"📋 Planning prompt: {user_prompt[:200]}...")
        
        schema_hint = """
        {
            "title": "Book Title",
            "chapters": [
                {
                    "number": 1,
                    "title": "Chapter Title",
                    "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
                    "estimated_pages": 5
                }
            ],
            "total_estimated_pages": 50
        }
        """
        
        print(f"�� Calling Claude API for outline generation...")
        outline_result = complete_json(PLANNER_MODEL, system_prompt, user_prompt, schema_hint)
        outline = outline_result[0] if isinstance(outline_result, tuple) else outline_result
        outline_metadata = outline_result[1] if isinstance(outline_result, tuple) else {}
        
        print(f"✅ Outline generated successfully!")
        print(f"📊 Cost: ${outline_metadata.get('cost', 0):.4f}")
        print(f"🔤 Tokens: {outline_metadata.get('input_tokens', 0)} input, {outline_metadata.get('output_tokens', 0)} output")
        print(f"📚 Book title: {outline.get('title', 'Generated Book')}")
        print(f"📑 Chapters planned: {len(outline.get('chapters', []))}")
        
        # Step 2: Generate all chapters
        print(f"\n✍️  STEP 2: Writing chapters...")
        print(f"🤖 Using model: {WRITER_MODEL}")
        
        chapters = []
        total_chapter_cost = 0
        
        for i, chapter_info in enumerate(outline.get("chapters", []), 1):
            print(f"\n📝 Writing Chapter {i}/{len(outline.get('chapters', []))}: {chapter_info.get('title', '')}")
            
            chapter_system = """You are an expert technical writer. Write comprehensive, well-structured chapters with detailed explanations and examples. 

IMPORTANT FORMATTING RULES:
- Use proper markdown formatting with headers, lists, and emphasis
- For mathematical equations, use LaTeX format: $equation$ for inline math and $$equation$$ for display math
- Use **bold** for emphasis and *italic* for technical terms
- Use code blocks with ```language for code examples
- Use numbered lists (1., 2., 3.) and bullet points (-) appropriately
- Ensure proper spacing between sections
- IMPORTANT: When writing mathematical expressions, use simple LaTeX without complex backslashes that break JSON parsing"""
            
            chapter_user = f"""
            Write a comprehensive chapter for the book "{outline.get('title', '')}".
            
            Chapter {chapter_info['number']}: {chapter_info['title']}
            Subtopics to cover: {', '.join(chapter_info.get('subtopics', []))}
            Target length: {chapter_info.get('estimated_pages', 5)} pages
            
            Write in {request.style} style for {request.target_audience} audience.
            Include detailed explanations, examples, and practical insights.
            
            FORMATTING REQUIREMENTS:
            - Use proper markdown headers (##, ###, ####)
            - Use LaTeX math notation: $P(y=1) = frac{{1}}{{1 + e^{{-z}}}}$ for equations (use frac instead of \\frac)
            - Use **bold** for key terms and *italic* for emphasis
            - Include code examples in ```python blocks when relevant
            - Use numbered lists for step-by-step processes
            - Use bullet points for feature lists
            - For fractions, use: frac{{numerator}}{{denominator}} instead of \\frac
            - For subscripts, use: x_i instead of x_{{i}}
            - For superscripts, use: x^2 instead of x^{{2}}
            """
            
            print(f"🔄 Calling Claude API for chapter {i}...")
            print(f"📋 Chapter prompt: {chapter_user[:150]}...")
            
            chapter_schema = """
            {
                "chapter_number": 1,
                "title": "Chapter Title",
                "content": "Full chapter content in markdown format with proper LaTeX math notation"
            }
            """
            
            chapter_result = complete_json(WRITER_MODEL, chapter_system, chapter_user, chapter_schema)
            chapter = chapter_result[0] if isinstance(chapter_result, tuple) else chapter_result
            chapter_metadata = chapter_result[1] if isinstance(chapter_result, tuple) else {}
            
            chapter_cost = chapter_metadata.get('cost', 0)
            total_chapter_cost += chapter_cost
            
            print(f"✅ Chapter {i} completed!")
            print(f"💰 Cost: ${chapter_cost:.4f}")
            print(f"🔤 Tokens: {chapter_metadata.get('input_tokens', 0)} input, {chapter_metadata.get('output_tokens', 0)} output")
            print(f"📄 Content length: {len(chapter.get('content', ''))} characters")
            
            chapters.append(chapter)
        
        # Step 3: Combine all chapters into a complete book
        print(f"\n📚 STEP 3: Assembling complete book...")
        
        book_content = f"# {outline.get('title', 'Generated Book')}\n\n"
        book_content += f"*Generated for {request.target_audience} audience in {request.style} style*\n\n"
        book_content += f"*Total estimated pages: {outline.get('total_estimated_pages', request.target_pages)}*\n\n"
        
        for chapter in chapters:
            book_content += f"## {chapter.get('title', '')}\n\n"
            chapter_content = chapter.get('content', '')
            
            # Fix LaTeX formatting for proper rendering
            chapter_content = chapter_content.replace('frac{', '\\frac{')
            chapter_content = chapter_content.replace('partial ', '\\partial ')
            chapter_content = chapter_content.replace('sum_', '\\sum_')
            chapter_content = chapter_content.replace('bar{x}', '\\bar{x}')
            
            book_content += chapter_content + "\n\n"
        
        # Step 4: Save the complete book
        print(f"💾 Saving book to file...")
        book_path = ROOT / "exports" / f"{outline.get('title', 'generated_book').replace(' ', '_').lower()}.md"
        book_path.parent.mkdir(exist_ok=True)
        
        with open(book_path, "w", encoding="utf-8") as f:
            f.write(book_content)
        
        print(f"✅ Book saved: {book_path}")
        print(f"📊 Total book size: {len(book_content)} characters")
        
        # Step 5: Build HTML version with custom styling
        print(f"\n🌐 STEP 4: Building HTML version with {request.book_style} styling...")
        html_path = None
        try:
            html_path = book_path.with_suffix('.html')
            html_content = convert_markdown_to_html_with_math(
                book_content, 
                outline.get('title', 'Generated Book'),
                request.book_style,
                request.custom_style
            )
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"✅ HTML version created with {request.book_style} styling: {html_path}")
            print(f"📊 HTML size: {len(html_content)} characters")
        except Exception as e:
            print(f"⚠️  HTML build failed: {e}")
            print(f"💡 You can manually convert using: pandoc -f markdown -t html --mathjax {book_path} -o {html_path}")
        
        # Calculate total cost
        total_cost = outline_metadata.get('cost', 0) + total_chapter_cost
        
        print(f"\n🎉 BOOK GENERATION COMPLETE!")
        print(f"💰 Total cost: ${total_cost:.4f}")
        print(f"📚 Book: {outline.get('title', 'Generated Book')}")
        print(f"📄 Pages: {outline.get('total_estimated_pages', request.target_pages)}")
        print(f"📑 Chapters: {len(chapters)}")
        print(f"🎨 Style: {request.book_style}")
        
        return {
            "success": True,
            "book_title": outline.get('title', 'Generated Book'),
            "total_chapters": len(chapters),
            "estimated_pages": outline.get('total_estimated_pages', request.target_pages),
            "total_cost": total_cost,
            "book_style": request.book_style,
            "custom_style": request.custom_style,
            "files_created": {
                "markdown": str(book_path),
                "html": str(html_path) if html_path else None
            },
            "outline": outline,
            "chapters": chapters,
            "cost_breakdown": {
                "outline": outline_metadata.get('cost', 0),
                "chapters": total_chapter_cost,
                "total": total_cost
            }
        }
        
    except Exception as e:
        print(f"❌ Book generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Book generation failed: {str(e)}")

@app.post("/generate")
def generate(req: GenerateReq):
    # naive demo writer that stubs chapter content
    (BOOK / "chapters").mkdir(parents=True, exist_ok=True)
    for i, ch in enumerate(req.chapters, 1):
        md = f"# {ch}\n\n" + ("Lorem ipsum " * (req.words_per_chapter//2)) + "\n"
        (BOOK/"chapters"/f"{i:02d}-{ch.replace(' ','-').lower()}.md").write_text(md)
    (BOOK/"config.yml").write_text(f'title: "{req.title}"\n')
    out = ROOT/"exports"/"book.pdf"
    out.parent.mkdir(exist_ok=True, parents=True)
    # compile with pandoc
    md_files = sorted((BOOK/"chapters").glob("*.md"))
    cmd = ["pandoc","-s","--from","markdown+footnotes","--citeproc",
           "--metadata-file", str(BOOK/"config.yml"), "-o", str(out), *map(str, md_files)]
    subprocess.check_call(cmd)
    return {"export": str(out)}

@app.post("/agent/run")
def agent_run(req: AgentReq):
    """Run the reasoning agent"""
    trace, result = run_agent(req.goal, req.model, req.max_steps)
    return {"result": result, "trace": trace}

@app.post("/outline/generate")
def generate_outline_endpoint(req: OutlineReq):
    """Generate book outline"""
    outline, metadata = generate_outline(
        PLANNER_MODEL,
        req.topic,
        req.chapters,
        req.words_per_chapter,
        req.audience,
        req.tone
    )
    
    # Save outline
    T.write_file("toc.yaml", json.dumps(outline, indent=2))
    
    return {"outline": outline, "metadata": metadata}

@app.post("/chapter/write")
def write_chapter_endpoint(chapter_data: dict):
    """Write a chapter"""
    content, metadata = write_chapter(
        WRITER_MODEL,
        chapter_data.get("chapter_brief", {}),
        chapter_data.get("sections", []),
        chapter_data.get("facts", [])
    )
    return {"content": content, "metadata": metadata}

@app.post("/build")
def build_endpoint(format: str = "html"):
    """Build the book"""
    result = T.build_book(format)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
