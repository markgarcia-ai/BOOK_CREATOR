import json
from typing import Dict, List, Any
from .llm import chat  # Use direct chat instead of complete_json
from .settings import WRITER_MODEL
from .prompt_loader import get_writer_prompt
# Conditional RAG import
try:
    from rag.retrieve import fact_pack
except ImportError:
    fact_pack = None

# Get writer system prompt from external file
WRITER_SYSTEM = get_writer_prompt()

def count_words(text: str) -> int:
    """Count words in text, excluding markdown formatting"""
    import re
    # Remove markdown formatting for accurate word count
    clean_text = re.sub(r'[#*`\[\](){}]', '', text)
    clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', clean_text)  # Remove images
    clean_text = re.sub(r'\[.*?\]\(.*?\)', '', clean_text)   # Remove links
    return len(clean_text.split())

def write_section_iterative(
    model: str, 
    brief: Dict[str, Any], 
    facts: List[Dict[str, Any]],
    target_words: int = 1200,
    temp_file_path: str = None
) -> tuple[str, Dict[str, Any]]:
    """
    Write a book section using file-based iterative generation
    
    Args:
        model: LLM model to use
        brief: Section brief with topic, context, etc.
        facts: List of fact packs from RAG
        target_words: Target word count
        temp_file_path: Path to temporary file for iterative building
    
    Returns:
        (markdown_content, metadata)
    """
    import logging
    import tempfile
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    
    # Agent statistics
    agent_stats = {
        "attempts": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cost": 0,
        "target_words": target_words,
        "final_word_count": 0,
        "iterations": []
    }
    
    # Create temp file if not provided
    if temp_file_path is None:
        temp_dir = Path(tempfile.gettempdir()) / "book_creator"
        temp_dir.mkdir(exist_ok=True)
        topic_safe = "".join(c for c in brief.get('topic', 'section') if c.isalnum() or c in (' ', '-', '_'))
        topic_safe = topic_safe.replace(' ', '_').lower()
        temp_file_path = temp_dir / f"{topic_safe}_temp.md"
    else:
        temp_file_path = Path(temp_file_path)
    
    # Prepare facts for the prompt
    facts_text = ""
    if facts:
        facts_text = "\n\nSUPPORTING FACTS:\n"
        for i, fact in enumerate(facts, 1):
            cite_key = fact.get('citeKey', 'source')
            facts_text += f"\n{i}. {fact['text']}\n   Source: {fact['source']['title']} [@{cite_key}]\n"
    
    max_attempts = 5
    tolerance = 0.15  # 15% tolerance
    
    logger.info(f"🎯 Starting file-based iterative generation for '{brief.get('topic', 'Unknown topic')}'")
    logger.info(f"📝 Target: {target_words} words")
    logger.info(f"📁 Temp file: {temp_file_path}")
    
    for attempt in range(max_attempts):
        agent_stats["attempts"] += 1
        
        # Read current content from file (if exists)
        current_content = ""
        if temp_file_path.exists():
            current_content = temp_file_path.read_text(encoding='utf-8')
        
        current_word_count = count_words(current_content)
        words_needed = target_words - current_word_count
        
        logger.info(f"🔄 Attempt {attempt + 1}/{max_attempts}: Current words: {current_word_count}, Need: {words_needed}")
        
        # Check if we've reached the target
        if current_word_count >= target_words * (1 - tolerance):
            logger.info(f"✅ Target reached! Final count: {current_word_count} words")
            break
        
        # Determine prompt based on whether file exists
        if attempt == 0 or not temp_file_path.exists():
            # First attempt: Generate initial content
            user_prompt = f"""Write a comprehensive book section with the following specifications:

TOPIC: {brief.get('topic', 'General topic')}
TARGET WORDS: Start with approximately {min(target_words, 2000)} words for the initial version
CONTEXT: {brief.get('context', '')}
AUDIENCE: {brief.get('audience', 'General audience')}
TONE: {brief.get('tone', 'Professional')}

{facts_text}

Write a well-structured section that covers the topic thoroughly:
- Start with an engaging introduction
- Create multiple detailed subsections
- Include practical examples and use cases
- Add mathematical formulas where relevant (LaTeX: $ for inline, $$ for display)
- Use proper markdown formatting (##, ###, ####)
- Include citations [@citeKey] and figure placeholders {{{{FIG:description:"caption"}}}}
- End with summary and key takeaways

This is the initial version - focus on creating a solid foundation that can be expanded later.

Return ONLY the markdown content."""
        else:
            # Expansion attempt: Add more content to existing
            user_prompt = f"""I have an existing book section that currently has {current_word_count} words, but I need to expand it to approximately {target_words} words (need {words_needed} more words).

CURRENT SECTION CONTENT:
{current_content}

TASK: Add approximately {words_needed} more words to this section by:
- Adding new relevant subsections after the existing content
- Including more detailed examples and explanations
- Adding more mathematical formulas and technical details
- Including additional practical use cases
- Expanding technical concepts with more depth
- Adding more figure placeholders where helpful

IMPORTANT: 
- Keep ALL existing content exactly as is
- Add new content seamlessly after the existing sections
- Do not modify the existing summary/key takeaways - create new ones at the end
- The final result should be approximately {target_words} words total

Return the COMPLETE expanded section (existing + new content)."""
        
        try:
            messages = [
                {"role": "system", "content": WRITER_SYSTEM},
                {"role": "user", "content": user_prompt}
            ]
            
            # Calculate appropriate max_tokens
            if attempt == 0:
                estimated_tokens = min(3000, int(target_words * 1.5) + 500)
            else:
                estimated_tokens = int(words_needed * 1.5) + 1000  # Buffer for existing content
            
            max_tokens = min(estimated_tokens, 8000)
            
            logger.info(f"🤖 Making LLM call with max_tokens: {max_tokens}")
            
            content, metadata = chat(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            
            # Write new content to file immediately
            temp_file_path.write_text(content, encoding='utf-8')
            
            # Update statistics
            agent_stats["total_input_tokens"] += metadata.get("input_tokens", 0)
            agent_stats["total_output_tokens"] += metadata.get("output_tokens", 0)
            agent_stats["total_cost"] += metadata.get("cost", 0)
            
            # Count words in new content
            new_word_count = count_words(content)
            
            iteration_stats = {
                "attempt": attempt + 1,
                "input_tokens": metadata.get("input_tokens", 0),
                "output_tokens": metadata.get("output_tokens", 0),
                "cost": metadata.get("cost", 0),
                "word_count": new_word_count,
                "words_added": new_word_count - current_word_count if attempt > 0 else new_word_count
            }
            agent_stats["iterations"].append(iteration_stats)
            
            logger.info(f"📊 Iteration {attempt + 1}: Generated {new_word_count} words (+{iteration_stats['words_added']}), Cost: ${metadata.get('cost', 0):.4f}")
            logger.info(f"💾 Content written to: {temp_file_path}")
            
        except Exception as e:
            logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                # If first attempt fails, return error
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
                return error_content, {"error": str(e), "agent_stats": agent_stats}
            # If later attempts fail, use current file content
            break
    
    # Read final content from file
    final_content = ""
    if temp_file_path.exists():
        final_content = temp_file_path.read_text(encoding='utf-8')
        # Clean up temp file
        temp_file_path.unlink()
    
    # Final statistics
    agent_stats["final_word_count"] = count_words(final_content)
    completion_percentage = (agent_stats["final_word_count"] / target_words) * 100
    
    logger.info(f"🎉 SECTION COMPLETED: '{brief.get('topic', 'Unknown topic')}'")
    logger.info(f"📊 FINAL STATS:")
    logger.info(f"   🎯 Target: {target_words} words")
    logger.info(f"   ✅ Achieved: {agent_stats['final_word_count']} words ({completion_percentage:.1f}%)")
    logger.info(f"   🔄 Attempts: {agent_stats['attempts']}")
    logger.info(f"   💰 Total Cost: ${agent_stats['total_cost']:.4f}")
    logger.info(f"   🔤 Total Tokens: {agent_stats['total_input_tokens']} in, {agent_stats['total_output_tokens']} out")
    
    # Add agent stats to metadata
    final_metadata = {
        "input_tokens": agent_stats["total_input_tokens"],
        "output_tokens": agent_stats["total_output_tokens"],
        "cost": agent_stats["total_cost"],
        "agent_stats": agent_stats,
        "word_count": agent_stats["final_word_count"],
        "target_completion": completion_percentage
    }
    
    return final_content, final_metadata

def write_section(
    model: str, 
    brief: Dict[str, Any], 
    facts: List[Dict[str, Any]],
    target_words: int = 1200
) -> tuple[str, Dict[str, Any]]:
    """
    Write a book section - uses iterative file-based approach for large targets
    """
    if target_words > 2000:
        return write_section_iterative(model, brief, facts, target_words)
    else:
        # For smaller sections, use the simple approach
        return write_section_simple(model, brief, facts, target_words)

def write_section_simple(
    model: str, 
    brief: Dict[str, Any], 
    facts: List[Dict[str, Any]],
    target_words: int = 1200
) -> tuple[str, Dict[str, Any]]:
    """
    Simple section writing for shorter content
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Prepare facts for the prompt
    facts_text = ""
    if facts:
        facts_text = "\n\nSUPPORTING FACTS:\n"
        for i, fact in enumerate(facts, 1):
            cite_key = fact.get('citeKey', 'source')
            facts_text += f"\n{i}. {fact['text']}\n   Source: {fact['source']['title']} [@{cite_key}]\n"
    
    user_prompt = f"""Write a comprehensive book section with the following specifications:

TOPIC: {brief.get('topic', 'General topic')}
TARGET WORDS: {target_words} words
CONTEXT: {brief.get('context', '')}
AUDIENCE: {brief.get('audience', 'General audience')}
TONE: {brief.get('tone', 'Professional')}

{facts_text}

Write a detailed section that reaches approximately {target_words} words:
- Start with an engaging introduction
- Cover the topic with detailed subsections
- Include practical examples and use cases
- Add mathematical formulas where relevant (LaTeX: $ for inline, $$ for display)
- Use proper markdown formatting (##, ###, ####)
- Include citations [@citeKey] and figure placeholders {{{{FIG:description:"caption"}}}}
- End with comprehensive summary and key takeaways

Return ONLY the markdown content."""

    try:
        messages = [
            {"role": "system", "content": WRITER_SYSTEM},
            {"role": "user", "content": user_prompt}
        ]
        
        estimated_tokens = int(target_words * 1.5) + 500
        max_tokens = min(estimated_tokens, 8000)
        
        content, metadata = chat(
            model=model,
            messages=messages,
            max_tokens=max_tokens
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
