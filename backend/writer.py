import json
from typing import Dict, List, Any
from .llm import chat  # Use direct chat instead of complete_json
from .settings import WRITER_MODEL
from .prompt_loader import get_writer_prompt
from rag.retrieve import fact_pack

# Get writer system prompt from external file
WRITER_SYSTEM = get_writer_prompt()

def write_section(
    model: str, 
    brief: Dict[str, Any], 
    facts: List[Dict[str, Any]],
    target_words: int = 1200
) -> tuple[str, Dict[str, Any]]:
    """
    Write a book section using provided facts and brief
    
    Args:
        model: LLM model to use
        brief: Section brief with topic, context, etc.
        facts: List of fact packs from RAG
        target_words: Target word count
    
    Returns:
        (markdown_content, metadata)
    """
    
    # Prepare facts for the prompt
    facts_text = ""
    if facts:
        facts_text = "\n\nSUPPORTING FACTS:\n"
        for i, fact in enumerate(facts, 1):
            facts_text += f"\n{i}. {fact['text']}\n   Source: {fact['source']['title']} [@{fact['citeKey']}]\n"
    
    # Create user prompt
    user_prompt = f"""Write a book section with the following specifications:

TOPIC: {brief.get('topic', 'General topic')}
TARGET WORDS: {target_words}
CONTEXT: {brief.get('context', '')}
AUDIENCE: {brief.get('audience', 'General audience')}
TONE: {brief.get('tone', 'Professional')}

{facts_text}

Write a comprehensive, well-structured section that:
- Covers the topic thoroughly
- Uses the provided facts as supporting evidence
- Includes proper citations
- Maintains the specified tone and style
- Ends with a summary and key takeaways

Remember to use [@citeKey] for citations and [[NEEDS_SOURCE]] if you make claims without supporting evidence.

Return ONLY the markdown content, no JSON wrapper, no explanations."""

    try:
        content, metadata = chat(
            model=model,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=2000,
            system=WRITER_SYSTEM
        )
        
        return content, metadata
        
    except Exception as e:
        error_content = f"""# {brief.get('topic', 'Section')}

## Error

There was an error generating this section: {str(e)}

[[NEEDS_SOURCE]] - This section requires manual review and completion.

## Summary

This section could not be automatically generated due to a technical error.

## Key Takeaways

- Manual review required
- Technical error encountered during generation
"""
        return error_content, {"error": str(e), "input_tokens": 0, "output_tokens": 0, "cost": 0}

def write_chapter(
    model: str,
    chapter_brief: Dict[str, Any],
    sections: List[Dict[str, Any]],
    facts: List[Dict[str, Any]] = None
) -> tuple[str, Dict[str, Any]]:
    """
    Write a complete chapter with multiple sections
    
    Args:
        model: LLM model to use
        chapter_brief: Chapter-level information
        sections: List of section briefs
        facts: Optional facts for the entire chapter
    
    Returns:
        (markdown_content, metadata)
    """
    
    chapter_content = f"# {chapter_brief.get('title', 'Chapter')}\n\n"
    
    if chapter_brief.get('introduction'):
        chapter_content += f"{chapter_brief['introduction']}\n\n"
    
    total_metadata = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost": 0,
        "sections_written": 0,
        "errors": []
    }
    
    for i, section in enumerate(sections, 1):
        section_brief = {
            "topic": section.get("title", f"Section {i}"),
            "context": section.get("context", ""),
            "audience": chapter_brief.get("audience", "General audience"),
            "tone": chapter_brief.get("tone", "Professional"),
            "target_words": section.get("target_words", 1200)
        }
        
        # Get section-specific facts if available
        section_facts = facts or []
        if section.get("fact_query"):
            section_facts = fact_pack(section["fact_query"], k=6)
        
        section_content, section_metadata = write_section(
            model=model,
            brief=section_brief,
            facts=section_facts,
            target_words=section_brief["target_words"]
        )
        
        chapter_content += section_content + "\n\n"
        
        # Aggregate metadata
        total_metadata["input_tokens"] += section_metadata.get("input_tokens", 0)
        total_metadata["output_tokens"] += section_metadata.get("output_tokens", 0)
        total_metadata["cost"] += section_metadata.get("cost", 0)
        total_metadata["sections_written"] += 1
        
        if "error" in section_metadata:
            total_metadata["errors"].append(f"Section {i}: {section_metadata['error']}")
    
    return chapter_content, total_metadata
