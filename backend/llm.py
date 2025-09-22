import os, json, re
from anthropic import Anthropic
from .settings import ANTHROPIC_API_KEY, MODEL_NAME

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def clean_json_response(content: str) -> str:
    """Clean JSON response from Claude with enhanced LaTeX handling"""
    # Remove markdown code blocks
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    # Remove control characters that break JSON
    content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
    
    # Enhanced LaTeX handling - replace problematic patterns
    content = re.sub(r'\\begin\{[^}]*\}', '__LATEX_BEGIN__', content)
    content = re.sub(r'\\end\{[^}]*\}', '__LATEX_END__', content)
    content = re.sub(r'\\frac\{[^}]*\}\{[^}]*\}', '__LATEX_FRAC__', content)
    content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '__LATEX_CMD__', content)
    content = re.sub(r'\\\\', '__LATEX_DOUBLE_BACKSLASH__', content)
    content = re.sub(r'\\[^a-zA-Z]', '__LATEX_ESCAPE__', content)
    
    # Fix common JSON issues
    content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    return content

def restore_latex_backslashes(content: str) -> str:
    """Restore LaTeX backslashes after JSON parsing"""
    content = content.replace('__LATEX_ESCAPE__', '\\')
    content = content.replace('__LATEX_DOUBLE_BACKSLASH__', '\\\\')
    content = content.replace('__LATEX_CMD__', '\\command{}')
    content = content.replace('__LATEX_FRAC__', '\\frac{}{}')
    content = content.replace('__LATEX_END__', '\\end{}')
    content = content.replace('__LATEX_BEGIN__', '\\begin{}')
    return content

def extract_json_from_response(content: str) -> str:
    """Extract JSON from response with multiple fallback strategies"""
    # Strategy 1: Look for complete JSON object
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    # Strategy 2: Look for JSON between first { and last }
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return content[first_brace:last_brace + 1]
    
    return content

def chat(model: str, messages: list, max_tokens: int = 1400) -> tuple[str, dict]:
    """Chat with Claude and return response with metadata"""
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages
        )
        
        content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        
        cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
        
        metadata = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        
        return content, metadata
        
    except Exception as e:
        raise Exception(f"Claude API error: {e}")

def complete_json(
    model: str, 
    system: str, 
    user: str, 
    schema_hint: str,
    max_tokens: int = 1400,
    max_retries: int = 3
) -> tuple[dict, dict]:
    """Get structured JSON response from Claude with enhanced error handling"""
    
    for attempt in range(max_retries):
        try:
            prompt = f"""{system}

Return ONLY valid JSON matching this schema:
{schema_hint}

USER:
{user}

CRITICAL JSON REQUIREMENTS:
- Return ONLY the JSON object, no other text, no markdown formatting
- For mathematical expressions, use simple LaTeX without complex backslashes
- Use 'frac' instead of '\\frac', 'partial' instead of '\\partial'
- Avoid nested braces in LaTeX expressions
- Use single quotes for strings if needed to avoid escaping issues
- Ensure all braces and brackets are properly matched"""

            content, metadata = chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            # Try multiple parsing strategies
            parsed_json = None
            
            # Strategy 1: Direct parsing
            try:
                cleaned_content = clean_json_response(content)
                parsed_json = json.loads(cleaned_content)
            except json.JSONDecodeError:
                pass
            
            # Strategy 2: Extract and parse
            if parsed_json is None:
                try:
                    json_str = extract_json_from_response(content)
                    cleaned_content = clean_json_response(json_str)
                    parsed_json = json.loads(cleaned_content)
                except json.JSONDecodeError:
                    pass
            
            # Strategy 3: Manual JSON construction for common patterns
            if parsed_json is None:
                try:
                    title_match = re.search(r'"title":\s*"([^"]*)"', content)
                    content_match = re.search(r'"content":\s*"([^"]*(?:\\.[^"]*)*)"', content, re.DOTALL)
                    chapter_match = re.search(r'"chapter_number":\s*(\d+)', content)
                    
                    if title_match and content_match:
                        parsed_json = {
                            "title": title_match.group(1),
                            "content": content_match.group(1),
                            "chapter_number": int(chapter_match.group(1)) if chapter_match else 1
                        }
                except:
                    pass
            
            if parsed_json is not None:
                # Restore backslashes in content fields for proper LaTeX rendering
                if isinstance(parsed_json, dict):
                    for key, value in parsed_json.items():
                        if isinstance(value, str) and ('content' in key.lower() or 'text' in key.lower()):
                            parsed_json[key] = restore_latex_backslashes(value)
                
                return parsed_json, metadata
            
            raise ValueError(f"All JSON parsing strategies failed on attempt {attempt + 1}")
            
        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed, return fallback JSON
                print(f"Warning: JSON parsing failed after {max_retries} attempts: {e}")
                fallback_json = {
                    "title": "Chapter Content",
                    "content": f"# Chapter Content\n\nThis chapter could not be generated due to a technical error.\n\nError: {str(e)[:200]}...\n\n## Summary\n\nThis section requires manual review and completion.\n\n## Key Takeaways\n\n- Technical error encountered during generation\n- Manual review required\n- Content needs to be completed manually",
                    "chapter_number": 1
                }
                return fallback_json, metadata
            else:
                print(f"JSON parsing attempt {attempt + 1} failed: {e}")
                continue
    
    return {"error": "JSON parsing failed"}, {"error": True}

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for token usage"""
    return (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
