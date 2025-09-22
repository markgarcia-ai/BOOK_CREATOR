from typing import Optional, Dict, Any
import json
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from .settings import BOOK, CHAPTERS, ASSETS, EXPORTS, ROOT

def write_file(relpath: str, text: str) -> Dict[str, Any]:
    """Write text to a file and return metadata"""
    p = (BOOK / relpath).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if content changed
    before_hash = None
    if p.exists():
        before_hash = hashlib.md5(p.read_text().encode()).hexdigest()
    
    p.write_text(text)
    after_hash = hashlib.md5(text.encode()).hexdigest()
    
    return {
        "path": str(p),
        "bytes": len(text.encode()),
        "updated": before_hash != after_hash,
        "hash": after_hash
    }

def read_file(relpath: str) -> Dict[str, Any]:
    """Read a file and return content with metadata"""
    p = (BOOK / relpath).resolve()
    if not p.exists():
        return {"error": f"File not found: {relpath}"}
    
    content = p.read_text()
    return {
        "path": str(p),
        "content": content,
        "bytes": len(content.encode()),
        "hash": hashlib.md5(content.encode()).hexdigest()
    }

def build_book(fmt: str = "pdf") -> Dict[str, Any]:
    """Build book using Pandoc"""
    EXPORTS.mkdir(parents=True, exist_ok=True)
    out = EXPORTS / f"book.{fmt}"
    
    # Find all markdown files in chapters
    md_files = sorted(CHAPTERS.glob("*.md"))
    if not md_files:
        return {"error": "No markdown files found in chapters directory"}
    
    # Build Pandoc command
    cmd = [
        "pandoc", "-s", 
        "--from", "markdown+footnotes+raw_tex",
        "--citeproc", 
        "--metadata-file", str(BOOK / "config.yml"),
        "-o", str(out)
    ] + [str(f) for f in md_files]
    
    try:
        subprocess.check_call(cmd, cwd=str(ROOT))
        return {
            "export": str(out),
            "chapters": [m.name for m in md_files],
            "format": fmt,
            "success": True
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": f"Pandoc build failed: {e}",
            "format": fmt,
            "success": False
        }

def list_chapters() -> Dict[str, Any]:
    """List all available chapters"""
    md_files = sorted(CHAPTERS.glob("*.md"))
    return {
        "chapters": [f.stem for f in md_files],
        "count": len(md_files)
    }

def get_project_status() -> Dict[str, Any]:
    """Get overall project status"""
    chapters = list_chapters()
    config_exists = (BOOK / "config.yml").exists()
    toc_exists = (BOOK / "toc.yaml").exists()
    
    return {
        "chapters": chapters["chapters"],
        "chapter_count": chapters["count"],
        "config_exists": config_exists,
        "toc_exists": toc_exists,
        "exports": list(EXPORTS.glob("*")) if EXPORTS.exists() else []
    }

def create_project_structure(title: str) -> Dict[str, Any]:
    """Create basic project structure"""
    # Create config.yml
    config_content = f'title: "{title}"\n'
    config_result = write_file("config.yml", config_content)
    
    # Create basic toc.yaml
    toc_content = f"""title: "{title}"
chapters: []
"""
    toc_result = write_file("toc.yaml", toc_content)
    
    return {
        "config": config_result,
        "toc": toc_result,
        "title": title
    }

def convert_markdown_to_html_with_math_advanced(markdown_content: str, title: str, book_style: str = "modern", custom_style: Optional[Dict] = None) -> str:
    """Convert markdown content to HTML with MathJax support"""
    try:
        import markdown
        from markdown.extensions import codehilite, fenced_code, tables, toc
        from .book_styles import get_style
        
        # Configure markdown extensions
        extensions = [
            'codehilite',
            'fenced_code', 
            'tables',
            'toc',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.footnotes',
            'markdown.extensions.md_in_html'
        ]
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=extensions)
        html_content = md.convert(markdown_content)
        
        # Get style CSS
        style_css = get_style(book_style, custom_style)
        
        # Create complete HTML document with MathJax
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {style_css}
    </style>
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
    <div class="book-container">
        {html_content}
    </div>
</body>
</html>"""
        
        return full_html
        
    except Exception as e:
        # Fallback: simple HTML without MathJax
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div>{markdown_content.replace(chr(10), '<br>')}</div>
</body>
</html>"""

def save_html_file(html_content: str, output_path: str) -> Dict[str, Any]:
    """Save HTML content to file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return {"success": True, "html_path": output_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

def simple_markdown_to_html(markdown_content: str, title: str) -> str:
    """Simple markdown to HTML conversion without external dependencies"""
    import re
    
    # Basic markdown to HTML conversion
    html = markdown_content
    
    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Code blocks
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Lists
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Line breaks
    html = html.replace('\n', '<br>\n')
    
    # Create complete HTML document
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{ 
            color: #2c3e50; 
            margin-top: 2em;
            margin-bottom: 1em;
        }}
        h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 0.5em; }}
        h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 0.3em; }}
        code {{ 
            background: #f8f9fa; 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }}
        pre {{ 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto; 
            border-left: 4px solid #3498db;
        }}
        pre code {{ background: none; padding: 0; }}
        ul {{ padding-left: 1.5em; }}
        li {{ margin-bottom: 0.5em; }}
        blockquote {{ 
            border-left: 4px solid #3498db; 
            margin: 1em 0; 
            padding-left: 1em; 
            color: #666;
            font-style: italic;
        }}
        .math {{ 
            background: #f0f0f0; 
            padding: 2px 4px; 
            border-radius: 3px; 
            font-family: 'Times New Roman', serif;
        }}
    </style>
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
    <div class="book-container">
        {html}
    </div>
</body>
</html>"""
    
    return full_html

def convert_markdown_to_html_with_math(markdown_content: str, title: str, book_style: str = "modern", custom_style: Optional[Dict] = None) -> str:
    """Convert markdown content to HTML with MathJax support - main function with fallback"""
    try:
        # Try the advanced version first
        return convert_markdown_to_html_with_math_advanced(markdown_content, title, book_style, custom_style)
    except Exception as e:
        # Fallback to simple version
        return simple_markdown_to_html(markdown_content, title)
