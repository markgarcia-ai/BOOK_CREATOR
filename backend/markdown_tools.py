"""
Markdown file manipulation tools for the writer agent
"""
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re

logger = logging.getLogger(__name__)

def identify_unexpanded_bullets(content: str) -> List[Dict[str, str]]:
    """
    Identify bullet points that lack narrative explanation after them
    """
    unexpanded_bullets = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Find bullet points
        if re.match(r'^\s*[-*]\s*(.+)$', line):
            bullet_text = re.match(r'^\s*[-*]\s*(.+)$', line).group(1).strip()
            
            # Check if the bullet is followed by narrative content
            has_narrative = False
            
            # Look at the next few lines to see if there's explanatory content
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                
                # Stop if we hit another bullet, header, or section
                if (next_line.startswith('-') or next_line.startswith('*') or 
                    next_line.startswith('#') or not next_line):
                    break
                
                # If we find substantial narrative content (not just short phrases)
                if len(next_line.split()) > 10:  # More than 10 words = narrative
                    has_narrative = True
                    break
            
            # If no narrative found, this bullet needs expansion
            if not has_narrative:
                unexpanded_bullets.append({
                    "bullet_text": bullet_text,
                    "line_number": i + 1,
                    "context": lines[max(0, i-2):i+3]  # surrounding context
                })
    
    return unexpanded_bullets

def analyze_content_gaps(content: str) -> Dict[str, List[str]]:
    """
    Analyze content to identify specific improvement opportunities
    """
    gaps = {
        "unexpanded_bullets": [],    # Bullet points lacking narrative explanation
        "missing_examples": [],      # Concepts without concrete examples  
        "missing_math": [],          # Topics needing mathematical formulation
        "missing_code": [],          # Concepts needing implementation
        "weak_transitions": [],     # Sections needing better flow
        "missing_context": [],      # Topics needing broader context
        "placeholder_content": []   # Placeholder text to remove
    }
    
    # Identify bullet points that need narrative expansion
    unexpanded = identify_unexpanded_bullets(content)
    for bullet_info in unexpanded:
        gaps["unexpanded_bullets"].append(bullet_info["bullet_text"])
    
    # Check for placeholder content
    placeholder_patterns = [
        r'\[Existing content remains the same\]',
        r'\[.*?\]',
        r'TODO:',
        r'PLACEHOLDER',
        r'to be expanded',
        r'more details needed'
    ]
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        gaps["placeholder_content"].extend(matches)
    
    # Check for mathematical concepts without formulas
    math_keywords = ['algorithm', 'optimization', 'probability', 'matrix', 'vector', 'function', 'equation']
    has_math_content = any(keyword in content.lower() for keyword in math_keywords)
    has_math_notation = bool(re.search(r'\$.*?\$', content))
    
    if has_math_content and not has_math_notation:
        gaps["missing_math"].append("Add mathematical formulations and worked examples")
    
    # Check for concepts without examples
    example_patterns = [r'example', r'for instance', r'consider', r'suppose', r'let\'s say']
    has_examples = any(re.search(pattern, content, re.IGNORECASE) for pattern in example_patterns)
    
    if not has_examples and len(content.split()) > 100:  # Only for substantial content
        gaps["missing_examples"].append("Add concrete examples and case studies")
    
    # Check for code-related concepts without implementation
    code_keywords = ['implementation', 'algorithm', 'function', 'class', 'method', 'programming']
    has_code_content = any(keyword in content.lower() for keyword in code_keywords)
    has_code_blocks = bool(re.search(r'```.*?```', content, re.DOTALL))
    
    if has_code_content and not has_code_blocks:
        gaps["missing_code"].append("Add implementation examples and code")
    
    # Check for weak section transitions
    sections = re.split(r'\n#{2,4}\s+', content)
    if len(sections) > 2:  # Multiple sections
        for i in range(1, len(sections)):
            # Check if sections start abruptly without context
            section_start = sections[i][:100].strip()
            if not section_start or len(section_start.split()) < 10:
                gaps["weak_transitions"].append(f"Section {i+1} needs better introduction")
    
    return gaps

def assess_content_quality(content: str) -> Dict[str, bool]:
    """
    Assess if content meets educational quality standards
    """
    criteria = {
        "has_clear_definitions": bool(re.search(r'\b\w+ is (a|an|the)\b', content, re.IGNORECASE)),
        "has_worked_examples": bool(re.search(r'example|for instance|consider|suppose', content, re.IGNORECASE)),
        "has_mathematical_rigor": bool(re.search(r'\$.*?\$', content)),
        "has_practical_context": bool(re.search(r'application|use case|practice|industry', content, re.IGNORECASE)),
        "has_smooth_transitions": not bool(re.search(r'\n\s*\n\s*#{2,4}', content)),  # No blank lines before headers
        "no_placeholder_content": not bool(re.search(r'\[.*?\]|TODO|placeholder', content, re.IGNORECASE)),
        "sufficient_depth": len(content.split()) > 200  # Minimum depth threshold
    }
    
    return criteria

def create_targeted_enhancement_prompt(content: str, gaps: Dict[str, List[str]]) -> str:
    """
    Create specific enhancement prompts based on content analysis
    """
    enhancements = []
    
    if gaps["unexpanded_bullets"]:
        enhancements.append(f"""
**GENERATE NARRATIVE EXPLANATIONS**: Create detailed explanatory content for these bullet points:
{chr(10).join(f"- {concept}" for concept in gaps["unexpanded_bullets"][:5])}

For EACH bullet point, generate a comprehensive explanation section that includes:
- Detailed definition and conceptual explanation
- Mathematical formulations with LaTeX notation where relevant  
- Concrete examples with step-by-step worked solutions
- Real-world applications and practical significance
- Connection to broader AI/ML concepts and why it matters

CRITICAL: Generate NEW content to be APPENDED after the existing bullet points, don't replace them.""")
    
    if gaps["missing_math"]:
        enhancements.append("""
**ADD MATHEMATICAL RIGOR**: Include formal mathematical formulations:
- Provide precise mathematical definitions using LaTeX notation
- Include step-by-step worked examples with actual calculations
- Show multiple solution approaches where relevant
- Add geometric or intuitive interpretations""")
    
    if gaps["missing_examples"]:
        enhancements.append("""
**ADD CONCRETE EXAMPLES**: Enhance with specific, worked examples:
- Real-world case studies with actual data and numbers
- Step-by-step problem solutions showing all calculations
- Industry applications demonstrating practical value
- Multiple examples showing different use cases""")
    
    if gaps["missing_code"]:
        enhancements.append("""
**ADD IMPLEMENTATION DETAILS**: Include practical code examples:
- Full implementation with detailed explanations
- Line-by-line code commentary
- Performance considerations and optimizations
- Real-world usage patterns and best practices""")
    
    if gaps["weak_transitions"]:
        enhancements.append("""
**IMPROVE SECTION FLOW**: Add contextual bridges between sections:
- Provide smooth transitions that connect concepts
- Include introductory paragraphs for each major section
- Explain how concepts build upon previous material
- Maintain narrative continuity throughout""")
    
    if gaps["placeholder_content"]:
        enhancements.append(f"""
**REMOVE PLACEHOLDERS**: Replace all placeholder content:
{chr(10).join(f"- Remove: '{placeholder}'" for placeholder in gaps["placeholder_content"][:3])}
Replace with actual substantive content explaining the concepts.""")
    
    return "\n\n".join(enhancements)

def copy_source_to_exports(source_file: Path, export_dir: Path) -> Path:
    """
    Copy the source markdown file to the exports directory
    
    Args:
        source_file: Path to source file in uploads
        export_dir: Export directory for the book
    
    Returns:
        Path to copied file
    """
    logger.info(f"📋 COPY SOURCE: Starting copy process")
    logger.info(f"   📁 Source: {source_file}")
    logger.info(f"   📁 Destination: {export_dir}")
    
    # Create exports directory
    if not export_dir.exists():
        export_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ FOLDER CREATED: {export_dir}")
    else:
        logger.info(f"📁 FOLDER EXISTS: {export_dir}")
    
    # Copy file
    source_content = source_file.read_text(encoding='utf-8')
    source_words = len(source_content.split())
    logger.info(f"📄 SOURCE CONTENT: {len(source_content)} characters, {source_words} words")
    
    copied_file = export_dir / f"source_{source_file.name}"
    copied_file.write_text(source_content, encoding='utf-8')
    
    logger.info(f"✅ FILE CREATED: {copied_file}")
    logger.info(f"   📊 File size: {len(source_content)} characters")
    
    return copied_file

def split_markdown_by_chapters(markdown_file: Path, export_dir: Path) -> List[Dict[str, Any]]:
    """
    Split a markdown file into separate files per chapter
    
    Args:
        markdown_file: Path to the markdown file to split
        export_dir: Directory to save chapter files
    
    Returns:
        List of chapter info dictionaries
    """
    logger.info(f"✂️ SPLIT CHAPTERS: Starting split process")
    logger.info(f"   📁 Source file: {markdown_file}")
    logger.info(f"   📁 Output directory: {export_dir}")
    
    content = markdown_file.read_text(encoding='utf-8')
    content_words = len(content.split())
    logger.info(f"   📊 Source content: {len(content)} characters, {content_words} words")
    
    # Find chapter headers (## followed by chapter title)
    chapter_pattern = r'^## (\d+\.\s*.+)$'
    chapters = []
    
    # Split content by chapters
    chapter_matches = list(re.finditer(chapter_pattern, content, re.MULTILINE))
    logger.info(f"   🔍 Found {len(chapter_matches)} chapter headers")
    
    if not chapter_matches:
        logger.warning("⚠️ SPLIT FAILED: No chapters found in markdown file")
        logger.info(f"   📝 Content preview: {content[:200]}...")
        return []
    
    for i, match in enumerate(chapter_matches):
        chapter_title = match.group(1).strip()
        chapter_start = match.start()
        
        logger.info(f"   📄 Processing chapter {i+1}: '{chapter_title}'")
        
        # Find the end of this chapter (start of next chapter or end of file)
        if i + 1 < len(chapter_matches):
            chapter_end = chapter_matches[i + 1].start()
        else:
            chapter_end = len(content)
        
        # Extract chapter content
        chapter_content = content[chapter_start:chapter_end].strip()
        chapter_words = len(chapter_content.split())
        
        # Create safe filename
        safe_title = "".join(c for c in chapter_title if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title.replace(' ', '_').lower()
        chapter_file = export_dir / f"chapter_{i+1:02d}_{safe_title}.md"
        
        logger.info(f"   📁 Creating chapter file: {chapter_file}")
        
        # Write chapter file
        chapter_file.write_text(chapter_content, encoding='utf-8')
        
        logger.info(f"✅ FILE CREATED: {chapter_file}")
        logger.info(f"   📊 Chapter {i+1} stats: {chapter_words} words, {len(chapter_content)} characters")
        
        chapter_info = {
            "number": i + 1,
            "title": chapter_title,
            "file_path": chapter_file,
            "original_content": chapter_content,
            "word_count": chapter_words,
            "safe_title": safe_title
        }
        chapters.append(chapter_info)
    
    total_chapter_words = sum(ch["word_count"] for ch in chapters)
    logger.info(f"✅ SPLIT COMPLETED: {len(chapters)} chapters created")
    logger.info(f"   📊 Total words distributed: {total_chapter_words} words")
    
    return chapters

def update_markdown_file(file_path: Path, new_content: str) -> bool:
    """
    Update a markdown file with new content
    
    Args:
        file_path: Path to the markdown file
        new_content: New content to write
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get current content for comparison
        old_content = ""
        old_words = 0
        if file_path.exists():
            old_content = file_path.read_text(encoding='utf-8')
            old_words = len(old_content.split())
            
        new_words = len(new_content.split())
        words_added = new_words - old_words
        
        logger.info(f"💾 FILE UPDATE: Starting update process")
        logger.info(f"   📁 File: {file_path}")
        logger.info(f"   📊 Before: {old_words} words")
        logger.info(f"   📊 After: {new_words} words")
        logger.info(f"   📈 Change: +{words_added} words")
        
        file_path.write_text(new_content, encoding='utf-8')
        
        logger.info(f"✅ FILE UPDATED: {file_path}")
        logger.info(f"   📊 Final size: {len(new_content)} characters, {new_words} words")
        
        return True
    except Exception as e:
        logger.error(f"❌ FILE UPDATE FAILED: {file_path}")
        logger.error(f"   🚨 Error: {e}")
        return False

def extend_chapter_content(
    chapter_file: Path, 
    target_words: int, 
    model: str,
    context_facts: List[Dict[str, Any]] = None,
    book_type_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Extend a chapter's content using the writer agent with book type awareness
    
    Args:
        chapter_file: Path to the chapter markdown file
        target_words: Target word count for the chapter
        model: LLM model to use
        context_facts: Optional context facts for generation
        book_type_info: Optional book type information for specialized prompts
    
    Returns:
        Dictionary with results and statistics
    """
    from .llm import chat
    from .book_type_prompts import generate_book_type_system_prompt, generate_book_type_user_prompt
    
    logger.info(f"🔄 ENHANCE CHAPTER: Starting quality-driven enhancement")
    logger.info(f"   📁 Chapter file: {chapter_file}")
    logger.info(f"   🎯 Goal: Comprehensive educational content")
    
    # Log book type information if provided
    if book_type_info:
        logger.info(f"📚 BOOK TYPE ENHANCEMENT: {book_type_info.get('name', 'Unknown')}")
        logger.info(f"   🎯 Target audience: {book_type_info.get('target_audience', 'Unknown')}")
        logger.info(f"   ✍️  Writing style: {book_type_info.get('writing_style', 'Unknown')}")
        logger.info(f"   🔧 Method: Book-type-aware content generation")
    else:
        logger.info(f"   🔧 Method: Generic content enhancement")
    
    # Read current content
    current_content = chapter_file.read_text(encoding='utf-8')
    current_words = len(current_content.split())
    
    logger.info(f"   📊 Current words: {current_words:,}")
    logger.info(f"   🔍 Analyzing content quality and gaps...")
    
    # Analyze content gaps and quality
    gaps = analyze_content_gaps(current_content)
    quality = assess_content_quality(current_content)
    
    # Log identified gaps
    total_gaps = sum(len(gap_list) for gap_list in gaps.values())
    logger.info(f"   📋 Content analysis: {total_gaps} improvement opportunities identified")
    
    for gap_type, gap_items in gaps.items():
        if gap_items:
            logger.info(f"      - {gap_type}: {len(gap_items)} items")
    
    # Check if content meets quality standards
    quality_score = sum(quality.values()) / len(quality)
    logger.info(f"   📊 Quality score: {quality_score:.1%} ({sum(quality.values())}/{len(quality)} criteria met)")
    
    if quality_score >= 0.8 and total_gaps <= 2:  # 80% quality + minimal gaps
        logger.info(f"✅ CHAPTER COMPLETE: High quality content with minimal gaps")
        return {
            "success": True,
            "attempts": 0,
            "final_word_count": current_words,
            "completion_rate": quality_score * 100,
            "cost": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "quality_score": quality_score,
            "gaps_identified": total_gaps
        }
    
    # Prepare context facts
    facts_text = ""
    if context_facts:
        facts_text = "\n\nSUPPORTING FACTS:\n"
        for i, fact in enumerate(context_facts, 1):
            cite_key = fact.get('citeKey', 'source')
            facts_text += f"\n{i}. {fact['text']}\n   Source: {fact['source']['title']} [@{cite_key}]\n"
    
    # Extract chapter title from content
    title_match = re.search(r'^## (.+)$', current_content, re.MULTILINE)
    chapter_title = title_match.group(1) if title_match else "Unknown Chapter"
    
    max_attempts = 3
    total_cost = 0
    total_input_tokens = 0
    total_output_tokens = 0
    
    logger.info(f"🔄 ENHANCEMENT LOOP: Starting quality-driven improvements (max {max_attempts} iterations)")
    
    for attempt in range(max_attempts):
        # Re-analyze content after each iteration
        current_content = chapter_file.read_text(encoding='utf-8')
        current_words = len(current_content.split())
        gaps = analyze_content_gaps(current_content)
        quality = assess_content_quality(current_content)
        
        total_gaps = sum(len(gap_list) for gap_list in gaps.values())
        quality_score = sum(quality.values()) / len(quality)
        
        logger.info(f"🔄 ITERATION {attempt + 1}/{max_attempts}:")
        logger.info(f"   📊 Current: {current_words:,} words")
        logger.info(f"   📈 Quality: {quality_score:.1%} ({sum(quality.values())}/{len(quality)} criteria)")
        logger.info(f"   🔍 Gaps: {total_gaps} improvement opportunities")
        
        if quality_score >= 0.85 and total_gaps <= 1:  # High quality threshold
            logger.info(f"✅ QUALITY THRESHOLD REACHED: Excellent educational content achieved")
            break
        
        if total_gaps == 0:
            logger.info(f"✅ NO GAPS IDENTIFIED: Content appears comprehensive")
            break
        
        # Create targeted enhancement prompt based on specific gaps
        enhancement_instructions = create_targeted_enhancement_prompt(current_content, gaps)
        
        if not enhancement_instructions.strip():
            logger.info(f"   ℹ️ No specific improvements identified - applying general enhancement")
            enhancement_instructions = "Enhance content depth and educational value"
        
        # TARGETED APPROACH: Generate specific content for identified gaps and append
        user_prompt = f"""Generate additional educational content to address specific gaps in this chapter:

CURRENT CHAPTER CONTENT:
{current_content}

SPECIFIC GAPS TO ADDRESS:
{enhancement_instructions}

TASK: Generate new educational content sections to be APPENDED at the end of this chapter.

CONTENT GENERATION REQUIREMENTS:
- Create detailed explanatory sections for the identified gaps
- Include mathematical formulations with LaTeX: $inline$ and $$display$$
- Provide concrete examples with step-by-step solutions
- Add practical applications and real-world context
- Use university-level academic depth

{facts_text}

FORMAT REQUIREMENTS:
- Generate ONLY new content sections (no existing content)
- Start with appropriate subsection headers (### or ####)
- NO chapter title (## Title) - only subsection content
- Use proper markdown formatting
- Ensure content flows well as additions to existing material

Generate comprehensive educational content sections to fill the identified gaps."""

        try:
            # Generate book-type-aware system prompt
            if book_type_info:
                base_system_prompt = """You are a specialized book author generating additional educational content.

TASK: Generate new educational content sections to address specific gaps in existing material.

CONTENT GENERATION RULES:
1. Generate ONLY new educational content sections
2. Create detailed explanatory content for identified gaps  
3. Use appropriate subsection headers (### or ####)
4. NO meta-commentary about the generation process

ABSOLUTELY FORBIDDEN:
- Including any existing content or chapter headers
- Meta-commentary like "Building on the previous...", "To expand on..."
- Shallow explanations or brief definitions
- References to existing content or generation process

Generate substantial new educational content to fill the identified gaps."""
                
                # Add book-type-specific instructions
                book_type_additions = f"""

BOOK TYPE SPECIFICATIONS:
- Book Type: {book_type_info.get('name', 'Generic')}
- Target Audience: {book_type_info.get('target_audience', 'General readers')}
- Writing Style: {book_type_info.get('writing_style', 'Professional')}
- Content Approach: {book_type_info.get('content_approach', 'Balanced')}

CONTENT STYLE FOR THIS BOOK TYPE:
"""
                
                # Add section emphasis
                section_emphasis = book_type_info.get('section_emphasis', [])
                for emphasis in section_emphasis:
                    book_type_additions += f"- {emphasis}\n"
                
                # Add prompt modifiers
                prompt_modifiers = book_type_info.get('prompt_modifiers', {})
                if prompt_modifiers:
                    book_type_additions += "\nSPECIFIC INSTRUCTIONS:\n"
                    for key, instruction in prompt_modifiers.items():
                        book_type_additions += f"- {key.title()}: {instruction}\n"
                
                enhanced_system_prompt = base_system_prompt + book_type_additions
            else:
                # Fallback to generic system prompt
                enhanced_system_prompt = """You are a university textbook author generating additional educational content.

TASK: Generate new educational content sections to address specific gaps in existing material.

CONTENT GENERATION RULES:
1. Generate ONLY new educational content sections
2. Create detailed explanatory content for identified gaps  
3. Use appropriate subsection headers (### or ####)
4. NO meta-commentary about the generation process

CONTENT STYLE:
- University-level depth with comprehensive explanations
- Mathematical formulations with LaTeX: $inline$ and $$display$$
- Concrete examples with step-by-step calculations
- Practical applications and real-world context
- Rich educational content that fills knowledge gaps
- Clear section organization with proper headers

ABSOLUTELY FORBIDDEN:
- Including any existing content or chapter headers
- Meta-commentary like "Building on the previous...", "To expand on..."
- Shallow explanations or brief definitions
- References to existing content or generation process

Generate substantial new educational content to fill the identified gaps."""

            messages = [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Calculate max_tokens based on content complexity
            estimated_tokens = min(max(2000, current_words + 1500), 8000)
            
            logger.info(f"🤖 LLM CALL: Preparing request")
            logger.info(f"   📱 Model: {model}")
            logger.info(f"   🔤 Max tokens: {estimated_tokens:,}")
            logger.info(f"   📏 Prompt length: {len(user_prompt):,} characters")
            
            expanded_content, metadata = chat(
                model=model,
                messages=messages,
                max_tokens=estimated_tokens
            )
            
            # Update statistics
            attempt_cost = metadata.get("cost", 0)
            attempt_input = metadata.get("input_tokens", 0)
            attempt_output = metadata.get("output_tokens", 0)
            
            total_cost += attempt_cost
            total_input_tokens += attempt_input
            total_output_tokens += attempt_output
            
            logger.info(f"✅ LLM RESPONSE:")
            logger.info(f"   💰 Cost: ${attempt_cost:.4f}")
            logger.info(f"   🔤 Tokens: {attempt_input:,} in, {attempt_output:,} out")
            logger.info(f"   📏 Response length: {len(expanded_content):,} characters")
            
            # APPEND new content to existing content
            combined_content = current_content.rstrip() + '\n\n' + expanded_content.strip()
            
            if update_markdown_file(chapter_file, combined_content):
                old_words = current_words
                current_content = combined_content
                current_words = len(current_content.split())
                words_added = current_words - old_words
                
                # Re-analyze quality after update
                updated_gaps = analyze_content_gaps(combined_content)
                updated_quality = assess_content_quality(combined_content)
                updated_total_gaps = sum(len(gap_list) for gap_list in updated_gaps.values())
                updated_quality_score = sum(updated_quality.values()) / len(updated_quality)
                
                logger.info(f"✅ ITERATION {attempt + 1} COMPLETE:")
                logger.info(f"   📊 Words: {old_words:,} → {current_words:,} (+{words_added:,})")
                logger.info(f"   📈 Quality: {updated_quality_score:.1%} (was {quality_score:.1%})")
                logger.info(f"   🔍 Gaps: {updated_total_gaps} (was {total_gaps})")
                logger.info(f"   💰 Cost: ${attempt_cost:.4f}")
                logger.info(f"   🔧 Method: Targeted content addition (gaps → narrative)")
                
                # Log specific improvements made
                for gap_type, old_gaps in gaps.items():
                    new_gaps = updated_gaps.get(gap_type, [])
                    if len(old_gaps) > len(new_gaps):
                        improved = len(old_gaps) - len(new_gaps)
                        logger.info(f"      ✓ Improved {gap_type}: {improved} items addressed")
            else:
                logger.error(f"❌ FILE UPDATE FAILED on iteration {attempt + 1}")
                break
                
        except Exception as e:
            logger.error(f"❌ ATTEMPT {attempt + 1} FAILED:")
            logger.error(f"   🚨 Error: {e}")
            break
    
    # Final quality assessment
    final_content = chapter_file.read_text(encoding='utf-8')
    final_words = len(final_content.split())
    final_gaps = analyze_content_gaps(final_content)
    final_quality = assess_content_quality(final_content)
    final_total_gaps = sum(len(gap_list) for gap_list in final_gaps.values())
    final_quality_score = sum(final_quality.values()) / len(final_quality)
    
    logger.info(f"🎉 CHAPTER ENHANCEMENT COMPLETED:")
    logger.info(f"   📁 Chapter: {chapter_file.name}")
    logger.info(f"   📊 Final words: {final_words:,}")
    logger.info(f"   📈 Quality score: {final_quality_score:.1%} ({sum(final_quality.values())}/{len(final_quality)} criteria)")
    logger.info(f"   🔍 Remaining gaps: {final_total_gaps}")
    logger.info(f"   🔄 Iterations used: {attempt + 1}/{max_attempts}")
    logger.info(f"   💰 Total cost: ${total_cost:.4f}")
    logger.info(f"   🔤 Total tokens: {total_input_tokens:,} in, {total_output_tokens:,} out")
    
    # Log quality criteria details
    logger.info(f"   📋 Quality breakdown:")
    for criterion, met in final_quality.items():
        status = "✓" if met else "✗"
        logger.info(f"      {status} {criterion}")
    
    return {
        "success": True,
        "attempts": attempt + 1,
        "final_word_count": final_words,
        "target_words": target_words,
        "completion_rate": final_quality_score * 100,  # Quality-based completion
        "quality_score": final_quality_score,
        "gaps_remaining": final_total_gaps,
        "quality_criteria": final_quality,
        "cost": total_cost,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens
    }

def generate_chapter_introduction(chapter_file: Path, model: str = "claude-3-5-haiku-20241022") -> str:
    """
    Generate an introduction for a chapter by analyzing its content
    """
    from .llm import chat
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📝 GENERATING INTRODUCTION: {chapter_file.name}")
    
    # Read the chapter content
    chapter_content = chapter_file.read_text(encoding='utf-8')
    chapter_words = len(chapter_content.split())
    
    logger.info(f"   📊 Chapter content: {chapter_words:,} words")
    
    # Extract chapter title
    title_match = re.search(r'^## (.+)$', chapter_content, re.MULTILINE)
    chapter_title = title_match.group(1) if title_match else "Chapter"
    
    system_prompt = """You are a university textbook author writing chapter introductions.

TASK: Write ONLY the introduction paragraph content - no meta-commentary.

CRITICAL RULES:
- Generate ONLY the introduction paragraph text
- NO meta-commentary like "Here's an introduction..." or "This chapter..."
- Start immediately with the educational content
- Write 3-4 sentences explaining the importance of the concepts
- Use university-level academic tone

CONTENT REQUIREMENTS:
- Explain why the chapter's concepts are important in AI/ML
- Connect to broader applications and significance
- Use engaging, educational language
- NO bullet points or lists - flowing narrative only

ABSOLUTELY FORBIDDEN:
- Meta-commentary about writing introductions
- References like "Here's..." or "This chapter will..."
- Questions to the reader
- Preambles or explanations about the task

Generate ONLY the introduction paragraph content."""

    user_prompt = f"""Create an introduction paragraph for this chapter:

CHAPTER TITLE: {chapter_title}

CHAPTER CONTENT SUMMARY:
{chapter_content[:2000]}...

Generate a 3-4 sentence introduction paragraph that explains the importance and applications of the concepts covered in this chapter."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        logger.info(f"🤖 Generating introduction for '{chapter_title}'")
        
        introduction, metadata = chat(
            model=model,
            messages=messages,
            max_tokens=500
        )
        
        cost = metadata.get('cost', 0)
        input_tokens = metadata.get('input_tokens', 0)
        output_tokens = metadata.get('output_tokens', 0)
        
        logger.info(f"✅ INTRODUCTION GENERATED:")
        logger.info(f"   📏 Length: {len(introduction)} characters")
        logger.info(f"   💰 Cost: ${cost:.4f}")
        logger.info(f"   🔤 Tokens: {input_tokens:,} in, {output_tokens:,} out")
        
        return introduction.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to generate introduction for {chapter_title}: {e}")
        return f"This chapter explores the fundamental concepts of {chapter_title.lower()}, providing essential knowledge for understanding modern AI and machine learning applications."

def restructure_chapter_with_introduction(chapter_file: Path, model: str = "claude-3-5-haiku-20241022") -> Dict[str, Any]:
    """
    Add introduction to chapter using manual insertion approach
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📝 ADDING INTRODUCTION: {chapter_file.name}")
    
    # Read current chapter content
    current_content = chapter_file.read_text(encoding='utf-8')
    current_words = len(current_content.split())
    
    logger.info(f"   📊 Current content: {current_words:,} words")
    
    # Extract chapter title
    title_match = re.search(r'^## (.+)$', current_content, re.MULTILINE)
    chapter_title = title_match.group(1) if title_match else "Chapter"
    
    # Generate ONLY the introduction paragraph
    introduction = generate_chapter_introduction(chapter_file, model)
    
    # Manually insert the introduction after the title
    lines = current_content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # If this is the chapter title line, add introduction after it
        if line.strip().startswith('## ') and chapter_title in line:
            new_lines.append('')  # Empty line
            new_lines.append(introduction)  # Introduction paragraph
            new_lines.append('')  # Empty line
    
    # Combine back into content
    new_content = '\n'.join(new_lines)
    
    # Update the file
    if update_markdown_file(chapter_file, new_content):
        new_words = len(new_content.split())
        words_added = new_words - current_words
        
        logger.info(f"✅ INTRODUCTION ADDED:")
        logger.info(f"   📊 Words: {current_words:,} → {new_words:,} (+{words_added:,})")
        logger.info(f"   📏 Introduction: {len(introduction)} characters")
        
        return {
            "success": True,
            "words_added": words_added,
            "cost": 0.01,  # Approximate cost for introduction generation (10x increase)
            "input_tokens": 500,
            "output_tokens": 100
        }
    else:
        logger.error(f"❌ Failed to update file {chapter_file.name}")
        return {"success": False, "words_added": 0, "cost": 0}

def restructure_chapter_with_introduction_OLD(chapter_file: Path, model: str = "claude-3-5-haiku-20241022") -> Dict[str, Any]:
    """
    Complete chapter restructuring agent that adds introduction and organizes content
    """
    from .llm import chat
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔧 RESTRUCTURING CHAPTER: {chapter_file.name}")
    
    # Read current chapter content
    current_content = chapter_file.read_text(encoding='utf-8')
    current_words = len(current_content.split())
    
    logger.info(f"   📊 Current content: {current_words:,} words")
    
    # Extract chapter title
    title_match = re.search(r'^## (.+)$', current_content, re.MULTILINE)
    chapter_title = title_match.group(1) if title_match else "Chapter"
    
    system_prompt = """You are a university textbook editor. Your ONLY task is to add a brief introduction paragraph.

CRITICAL INSTRUCTIONS:
1. PRESERVE ALL EXISTING CONTENT EXACTLY - every word, bullet point, formula, and section
2. ADD ONLY a 3-4 sentence introduction paragraph immediately after the chapter title
3. DO NOT reorganize, summarize, or modify any existing content
4. DO NOT change header levels (keep ## for main chapter title)
5. DO NOT add meta-commentary or explanations about what you're doing

INTRODUCTION REQUIREMENTS:
- Write 3-4 sentences explaining the importance of the chapter's concepts
- Connect to broader AI/ML applications  
- Use engaging, university-level academic tone
- Place immediately after the chapter title with proper spacing

ABSOLUTELY FORBIDDEN:
- Changing ANY existing content
- Reorganizing sections
- Modifying bullet points or formulas
- Adding meta-commentary like "Here's the restructured..."
- Changing header levels or structure
- Summarizing or condensing existing material

TASK: Add ONLY an introduction paragraph while preserving everything else exactly."""

    user_prompt = f"""Add ONLY an introduction paragraph to this chapter. Preserve ALL existing content exactly.

CURRENT CHAPTER:
{current_content}

TASK: Add a 3-4 sentence introduction paragraph immediately after the chapter title "## {chapter_title}".

REQUIREMENTS:
- Keep ALL existing content exactly as written
- Add introduction paragraph after the title with proper spacing
- NO other changes to content, organization, or formatting
- Start output immediately with the chapter title

Return the complete chapter with introduction added."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        logger.info(f"🤖 Restructuring '{chapter_title}'")
        
        restructured_content, metadata = chat(
            model=model,
            messages=messages,
            max_tokens=8000  # Larger token limit for full chapter restructuring
        )
        
        cost = metadata.get('cost', 0)
        input_tokens = metadata.get('input_tokens', 0)
        output_tokens = metadata.get('output_tokens', 0)
        
        # Update the file with restructured content
        if update_markdown_file(chapter_file, restructured_content):
            new_words = len(restructured_content.split())
            words_added = new_words - current_words
            
            logger.info(f"✅ CHAPTER RESTRUCTURED:")
            logger.info(f"   📊 Words: {current_words:,} → {new_words:,} (+{words_added:,})")
            logger.info(f"   💰 Cost: ${cost:.4f}")
            logger.info(f"   🔤 Tokens: {input_tokens:,} in, {output_tokens:,} out")
            
            return {
                "success": True,
                "words_added": words_added,
                "cost": cost,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
        else:
            logger.error(f"❌ Failed to update file {chapter_file.name}")
            return {"success": False, "words_added": 0, "cost": cost}
        
    except Exception as e:
        logger.error(f"❌ Failed to restructure chapter {chapter_title}: {e}")
        return {"success": False, "words_added": 0, "cost": 0}

def add_introduction_to_chapter(chapter_file: Path, model: str = "claude-3-5-haiku-20241022") -> Dict[str, Any]:
    """
    Add an introduction to a chapter file
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📝 ADDING INTRODUCTION: {chapter_file.name}")
    
    # Generate the introduction
    introduction = generate_chapter_introduction(chapter_file, model)
    
    # Read current chapter content
    current_content = chapter_file.read_text(encoding='utf-8')
    
    # Extract title and rest of content
    lines = current_content.split('\n')
    title_line = None
    content_start_idx = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith('## '):
            title_line = line
            content_start_idx = i + 1
            break
    
    if title_line:
        # Build new content with introduction
        new_lines = [title_line, '', introduction, '']
        
        # Add the rest of the content
        for i in range(content_start_idx, len(lines)):
            if lines[i].strip():  # Skip empty lines right after title
                new_lines.extend(lines[i:])
                break
        
        new_content = '\n'.join(new_lines)
        
        # Update the file
        if update_markdown_file(chapter_file, new_content):
            new_words = len(new_content.split())
            old_words = len(current_content.split())
            words_added = new_words - old_words
            
            logger.info(f"✅ INTRODUCTION ADDED:")
            logger.info(f"   📊 Words: {old_words:,} → {new_words:,} (+{words_added:,})")
            logger.info(f"   📏 Introduction: {len(introduction)} characters")
            
            return {
                "success": True,
                "words_added": words_added,
                "introduction_length": len(introduction)
            }
    
    logger.error(f"❌ Failed to add introduction to {chapter_file.name}")
    return {"success": False, "words_added": 0, "introduction_length": 0}

def compile_chapters_to_book(chapters: List[Dict[str, Any]], book_dir: Path, book_title: str) -> Path:
    """
    Compile all chapter files into a single book
    
    Args:
        chapters: List of chapter info dictionaries
        book_dir: Directory containing the book
        book_title: Title of the book
    
    Returns:
        Path to the compiled book file
    """
    logger.info(f"📚 COMPILE BOOK: Starting compilation process")
    logger.info(f"   📖 Title: {book_title}")
    logger.info(f"   📄 Chapters to compile: {len(chapters)}")
    logger.info(f"   📁 Output directory: {book_dir}")
    
    # Create book content
    book_content = f"# {book_title}\n\n"
    
    total_words = 0
    total_characters = 0
    
    for i, chapter in enumerate(chapters, 1):
        logger.info(f"   📄 Processing chapter {i}: {chapter['title']}")
        
        chapter_content = chapter["file_path"].read_text(encoding='utf-8')
        chapter_words = len(chapter_content.split())
        chapter_chars = len(chapter_content)
        
        logger.info(f"      📊 Chapter stats: {chapter_words:,} words, {chapter_chars:,} characters")
        
        book_content += f"{chapter_content}\n\n---\n\n"
        
        # Update chapter word count
        chapter["final_word_count"] = chapter_words
        total_words += chapter_words
        total_characters += chapter_chars
    
    # Save compiled book
    safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_'))
    safe_title = safe_title.replace(' ', '_').lower()
    book_file = book_dir / f"{safe_title}_complete.md"
    
    logger.info(f"   📁 Creating final book file: {book_file}")
    book_file.write_text(book_content, encoding='utf-8')
    
    final_book_words = len(book_content.split())
    final_book_chars = len(book_content)
    
    logger.info(f"✅ BOOK COMPILED: {book_file}")
    logger.info(f"   📊 Final stats: {final_book_words:,} words, {final_book_chars:,} characters")
    logger.info(f"   📄 Estimated pages: {final_book_words / 250:.1f}")
    
    return book_file

def calculate_book_statistics(chapters: List[Dict[str, Any]], total_cost: float) -> Dict[str, Any]:
    """
    Calculate comprehensive book statistics
    
    Args:
        chapters: List of chapter info dictionaries with final statistics
        total_cost: Total cost of generation
    
    Returns:
        Dictionary with comprehensive statistics
    """
    total_words = sum(chapter.get("final_word_count", 0) for chapter in chapters)
    total_target_words = sum(chapter.get("target_words", 0) for chapter in chapters)
    total_attempts = sum(chapter.get("attempts", 0) for chapter in chapters)
    
    # Estimate pages (assuming 250 words per page)
    estimated_pages = total_words / 250
    
    statistics = {
        "total_chapters": len(chapters),
        "total_words": total_words,
        "total_target_words": total_target_words,
        "estimated_pages": round(estimated_pages, 1),
        "total_cost": total_cost,
        "total_attempts": total_attempts,
        "overall_completion_rate": (total_words / total_target_words * 100) if total_target_words > 0 else 0,
        "chapters": []
    }
    
    for chapter in chapters:
        chapter_stats = {
            "number": chapter["number"],
            "title": chapter["title"],
            "original_words": chapter.get("word_count", 0),
            "final_words": chapter.get("final_word_count", 0),
            "target_words": chapter.get("target_words", 0),
            "estimated_pages": round(chapter.get("final_word_count", 0) / 250, 1),
            "completion_rate": (chapter.get("final_word_count", 0) / chapter.get("target_words", 1) * 100) if chapter.get("target_words", 0) > 0 else 0,
            "attempts": chapter.get("attempts", 0),
            "cost": chapter.get("cost", 0)
        }
        statistics["chapters"].append(chapter_stats)
    
    return statistics
