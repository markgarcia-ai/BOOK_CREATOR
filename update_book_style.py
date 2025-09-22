#!/usr/bin/env python3
"""
Utility to update existing books with new styles
"""

import argparse
import json
from pathlib import Path
from backend.book_styles import get_style, create_custom_style

def create_mathjax_html_template(title: str, content: str, book_style: str = "modern", custom_style: dict = None) -> str:
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

def convert_markdown_to_html_with_math(markdown_content: str, title: str, book_style: str = "modern", custom_style: dict = None) -> str:
    """Convert markdown to HTML with proper math rendering and custom styling"""
    import subprocess
    
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

def update_book_style(markdown_file: str, output_file: str = None, book_style: str = "modern", custom_style: dict = None):
    """Update an existing book with a new style"""
    
    markdown_path = Path(markdown_file)
    if not markdown_path.exists():
        print(f"❌ Error: Markdown file not found: {markdown_file}")
        return
    
    # Read the markdown content
    markdown_content = markdown_path.read_text(encoding='utf-8')
    
    # Extract title from first line or filename
    title = markdown_path.stem.replace('_', ' ').title()
    if markdown_content.startswith('# '):
        title = markdown_content.split('\n')[0][2:].strip()
    
    # Generate output filename if not provided
    if not output_file:
        output_file = markdown_path.parent / f"{markdown_path.stem}_{book_style}.html"
    
    # Convert to HTML with new style
    print(f"🎨 Converting '{markdown_path.name}' to {book_style} style...")
    html_content = convert_markdown_to_html_with_math(markdown_content, title, book_style, custom_style)
    
    # Write the HTML file
    output_path = Path(output_file)
    output_path.write_text(html_content, encoding='utf-8')
    
    print(f"✅ Updated book saved: {output_path}")
    print(f"📊 File size: {output_path.stat().st_size:,} bytes")
    print(f"🎨 Style: {book_style}")
    if custom_style:
        print(f"🎨 Custom options: {custom_style}")

def main():
    parser = argparse.ArgumentParser(description="Update existing books with new styles")
    parser.add_argument("markdown_file", help="Path to the markdown file to update")
    parser.add_argument("-o", "--output", help="Output HTML file path")
    parser.add_argument("-s", "--style", default="modern", 
                       choices=["academic", "modern", "compact", "ebook", "minimal"],
                       help="Book style to apply")
    
    # Custom style options
    parser.add_argument("--font-family", help="Custom font family")
    parser.add_argument("--line-height", help="Custom line height")
    parser.add_argument("--paragraph-spacing", help="Custom paragraph spacing")
    parser.add_argument("--header-spacing", help="Custom header spacing")
    parser.add_argument("--max-width", help="Custom max width")
    parser.add_argument("--color-scheme", help="Custom color scheme")
    
    args = parser.parse_args()
    
    # Prepare custom style if any custom options are provided
    custom_style = None
    if any([args.font_family, args.line_height, args.paragraph_spacing, 
            args.header_spacing, args.max_width, args.color_scheme]):
        custom_style = {}
        if args.font_family:
            custom_style["font_family"] = args.font_family
        if args.line_height:
            custom_style["line_height"] = args.line_height
        if args.paragraph_spacing:
            custom_style["paragraph_spacing"] = args.paragraph_spacing
        if args.header_spacing:
            custom_style["header_spacing"] = args.header_spacing
        if args.max_width:
            custom_style["max_width"] = args.max_width
        if args.color_scheme:
            custom_style["color_scheme"] = args.color_scheme
    
    update_book_style(args.markdown_file, args.output, args.style, custom_style)

if __name__ == "__main__":
    main()
