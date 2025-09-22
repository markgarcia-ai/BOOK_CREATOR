#!/usr/bin/env python3
"""
Fix mathematical formatting in generated books
"""

import re
from pathlib import Path

def fix_math_formatting(content: str) -> str:
    """Fix mathematical formatting in markdown content"""
    
    # Fix LaTeX math formatting
    # Convert $equation$ to proper LaTeX format
    content = re.sub(r'\$([^$]+)\$', r'$\1$', content)
    
    # Fix common math issues
    content = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\\frac{\1}{\2}', content)
    content = re.sub(r'\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}', r'\\frac{\1}{\2}', content)
    
    # Fix exponent formatting
    content = re.sub(r'e\^\{([^}]+)\}', r'e^{\1}', content)
    content = re.sub(r'e\^-\{([^}]+)\}', r'e^{-\1}', content)
    
    # Fix partial derivatives
    content = re.sub(r'\\partial\s+([a-zA-Z])', r'\\partial \1', content)
    
    return content

def create_mathjax_html(markdown_file: str, output_file: str = None):
    """Create HTML with MathJax support from markdown"""
    
    if output_file is None:
        output_file = markdown_file.replace('.md', '_fixed.html')
    
    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix math formatting
    fixed_content = fix_math_formatting(content)
    
    # Escape content for HTML
    escaped_content = fixed_content.replace('`', '\\`').replace('\\', '\\\\')
    
    # Create HTML template with MathJax
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fixed Book with MathJax</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 2em;
            margin-bottom: 1em;
        }}
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
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
        <strong>Fixed Book with MathJax Support</strong><br>
        <em>Mathematical equations should now render properly</em>
    </div>
    <div id="content">
        <!-- Content will be inserted here -->
    </div>
    
    <script>
        // Convert markdown to HTML (simple conversion)
        const markdown = `{escaped_content}`;
        
        // Simple markdown to HTML conversion
        let html = markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
            .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
            .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\\n\\n/g, '</p><p>')
            .replace(/\\n/g, '<br>');
        
        // Wrap in paragraphs
        html = '<p>' + html + '</p>';
        
        document.getElementById('content').innerHTML = html;
        
        // Process MathJax after content is loaded
        if (window.MathJax) {{
            MathJax.typesetPromise();
        }}
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Created fixed HTML: {output_file}")
    return output_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fix_math_formatting.py <markdown_file> [output_file]")
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(markdown_file).exists():
        print(f"❌ File not found: {markdown_file}")
        sys.exit(1)
    
    create_mathjax_html(markdown_file, output_file)
