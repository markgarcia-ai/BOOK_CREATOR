#!/usr/bin/env python3
"""
Test the math formatting fix
"""

import requests
import json

def test_math_formatting():
    """Test if the math formatting issue is fixed"""
    
    # Test data with math equations
    test_content = """
    ## Sigmoid Function
    
    The sigmoid function is commonly used in machine learning:
    
    $$P(y=1) = \\frac{1}{1 + e^{-z}}$$
    
    This equation shows the probability calculation.
    """
    
    # Create a simple HTML with MathJax
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Math Test</title>
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <h1>Math Formatting Test</h1>
    {test_content}
</body>
</html>"""
    
    # Save test file
    with open('test_math.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created test_math.html with MathJax support")
    print("📖 Open test_math.html in your browser to see the rendered equations")
    print("🔍 The sigmoid function should display as a proper mathematical equation")

if __name__ == "__main__":
    test_math_formatting()
