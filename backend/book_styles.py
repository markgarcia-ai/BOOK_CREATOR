"""
Book styling and formatting options
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class BookStyle:
    name: str
    description: str
    css_styles: str
    paragraph_spacing: str
    header_spacing: str
    font_family: str
    line_height: str
    max_width: str

# Predefined book styles
BOOK_STYLES = {
    "academic": BookStyle(
        name="Academic",
        description="Formal academic style with tight spacing",
        css_styles="""
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.4;
            max-width: 700px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: bold;
        }
        h1 {
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 8px;
            font-size: 2.2em;
        }
        h2 {
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 4px;
            font-size: 1.8em;
        }
        h3 {
            font-size: 1.4em;
        }
        p {
            margin-bottom: 0.8em;
            text-align: justify;
        }
        """,
        paragraph_spacing="0.8em",
        header_spacing="1.5em",
        font_family="Times New Roman",
        line_height="1.4",
        max_width="700px"
    ),
    
    "modern": BookStyle(
        name="Modern",
        description="Clean modern style with generous spacing",
        css_styles="""
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 60px 40px;
            color: #333;
            background-color: #fafafa;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 2.5em;
            margin-bottom: 1em;
            font-weight: 600;
        }
        h1 {
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            font-size: 2.5em;
        }
        h2 {
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            font-size: 2em;
        }
        h3 {
            font-size: 1.6em;
        }
        p {
            margin-bottom: 1.5em;
            text-align: left;
        }
        """,
        paragraph_spacing="1.5em",
        header_spacing="2.5em",
        font_family="System Font",
        line_height="1.6",
        max_width="800px"
    ),
    
    "compact": BookStyle(
        name="Compact",
        description="Space-efficient style for maximum content",
        css_styles="""
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.3;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px 30px;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 1em;
            margin-bottom: 0.3em;
            font-weight: bold;
        }
        h1 {
            border-bottom: 1px solid #2c3e50;
            padding-bottom: 5px;
            font-size: 1.8em;
        }
        h2 {
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 3px;
            font-size: 1.5em;
        }
        h3 {
            font-size: 1.3em;
        }
        p {
            margin-bottom: 0.5em;
            text-align: left;
        }
        """,
        paragraph_spacing="0.5em",
        header_spacing="1em",
        font_family="Helvetica",
        line_height="1.3",
        max_width="900px"
    ),
    
    "ebook": BookStyle(
        name="E-book",
        description="Optimized for e-readers and mobile devices",
        css_styles="""
        body {
            font-family: Georgia, 'Times New Roman', serif;
            line-height: 1.5;
            max-width: 100%;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 1.8em;
            margin-bottom: 0.8em;
            font-weight: bold;
        }
        h1 {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            font-size: 2em;
        }
        h2 {
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
            font-size: 1.6em;
        }
        h3 {
            font-size: 1.4em;
        }
        p {
            margin-bottom: 1em;
            text-align: left;
        }
        @media (max-width: 768px) {
            body {
                padding: 15px;
                font-size: 16px;
            }
            h1 { font-size: 1.8em; }
            h2 { font-size: 1.5em; }
            h3 { font-size: 1.3em; }
        }
        """,
        paragraph_spacing="1em",
        header_spacing="1.8em",
        font_family="Georgia",
        line_height="1.5",
        max_width="100%"
    ),
    
    "minimal": BookStyle(
        name="Minimal",
        description="Clean minimal style with focus on content",
        css_styles="""
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.4;
            max-width: 750px;
            margin: 0 auto;
            padding: 50px 30px;
            color: #444;
            background-color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333;
            margin-top: 2em;
            margin-bottom: 0.5em;
            font-weight: normal;
        }
        h1 {
            border-bottom: none;
            padding-bottom: 0;
            font-size: 2.2em;
            font-weight: 300;
        }
        h2 {
            border-bottom: none;
            padding-bottom: 0;
            font-size: 1.8em;
            font-weight: 400;
        }
        h3 {
            font-size: 1.4em;
            font-weight: 500;
        }
        p {
            margin-bottom: 1.2em;
            text-align: left;
        }
        """,
        paragraph_spacing="1.2em",
        header_spacing="2em",
        font_family="Arial",
        line_height="1.4",
        max_width="750px"
    )
}

def get_style(style_name: str) -> BookStyle:
    """Get a book style by name"""
    return BOOK_STYLES.get(style_name.lower(), BOOK_STYLES["modern"])

def list_styles() -> Dict[str, str]:
    """List all available styles"""
    return {name: style.description for name, style in BOOK_STYLES.items()}

def create_custom_style(
    name: str,
    font_family: str = "Arial",
    line_height: str = "1.5",
    paragraph_spacing: str = "1em",
    header_spacing: str = "2em",
    max_width: str = "800px",
    color_scheme: str = "default"
) -> BookStyle:
    """Create a custom book style"""
    
    color_schemes = {
        "default": {"text": "#333", "headers": "#2c3e50", "border": "#3498db"},
        "dark": {"text": "#e0e0e0", "headers": "#ffffff", "border": "#4a9eff"},
        "sepia": {"text": "#5c4b37", "headers": "#3d2f1f", "border": "#8b7355"},
        "blue": {"text": "#2c3e50", "headers": "#1a252f", "border": "#3498db"}
    }
    
    colors = color_schemes.get(color_scheme, color_schemes["default"])
    
    css_styles = f"""
    body {{
        font-family: '{font_family}', sans-serif;
        line-height: {line_height};
        max-width: {max_width};
        margin: 0 auto;
        padding: 40px 30px;
        color: {colors['text']};
        background-color: #fff;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {colors['headers']};
        margin-top: {header_spacing};
        margin-bottom: 0.5em;
        font-weight: bold;
    }}
    h1 {{
        border-bottom: 2px solid {colors['border']};
        padding-bottom: 10px;
        font-size: 2.2em;
    }}
    h2 {{
        border-bottom: 1px solid {colors['border']};
        padding-bottom: 5px;
        font-size: 1.8em;
    }}
    h3 {{
        font-size: 1.4em;
    }}
    p {{
        margin-bottom: {paragraph_spacing};
        text-align: left;
    }}
    """
    
    return BookStyle(
        name=name,
        description=f"Custom style: {font_family}, {line_height} line height",
        css_styles=css_styles,
        paragraph_spacing=paragraph_spacing,
        header_spacing=header_spacing,
        font_family=font_family,
        line_height=line_height,
        max_width=max_width
    )
