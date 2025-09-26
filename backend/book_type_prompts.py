"""
Book Type-Specific Prompt Generation System
"""

from typing import Dict, Any, Optional

def generate_book_type_system_prompt(book_type_info: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a system prompt based on book type information
    
    Args:
        book_type_info: Dictionary containing book type specifications
        
    Returns:
        Enhanced system prompt tailored to the book type
    """
    
    base_prompt = """You are an expert book writer. Write high-quality, well-structured book sections in Markdown format.

## RULES:
1. Use proper Markdown formatting with headings (##, ###)
2. Include in-text citations [@citeKey] for all non-obvious claims
3. Use figure placeholders: {{FIG:slug:"caption"}}
4. If a claim lacks supporting evidence, insert [[NEEDS_SOURCE]]
5. End each section with a "Summary" and "Key Takeaways" list
6. Write in a clear, engaging, and professional tone
7. Maintain consistency with the book's overall style and audience

## CITATION FORMAT:
- Use [@citeKey] for in-text citations
- Only cite when making specific claims that need support
- If no supporting evidence is available, use [[NEEDS_SOURCE]]
- Citations should be natural and not interrupt flow

## FIGURE FORMAT:
- Use {{FIG:slug:"caption"}} for figure placeholders
- slug should be descriptive (e.g., "system-architecture", "data-flow")
- caption should be informative and standalone
- Plan figures that enhance understanding

## STRUCTURE:
- Start with a brief introduction to the section
- Use subheadings to organize content logically
- Include examples and explanations
- End with Summary and Key Takeaways"""

    if not book_type_info:
        return base_prompt

    # Add book-type-specific enhancements
    book_type_prompt = f"""

## BOOK TYPE SPECIFICATIONS:
- **Book Type**: {book_type_info.get('name', 'Generic')}
- **Target Audience**: {book_type_info.get('target_audience', 'General readers')}
- **Writing Style**: {book_type_info.get('writing_style', 'Professional and accessible')}
- **Content Approach**: {book_type_info.get('content_approach', 'Balanced theory and practice')}
- **Tone**: {book_type_info.get('tone_description', 'Clear and engaging')}

## CONTENT EMPHASIS:
"""
    
    # Add section emphasis points
    section_emphasis = book_type_info.get('section_emphasis', [])
    if section_emphasis:
        for emphasis in section_emphasis:
            book_type_prompt += f"- {emphasis}\n"
    
    # Add prompt modifiers
    prompt_modifiers = book_type_info.get('prompt_modifiers', {})
    if prompt_modifiers:
        book_type_prompt += "\n## SPECIFIC INSTRUCTIONS:\n"
        
        if 'structure' in prompt_modifiers:
            book_type_prompt += f"**Structure Requirements**: {prompt_modifiers['structure']}\n\n"
        
        if 'depth' in prompt_modifiers:
            book_type_prompt += f"**Content Depth**: {prompt_modifiers['depth']}\n\n"
        
        if 'examples' in prompt_modifiers:
            book_type_prompt += f"**Examples and Applications**: {prompt_modifiers['examples']}\n\n"

    return base_prompt + book_type_prompt


def generate_book_type_user_prompt(
    topic: str,
    book_type_info: Optional[Dict[str, Any]] = None,
    context_facts: Optional[str] = None,
    target_words: int = 1500
) -> str:
    """
    Generate a user prompt based on book type for content generation
    
    Args:
        topic: The section topic
        book_type_info: Book type specifications
        context_facts: Additional context or facts
        target_words: Target word count
        
    Returns:
        Book-type-aware user prompt
    """
    
    base_prompt = f"""Write a comprehensive book section on the following topic:

**Topic**: {topic}
**Target Length**: Approximately {target_words:,} words

**Requirements**:
1. Create engaging, informative content
2. Use clear markdown formatting
3. Include relevant examples
4. Ensure logical flow and organization
5. End with summary and key takeaways"""

    if not book_type_info:
        if context_facts:
            base_prompt += f"\n\n**Context/Facts to Consider**:\n{context_facts}"
        return base_prompt

    # Add book-type-specific instructions
    book_type_additions = f"""

**Book Type Context**:
- Writing for: {book_type_info.get('target_audience', 'general readers')}
- Style: {book_type_info.get('writing_style', 'professional')}
- Approach: {book_type_info.get('content_approach', 'balanced')}
"""

    # Add specific instructions based on book type
    prompt_modifiers = book_type_info.get('prompt_modifiers', {})
    if prompt_modifiers:
        book_type_additions += "\n**Specific Instructions for this Book Type**:\n"
        
        for key, instruction in prompt_modifiers.items():
            book_type_additions += f"- **{key.title()}**: {instruction}\n"

    # Add context facts if provided
    if context_facts:
        base_prompt += f"\n\n**Context/Facts to Consider**:\n{context_facts}"

    return base_prompt + book_type_additions


def get_book_type_outline_instructions(book_type_info: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate book-type-specific outline instructions
    
    Args:
        book_type_info: Book type specifications
        
    Returns:
        Book-type-aware outline instructions
    """
    
    base_instructions = """Create a comprehensive book outline with well-structured chapters.

REQUIREMENTS:
1. Create well-structured chapters
2. Each chapter should have 3-5 sections
3. Include 1-2 images per chapter
4. Ensure logical progression from basic to advanced concepts
5. Make slugs descriptive and URL-friendly
6. Set realistic word count targets
7. Include engaging chapter and section titles
8. Plan relevant images that support the content"""

    if not book_type_info:
        return base_instructions

    # Add book-type-specific outline instructions
    book_type_instructions = f"""

BOOK TYPE SPECIFICATIONS:
- Target Audience: {book_type_info.get('target_audience', 'General readers')}
- Writing Style: {book_type_info.get('writing_style', 'Professional')}
- Content Focus: {book_type_info.get('content_approach', 'Balanced approach')}

CONTENT EMPHASIS FOR THIS BOOK TYPE:
"""
    
    section_emphasis = book_type_info.get('section_emphasis', [])
    for emphasis in section_emphasis:
        book_type_instructions += f"- {emphasis}\n"

    prompt_modifiers = book_type_info.get('prompt_modifiers', {})
    if 'structure' in prompt_modifiers:
        book_type_instructions += f"\nSTRUCTURE GUIDELINES: {prompt_modifiers['structure']}"

    return base_instructions + book_type_instructions
