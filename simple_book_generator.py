#!/usr/bin/env python3
"""
Simple book generator that works around the JSON parsing issues
"""

import json
import subprocess
from pathlib import Path
from backend.book_styles import get_style, create_custom_style

def create_simple_html_template(title: str, content: str, book_style: str = "modern", custom_style: dict = None) -> str:
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

def convert_markdown_to_html(markdown_content: str, title: str, book_style: str = "modern", custom_style: dict = None) -> str:
    """Convert markdown to HTML with proper math rendering and custom styling"""
    try:
        # Use pandoc to convert markdown to HTML
        cmd = ["pandoc", "-f", "markdown", "-t", "html", "--mathjax"]
        result = subprocess.run(cmd, input=markdown_content, text=True, capture_output=True, check=True)
        html_content = result.stdout
        
        # Create full HTML document with MathJax and custom styling
        full_html = create_simple_html_template(title, html_content, book_style, custom_style)
        return full_html
        
    except subprocess.CalledProcessError as e:
        print(f"Pandoc conversion failed: {e}")
        # Fallback: simple HTML conversion
        html_content = markdown_content.replace('\n', '<br>\n')
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n')
        return create_simple_html_template(title, html_content, book_style, custom_style)

def generate_technical_book_example():
    """Generate a technical book example with different styles"""
    
    # Sample technical content
    technical_content = """# Advanced Python Programming

*Generated for senior developers in technical style*

## Chapter 1: Advanced Language Features

### Metaclasses: The Class Factory

**Metaclasses** are powerful mechanisms for dynamically controlling class creation and behavior.

#### Core Concepts

- Metaclasses are *classes that define how other classes are created*
- They provide a way to customize class instantiation
- Python's default metaclass is `type`

#### Example Implementation

```python
class LoggingMeta(type):
    def __new__(cls, name, bases, attrs):
        # Add logging to class methods
        for attr_name, attr_value in attrs.items():
            if callable(attr_value):
                attrs[attr_name] = cls.log_call(attr_value)
        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def log_call(func):
        def wrapper(*args, **kwargs):
            print(f"Calling {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
```

### Descriptors: Attribute Management

**Descriptors** provide a mechanism to customize how attributes are accessed, set, and deleted.

#### Descriptor Protocol

- Implements `__get__()`, `__set__()`, and `__delete__()` methods
- Used for creating managed attributes
- Enable advanced property behaviors

#### Mathematical Foundation

The descriptor protocol can be represented mathematically:

$$P(access) = \\frac{valid\\_accesses}{total\\_accesses}$$

Where valid accesses follow the descriptor protocol.

## Chapter 2: Performance Optimization

### Memory Management

Python's memory management can be optimized through several techniques:

1. **Object Pooling**: Reuse objects to reduce allocation overhead
2. **Weak References**: Prevent circular references
3. **Generators**: Lazy evaluation for large datasets

### Algorithmic Complexity

Understanding Big O notation is crucial for performance:

- **O(1)**: Constant time operations
- **O(log n)**: Logarithmic time (binary search)
- **O(n)**: Linear time (simple iteration)
- **O(n²)**: Quadratic time (nested loops)

## Conclusion

Advanced Python programming requires understanding of:

- Metaclasses and descriptors
- Performance optimization techniques
- Memory management strategies
- Algorithmic complexity analysis

These concepts enable building robust, efficient, and maintainable Python applications.
"""

    # Generate different style versions
    styles_to_generate = [
        ("academic", "Academic Style - Formal with tight spacing"),
        ("modern", "Modern Style - Clean with generous spacing"),
        ("compact", "Compact Style - Space-efficient for maximum content"),
        ("ebook", "E-book Style - Optimized for mobile devices"),
        ("minimal", "Minimal Style - Clean focus on content")
    ]
    
    # Custom technical style
    custom_technical_style = {
        "font_family": "Monaco",
        "line_height": "1.3",
        "paragraph_spacing": "0.8em",
        "header_spacing": "1.5em",
        "max_width": "900px",
        "color_scheme": "blue"
    }
    
    print("🎨 Generating technical book with different styles...")
    
    for style_name, description in styles_to_generate:
        print(f"\n📖 Generating {style_name} style: {description}")
        
        html_content = convert_markdown_to_html(
            technical_content, 
            "Advanced Python Programming",
            style_name
        )
        
        output_path = Path("exports") / f"advanced_python_{style_name}.html"
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        print(f"✅ Created: {output_path} ({output_path.stat().st_size:,} bytes)")
    
    # Generate custom technical style
    print(f"\n🎨 Generating custom technical style...")
    html_content = convert_markdown_to_html(
        technical_content, 
        "Advanced Python Programming",
        "modern",
        custom_technical_style
    )
    
    output_path = Path("exports") / "advanced_python_custom_technical.html"
    output_path.write_text(html_content, encoding='utf-8')
    
    print(f"✅ Created: {output_path} ({output_path.stat().st_size:,} bytes)")
    
    print(f"\n🎉 All style versions generated successfully!")
    print(f"📁 Check the exports/ folder to see all the different styles")
    print(f"�� Open any HTML file in your browser to see the styling differences")

if __name__ == "__main__":
    generate_technical_book_example()
