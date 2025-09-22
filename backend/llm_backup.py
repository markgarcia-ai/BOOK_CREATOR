import os, json, re
from anthropic import Anthropic
from .settings import ANTHROPIC_API_KEY, MODEL_NAME

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def clean_json_response(content: str) -> str:
    """Clean JSON response from Claude"""
    # Remove markdown code blocks
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    # Remove control characters that break JSON
    content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
    
    # Handle LaTeX backslashes more carefully
    # Replace problematic LaTeX backslashes with placeholders before JSON parsing
    content = content.replace('\\\\', '__DOUBLE_BACKSLASH__')
    content = content.replace('\\', '__SINGLE_BACKSLASH__')
    
    # Fix common JSON issues
    content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    return content

def restore_latex_backslashes(content: str) -> str:
    """Restore LaTeX backslashes after JSON parsing"""
    content = content.replace('__SINGLE_BACKSLASH__', '\\\\')
    content = content.replace('__DOUBLE_BACKSLASH__', '\\\\\\\\')
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
        
        # Estimate cost (rough approximation)
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
    max_tokens: int = 1400
) -> tuple[dict, dict]:
    """
    Get structured JSON response from Claude
    Returns: (parsed_json, metadata)
    """
    prompt = f"""{system}

Return ONLY valid JSON matching this schema:
{schema_hint}

USER:
{user}

IMPORTANT: Return ONLY the JSON object, no other text, no markdown formatting, no explanations.
For mathematical expressions, use simple LaTeX without complex backslashes that break JSON parsing.
Use 'frac' instead of '\\frac', 'partial' instead of '\\partial', etc."""

    content, metadata = chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    
    try:
        # Clean the response
        cleaned_content = clean_json_response(content)
        parsed_json = json.loads(cleaned_content)
        
        # Restore backslashes in content fields for proper LaTeX rendering
        if isinstance(parsed_json, dict):
            for key, value in parsed_json.items():
                if isinstance(value, str) and ('content' in key.lower() or 'text' in key.lower()):
                    parsed_json[key] = restore_latex_backslashes(value)

        return parsed_json, metadata
        
    except json.JSONDecodeError as e:
        # Try to extract JSON from the response
        try:
            # Look for JSON object in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                json_str = clean_json_response(json_str)
                parsed_json = json.loads(json_str)
                
                # Restore backslashes in content fields
                if isinstance(parsed_json, dict):
                    for key, value in parsed_json.items():
                        if isinstance(value, str) and ('content' in key.lower() or 'text' in key.lower()):
                            parsed_json[key] = restore_latex_backslashes(value)

                return parsed_json, metadata
        except:
            pass
        
        raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {content}")

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for token usage"""
    return (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
