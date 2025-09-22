import json
from typing import Dict, List, Any, Optional
from .llm import complete_json
from .settings import PLANNER_MODEL
from .prompt_loader import get_planner_prompt

# Get planner system prompt from external file
PLANNER_SYSTEM = get_planner_prompt()

PLANNER_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "audience": {"type": "string"},
        "tone": {"type": "string"},
        "total_target_words": {"type": "integer"},
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "title": {"type": "string"},
                    "target_words": {"type": "integer"},
                    "description": {"type": "string"},
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "slug": {"type": "string"},
                                "title": {"type": "string"},
                                "target_words": {"type": "integer"},
                                "description": {"type": "string"}
                            },
                            "required": ["slug", "title", "target_words", "description"]
                        }
                    },
                    "images": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "slug": {"type": "string"},
                                "prompt": {"type": "string"},
                                "caption": {"type": "string"},
                                "alt": {"type": "string"}
                            },
                            "required": ["slug", "prompt", "caption", "alt"]
                        }
                    }
                },
                "required": ["slug", "title", "target_words", "description", "sections", "images"]
            }
        }
    },
    "required": ["title", "description", "audience", "tone", "total_target_words", "chapters"]
}

def generate_outline(
    model: str,
    topic: str,
    chapters: int = 10,
    words_per_chapter: int = 3500,
    audience: str = "General audience",
    tone: str = "Professional and accessible",
    rag_content_summary: Optional[str] = None
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Generate a complete book outline with optional RAG content awareness
    
    Args:
        model: LLM model to use
        topic: Main book topic
        chapters: Number of chapters
        words_per_chapter: Target words per chapter
        audience: Target audience
        tone: Writing tone
        rag_content_summary: Optional RAG content summary for informed planning
    
    Returns:
        (outline_dict, metadata)
    """
    
    # Base user prompt
    user_prompt = f"""Create a comprehensive book outline for the following specifications:

TOPIC: {topic}
NUMBER OF CHAPTERS: {chapters}
WORDS PER CHAPTER: {words_per_chapter}
TARGET AUDIENCE: {audience}
TONE: {tone}

REQUIREMENTS:
1. Create {chapters} well-structured chapters
2. Each chapter should have 3-5 sections
3. Include 1-2 images per chapter
4. Ensure logical progression from basic to advanced concepts
5. Make slugs descriptive and URL-friendly
6. Set realistic word count targets
7. Include engaging chapter and section titles
8. Plan relevant images that support the content

The book should be comprehensive yet accessible, with clear learning objectives and practical applications."""

    # Add RAG content awareness if available
    if rag_content_summary:
        user_prompt += f"""

RAG CONTENT SUMMARY (Use this to inform your outline):
{rag_content_summary}

IMPORTANT: Use the RAG content summary above to:
- Focus on topics that are well-covered in the available content
- Structure chapters around the main themes identified in the content
- Ensure the outline aligns with what content is actually available
- Plan chapters that can be well-supported by the existing RAG content
- Note any content gaps that should be addressed or avoided"""

    try:
        result, metadata = complete_json(
            model=model,
            system=PLANNER_SYSTEM,
            user=user_prompt,
            schema_hint=json.dumps(PLANNER_SCHEMA, indent=2)
        )
        
        return result, metadata
        
    except Exception as e:
        # Return a basic fallback outline
        fallback_outline = {
            "title": f"Guide to {topic}",
            "description": f"A comprehensive guide to {topic}",
            "audience": audience,
            "tone": tone,
            "total_target_words": chapters * words_per_chapter,
            "chapters": []
        }
        
        for i in range(chapters):
            chapter = {
                "slug": f"chapter-{i+1:02d}",
                "title": f"Chapter {i+1}: {topic} Fundamentals",
                "target_words": words_per_chapter,
                "description": f"Introduction to {topic} concepts",
                "sections": [
                    {
                        "slug": f"intro-{i+1}",
                        "title": "Introduction",
                        "target_words": words_per_chapter // 4,
                        "description": "Chapter introduction"
                    },
                    {
                        "slug": f"main-{i+1}",
                        "title": "Main Content",
                        "target_words": words_per_chapter // 2,
                        "description": "Core chapter content"
                    },
                    {
                        "slug": f"summary-{i+1}",
                        "title": "Summary",
                        "target_words": words_per_chapter // 4,
                        "description": "Chapter summary and key takeaways"
                    }
                ],
                "images": [
                    {
                        "slug": f"chapter-{i+1}-diagram",
                        "prompt": f"Diagram illustrating {topic} concepts",
                        "caption": f"Visual representation of {topic} concepts",
                        "alt": f"Chapter {i+1} diagram"
                    }
                ]
            }
            fallback_outline["chapters"].append(chapter)
        
        return fallback_outline, {"error": str(e), "input_tokens": 0, "output_tokens": 0, "cost": 0}

def generate_rag_aware_outline(
    model: str,
    topic: str,
    rag_content_summary: str,
    chapters: int = 10,
    words_per_chapter: int = 3500,
    audience: str = "General audience",
    tone: str = "Professional and accessible"
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Generate a book outline specifically informed by RAG content analysis
    
    Args:
        model: LLM model to use
        topic: Main book topic
        rag_content_summary: RAG content summary from analysis
        chapters: Number of chapters
        words_per_chapter: Target words per chapter
        audience: Target audience
        tone: Writing tone
    
    Returns:
        (outline_dict, metadata)
    """
    
    user_prompt = f"""Create a comprehensive book outline based on the available RAG content:

TOPIC: {topic}
NUMBER OF CHAPTERS: {chapters}
WORDS PER CHAPTER: {words_per_chapter}
TARGET AUDIENCE: {audience}
TONE: {tone}

RAG CONTENT ANALYSIS:
{rag_content_summary}

CRITICAL REQUIREMENTS:
1. Structure the book around the content that is actually available in the RAG system
2. Focus on topics that are well-covered in the source material
3. Create chapters that can be fully supported by the existing content
4. Identify and plan around any content gaps
5. Ensure each chapter has sufficient source material to write comprehensively
6. Plan practical examples and applications based on available content
7. Structure the learning progression based on the content depth available

The outline should be realistic and achievable given the available source material."""

    try:
        result, metadata = complete_json(
            model=model,
            system=PLANNER_SYSTEM,
            user=user_prompt,
            schema_hint=json.dumps(PLANNER_SCHEMA, indent=2)
        )
        
        return result, metadata
        
    except Exception as e:
        # Fallback to regular outline generation
        return generate_outline(model, topic, chapters, words_per_chapter, audience, tone)

def validate_outline(outline: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an outline for completeness and consistency"""
    issues = []
    warnings = []
    
    # Check required fields
    required_fields = ["title", "description", "audience", "tone", "chapters"]
    for field in required_fields:
        if field not in outline:
            issues.append(f"Missing required field: {field}")
    
    if "chapters" in outline:
        chapter_slugs = set()
        for i, chapter in enumerate(outline["chapters"]):
            # Check chapter structure
            if "slug" not in chapter:
                issues.append(f"Chapter {i+1}: Missing slug")
            elif chapter["slug"] in chapter_slugs:
                issues.append(f"Chapter {i+1}: Duplicate slug '{chapter['slug']}'")
            else:
                chapter_slugs.add(chapter["slug"])
            
            if "sections" not in chapter or not chapter["sections"]:
                warnings.append(f"Chapter {i+1}: No sections defined")
            else:
                section_slugs = set()
                for j, section in enumerate(chapter["sections"]):
                    if "slug" not in section:
                        issues.append(f"Chapter {i+1}, Section {j+1}: Missing slug")
                    elif section["slug"] in section_slugs:
                        issues.append(f"Chapter {i+1}, Section {j+1}: Duplicate slug '{section['slug']}'")
                    else:
                        section_slugs.add(section["slug"])
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "chapter_count": len(outline.get("chapters", [])),
        "total_sections": sum(len(ch.get("sections", [])) for ch in outline.get("chapters", []))
    }

