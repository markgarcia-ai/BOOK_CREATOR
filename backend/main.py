import os, json, subprocess, shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .reasonning_agent import run_agent, run_simple_workflow
from .planner import generate_outline
from .writer import write_chapter  # Keep for legacy compatibility if needed
from .llm import complete_json
from . import tools as T
from .settings import WRITER_MODEL, PLANNER_MODEL
from .book_styles import get_style, list_styles, create_custom_style, BOOK_STYLES
from .book_types import BOOK_TYPES, calculate_cost_estimate
from .html_processor import HTMLProcessor, create_temp_extraction_dir, cleanup_temp_dir
from .config import Config
import logging

# Configure logging based on config
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Conditionally import RAG modules if enabled
if Config.RAG_ENABLED:
    try:
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from rag.retrieve import fact_pack, get_collection_stats
        from rag.ingest import ingest_file, ingest_directory, clear_collection
        from rag.pdf_processor import DocumentProcessor
        logger.info("✅ RAG modules loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠️ RAG modules not available: {e}")
        Config.RAG_ENABLED = False

# Create FastAPI app with dynamic title
app_title = "Book Creator API"
if Config.RAG_ENABLED:
    app_title += " with RAG"

app = FastAPI(title=app_title, version="4.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup
ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / Config.BOOK_DIR
EXPORTS_DIR = ROOT / Config.EXPORTS_DIR
UPLOADS_DIR = ROOT / Config.UPLOADS_DIR

# Ensure directories exist
BOOK_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# RAG directories (only if RAG is enabled)
if Config.RAG_ENABLED:
    RAG_DIR = ROOT / "rag"
    RAG_DB_DIR = RAG_DIR / "db"
    RAG_DB_DIR.mkdir(parents=True, exist_ok=True)

# Pydantic models
class GenerateReq(BaseModel):
    title: str
    chapters: List[str]

class OutlineReq(BaseModel):
    topic: str
    target_audience: str = "General audience"
    style: str = "informative"
    target_pages: int = 10

class BookGenerationRequest(BaseModel):
    title: str
    target_audience: str = "General audience"
    style: str = "informative"
    target_pages: int = 10
    chapters: int = 8
    book_style: str = "modern"
    font_family: Optional[str] = None
    line_height: Optional[str] = None
    paragraph_spacing: Optional[str] = None
    header_spacing: Optional[str] = None
    max_width: Optional[str] = None
    color_scheme: Optional[str] = None
    use_rag: bool = False
    rag_query: Optional[str] = None

class AgentReq(BaseModel):
    goal: str
    max_steps: int = 8
    model: str = WRITER_MODEL

class SimpleWorkflowReq(BaseModel):
    topic: str
    chapters: int = Config.DEFAULT_TARGET_PAGES
    words_per_chapter: int = Config.DEFAULT_WORDS_PER_CHAPTER
    source_content: Optional[str] = None
    book_type: Optional[str] = None
    book_type_info: Optional[Dict[str, Any]] = None

# Health endpoint with configuration info
@app.get("/health")
def health_check():
    """Health check with configuration status"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "features": {
            "rag_enabled": Config.RAG_ENABLED,
            "enhanced_logging": Config.ENHANCED_LOGGING,
            "pdf_generation": Config.PDF_GENERATION
        },
        "config": Config.to_dict()
    }

# Configuration endpoint
@app.get("/config")
def get_config():
    """Get current configuration"""
    return Config.to_dict()

@app.get("/book-types")
def get_book_types():
    """Get available book types with specifications and cost estimates"""
    logger.info("📚 Fetching book types")
    
    # Convert book types to dict format for API response
    book_types_response = {}
    for key, book_type in BOOK_TYPES.items():
        book_types_response[key] = {
            "name": book_type.name,
            "description": book_type.description,
            "recommended_chapters": book_type.recommended_chapters,
            "words_per_chapter": book_type.words_per_chapter,
            "estimated_pages": book_type.estimated_pages,
            "target_audience": book_type.target_audience,
            "complexity_level": book_type.complexity_level,
            "estimated_cost_usd": book_type.estimated_cost_usd,
            "estimated_time_minutes": book_type.estimated_time_minutes,
            "estimated_time_formatted": book_type.estimated_time_formatted,
            "total_words": book_type.total_words,
            "total_tokens": book_type.total_tokens,
            "use_cases": book_type.use_cases
        }
    
    logger.info(f"✅ Returning {len(book_types_response)} book types")
    
    from datetime import datetime
    return {
        "book_types": book_types_response,
        "timestamp": datetime.now().isoformat()
    }

# Core book generation endpoints
@app.post("/generate-outline")
def generate_outline_endpoint(req: OutlineReq):
    """Generate book outline"""
    try:
        logger.info(f"📋 Generating outline for: {req.topic}")
        
        # Create a simple direct outline without complex agent system
        simple_outline = {
            "title": req.topic,
            "description": f"A comprehensive guide to {req.topic}",
            "audience": req.target_audience,
            "style": req.style,
            "chapters": []
        }
        
        # Generate chapter titles based on the topic
        for i in range(1, 6):  # 5 chapters for simplicity
            chapter = {
                "number": i,
                "title": f"{req.topic} - Chapter {i}",
                "description": f"Chapter {i} covering key aspects of {req.topic}",
                "target_words": req.target_pages * 200 // 5
            }
            simple_outline["chapters"].append(chapter)
        
        logger.info(f"✅ Simple outline created with {len(simple_outline['chapters'])} chapters")
        return {"success": True, "outline": simple_outline}
        
    except Exception as e:
        logger.error(f"❌ Outline generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
def generate_book_endpoint(req: GenerateReq):
    """Generate book chapters"""
    try:
        logger.info(f"📚 Generating book: {req.title}")
        results = []
        for i, chapter_title in enumerate(req.chapters, 1):
            try:
                chapter_brief = {"topic": chapter_title, "chapter_number": i, "target_words": 1000}
                chapter_content, chapter_metadata = write_section(
                    model=WRITER_MODEL,
                    brief=chapter_brief, 
                    facts=[],
                    target_words=1000
                )
                results.append({"chapter": i, "title": chapter_title, "content": chapter_content})
            except Exception as e:
                logger.error(f"❌ Chapter {i} failed: {e}")
                results.append({"chapter": i, "title": chapter_title, "error": str(e)})
        
        return {"success": True, "chapters": results}
    except Exception as e:
        logger.error(f"❌ Book generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-book")
def generate_complete_book(req: BookGenerationRequest):
    """Generate complete book with optional RAG enhancement"""
    try:
        logger.info(f"📚 Starting book generation: {req.title}")
        
        # Step 1: Generate outline
        logger.info("📋 STEP 1: Generating outline...")
        outline_data, outline_metadata = generate_outline(
            model=PLANNER_MODEL,
            topic=req.title,
            chapters=req.chapters,
            words_per_chapter=req.target_pages * 200,  # Approximate words per page
            audience=req.target_audience,
            tone=req.style
        )
        
        chapters = outline_data.get("chapters", [])
        
        # Step 2: Generate chapters
        logger.info(f"📝 STEP 2: Writing {len(chapters)} chapters...")
        total_cost = 0
        successful_chapters = 0
        failed_chapters = 0
        chapter_contents = []
        
        for i, chapter in enumerate(chapters, 1):
            try:
                chapter_title = chapter.get("title", f"Chapter {i}")
                logger.info(f"📝 Writing Chapter {i}/{len(chapters)}: {chapter_title}")
                
                # Use RAG if enabled and requested
                rag_context = []
                if Config.RAG_ENABLED and req.use_rag:
                    try:
                        query = req.rag_query or f"{req.title} {chapter_title}"
                        rag_context = fact_pack(query, k=Config.RAG_TOP_K)
                        logger.info(f"🔍 Retrieved {len(rag_context)} relevant documents for chapter {i}")
                    except Exception as e:
                        logger.warning(f"⚠️ RAG retrieval failed for chapter {i}: {e}")
                
                # Generate chapter content using write_section for simplicity
                chapter_brief = {
                    "topic": chapter_title,
                    "chapter_number": i,
                    "target_words": req.target_pages * 200 // req.chapters
                }
                
                # Use write_section which has a simpler interface
                chapter_content, chapter_metadata = write_section(
                    model=WRITER_MODEL,
                    brief=chapter_brief,
                    facts=rag_context if rag_context else [],
                    target_words=req.target_pages * 200 // req.chapters
                )
                
                chapter_result = {
                    "content": chapter_content,
                    "cost": chapter_metadata.get("cost", 0),
                    "tokens": {
                        "input": chapter_metadata.get("input_tokens", 0),
                        "output": chapter_metadata.get("output_tokens", 0)
                    }
                }
                
                chapter_contents.append({
                    "number": i,
                    "title": chapter_title,
                    "content": chapter_result.get("content", ""),
                    "cost": chapter_result.get("cost", 0),
                    "tokens": chapter_result.get("tokens", 0)
                })
                
                successful_chapters += 1
                total_cost += chapter_result.get("cost", 0)
                
                logger.info(f"✅ Chapter {i} completed!")
                logger.info(f"💰 Cost: ${chapter_result.get('cost', 0):.4f}")
                logger.info(f"🔤 Tokens: {chapter_result.get('tokens', {}).get('input', 0)} input, {chapter_result.get('tokens', {}).get('output', 0)} output")
                logger.info(f"📄 Content length: {len(chapter_result.get('content', ''))} characters")
                
            except Exception as e:
                logger.error(f"❌ Chapter {i} failed: {e}")
                failed_chapters += 1
                chapter_contents.append({
                    "number": i,
                    "title": chapter_title,
                    "content": f"# {chapter_title}\n\nThis chapter could not be generated due to an error: {str(e)}",
                    "error": str(e)
                })
        
        # Step 3: Assemble complete book
        logger.info("\n📚 STEP 3: Assembling complete book...")
        book_content = f"# {req.title}\n\n"
        
        for chapter in chapter_contents:
            book_content += f"{chapter['content']}\n\n---\n\n"
        
        # Step 4: Save book
        logger.info("💾 Saving book to file...")
        from datetime import datetime
        
        safe_title = "".join(c for c in req.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()
        
        # Add timestamp to avoid duplicates
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_timestamp = f"{safe_title}_{timestamp}"
        
        book_path = EXPORTS_DIR / f"{filename_with_timestamp}.md"
        book_path.write_text(book_content, encoding='utf-8')
        logger.info(f"✅ Book saved: {book_path} ({len(book_content.encode('utf-8'))} bytes)")
        
        # Step 5: Create simple HTML version
        logger.info("\n🌐 STEP 5: Creating HTML version...")
        html_path = book_path.with_suffix('.html')
        
        # Simple HTML conversion (basic for now)
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{req.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; }}
        p {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <pre style="white-space: pre-wrap; font-family: inherit;">{book_content}</pre>
</body>
</html>"""
        
        html_path.write_text(html_content, encoding='utf-8')
        logger.info(f"✅ HTML book created: {html_path}")
        
        # Step 6: Skip PDF for now (simplified)
        pdf_path = None
        logger.info("📄 PDF generation skipped for simplicity")
        
        logger.info(f"\n🎉 BOOK GENERATION COMPLETE!")
        logger.info(f"📊 Total Cost: ${total_cost:.4f}")
        logger.info(f"✅ Successful Chapters: {successful_chapters}")
        logger.info(f"⚠️  Failed Chapters: {failed_chapters}")
        logger.info(f"📄 Total Chapters: {len(chapters)}")
        logger.info(f"📚 Book Title: {req.title}")
        logger.info(f"💾 Markdown: {book_path}")
        logger.info(f"🌐 HTML: {html_path}")
        if pdf_path:
            logger.info(f"📄 PDF: {pdf_path}")
        
        return {
            "success": True,
            "title": req.title,
            "chapters": len(chapters),
            "successful_chapters": successful_chapters,
            "failed_chapters": failed_chapters,
            "total_cost": total_cost,
            "files": {
                "markdown": str(book_path),
                "html": html_path,
                "pdf": pdf_path
            },
            "rag_enhanced": Config.RAG_ENABLED and req.use_rag,
            "chapter_contents": chapter_contents
        }
        
    except Exception as e:
        logger.error(f"❌ Complete book generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent endpoints
@app.post("/agent/run")
def agent_run(req: AgentReq):
    """Run reasoning agent"""
    try:
        logger.info(f"🤖 Running agent with goal: {req.goal}")
        trace, result = run_agent(req.goal, req.model, req.max_steps)
        return {"result": result, "trace": trace}
    except Exception as e:
        logger.error(f"❌ Agent run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simple-workflow")
def simple_workflow(req: SimpleWorkflowReq):
    """Run simple book generation workflow"""
    try:
        logger.info(f"🚀 Running simple workflow for: {req.topic}")
        
        # Log book type information
        if req.book_type and req.book_type_info:
            logger.info(f"📚 Book type: {req.book_type_info['name']}")
            logger.info(f"🎯 Target audience: {req.book_type_info['target_audience']}")
            logger.info(f"✍️  Writing style: {req.book_type_info['writing_style']}")
            logger.info(f"📋 Content approach: {req.book_type_info['content_approach']}")
        else:
            logger.info("📝 Using generic content generation (no book type specified)")
        
        # Log source content usage
        if req.source_content:
            logger.info(f"📖 Using source content: {len(req.source_content)} characters")
        else:
            logger.info("📝 Generating content without source material")
        
        # NEW ARCHITECTURE: Proper file-based iterative approach
        from datetime import datetime
        from .markdown_tools import (
            copy_source_to_exports, 
            split_markdown_by_chapters,
            extend_chapter_content,
            restructure_chapter_with_introduction,
            compile_chapters_to_book,
            calculate_book_statistics
        )
        from .report_generator import generate_book_report
        
        # Step 1: Create book working directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in req.topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()
        
        book_dir = EXPORTS_DIR / f"{safe_title}_{timestamp}"
        
        logger.info(f"📁 STEP 1: Creating book working directory")
        logger.info(f"   📖 Title: {req.topic}")
        logger.info(f"   📁 Safe title: {safe_title}")
        logger.info(f"   🕐 Timestamp: {timestamp}")
        logger.info(f"   📁 Directory: {book_dir}")
        
        book_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"✅ FOLDER CREATED: {book_dir}")
        
        # Step 2: Process source content (if provided)
        chapters = []
        if req.source_content:
            logger.info(f"📋 STEP 2: Processing source content")
            logger.info(f"   📊 Source size: {len(req.source_content):,} characters")
            logger.info(f"   📊 Source words: {len(req.source_content.split()):,}")
            
            # Create temporary source file
            temp_source = book_dir / "source_content.md"
            temp_source.write_text(req.source_content, encoding='utf-8')
            
            logger.info(f"✅ SOURCE FILE CREATED: {temp_source}")
            
            # Step 3: Split markdown into chapters
            logger.info(f"✂️ STEP 3: Splitting markdown into chapters")
            chapters = split_markdown_by_chapters(temp_source, book_dir)
            
            if not chapters:
                logger.error(f"❌ SPLIT FAILED: No chapters found in source content")
                raise HTTPException(status_code=400, detail="No chapters found in source content. Please ensure your markdown has ## chapter headers.")
                
            logger.info(f"✅ SPLIT COMPLETED: {len(chapters)} chapters created")
        else:
            # Create chapters from scratch if no source content
            for i in range(1, req.chapters + 1):
                chapter_title = f"{i}. {req.topic} - Part {i}"
                safe_chapter_title = "".join(c for c in chapter_title if c.isalnum() or c in (' ', '-', '_'))
                safe_chapter_title = safe_chapter_title.replace(' ', '_').lower()
                
                chapter_file = book_dir / f"chapter_{i:02d}_{safe_chapter_title}.md"
                initial_content = f"## {chapter_title}\n\nThis chapter will cover {req.topic} in detail.\n\n### Introduction\n\nContent to be expanded...\n"
                chapter_file.write_text(initial_content, encoding='utf-8')
                
                chapter_info = {
                    "number": i,
                    "title": chapter_title,
                    "file_path": chapter_file,
                    "word_count": len(initial_content.split()),
                    "safe_title": safe_chapter_title
                }
                chapters.append(chapter_info)
        
        # Step 4 & 5: Reasoning loop for each chapter
        total_cost = 0
        target_words_per_chapter = req.words_per_chapter
        
        # Prepare context facts from source content
        context_facts = []
        if req.source_content:
            context_facts = [{
                "text": req.source_content,
                "source": {"title": "Source Content", "type": "user_provided"},
                "confidence": 1.0,
                "citeKey": "source_content"
            }]
        
        logger.info(f"🔄 STEP 4-5: Starting reasoning agent extension loop")
        logger.info(f"   📄 Chapters to process: {len(chapters)}")
        logger.info(f"   📊 Target per chapter: {target_words_per_chapter:,} words")
        logger.info(f"   📊 Total target: {len(chapters) * target_words_per_chapter:,} words")
        
        for i, chapter in enumerate(chapters, 1):
            logger.info(f"🔄 PROCESSING CHAPTER {i}/{len(chapters)}: {chapter['title']}")
            logger.info(f"   📁 Chapter file: {chapter['file_path'].name}")
            logger.info(f"   📊 Original words: {chapter.get('word_count', 0):,}")
            logger.info(f"   🎯 Target words: {target_words_per_chapter:,}")
            
            # Add target words to chapter info
            chapter["target_words"] = target_words_per_chapter
            
            # Extend chapter content using reasoning agent
            result = extend_chapter_content(
                chapter_file=chapter["file_path"],
                target_words=target_words_per_chapter,
                model=WRITER_MODEL,
                context_facts=context_facts,
                book_type_info=req.book_type_info
            )
            
            # Update chapter with results
            chapter.update(result)
            total_cost += result.get("cost", 0)
            
            completion_percentage = result.get('completion_rate', 0)
            final_words = result.get('final_word_count', 0)
            
            logger.info(f"✅ CHAPTER {i} COMPLETED:")
            logger.info(f"   📊 Final words: {final_words:,}/{target_words_per_chapter:,}")
            logger.info(f"   📈 Completion: {completion_percentage:.1f}%")
            logger.info(f"   💰 Cost: ${result.get('cost', 0):.4f}")
            logger.info(f"   🔄 Attempts: {result.get('attempts', 0)}")
        
        # NEW STEP: Restructure chapters with introductions
        logger.info(f"🔧 STEP 5.5: Restructuring chapters with introductions")
        
        restructure_total_cost = 0
        restructure_total_words_added = 0
        
        for i, chapter in enumerate(chapters, 1):
            logger.info(f"🔧 RESTRUCTURING {i}/{len(chapters)}: {chapter['title']}")
            
            restructure_result = restructure_chapter_with_introduction(
                chapter_file=chapter["file_path"],
                model=WRITER_MODEL
            )
            
            if restructure_result["success"]:
                words_added = restructure_result.get("words_added", 0)
                cost_added = restructure_result.get("cost", 0)
                restructure_total_words_added += words_added
                restructure_total_cost += cost_added
                chapter["final_word_count"] = chapter.get("final_word_count", 0) + words_added
                
                logger.info(f"✅ RESTRUCTURE {i} COMPLETED:")
                logger.info(f"   📊 Words added: +{words_added:,}")
                logger.info(f"   💰 Cost: ${cost_added:.4f}")
            else:
                logger.warning(f"⚠️ Failed to restructure chapter {i}")
        
        logger.info(f"✅ ALL RESTRUCTURING COMPLETED:")
        logger.info(f"   📊 Total words added: +{restructure_total_words_added:,}")
        logger.info(f"   💰 Total restructure cost: ${restructure_total_cost:.4f}")
        
        # Update total cost
        total_cost += restructure_total_cost
        
        # Step 6 & 7: Compile all chapters into final book
        logger.info(f"📚 STEP 6-7: Compiling final book")
        book_file = compile_chapters_to_book(chapters, book_dir, req.topic)
        book_content = book_file.read_text(encoding='utf-8')
        
        # Step 8: Calculate comprehensive statistics
        logger.info(f"📊 STEP 8: Calculating comprehensive statistics")
        statistics = calculate_book_statistics(chapters, total_cost)
        
        logger.info(f"✅ STATISTICS CALCULATED:")
        logger.info(f"   📄 Total chapters: {statistics['total_chapters']}")
        logger.info(f"   📊 Total words: {statistics['total_words']:,}")
        logger.info(f"   📈 Overall completion: {statistics['overall_completion_rate']:.1f}%")
        logger.info(f"   📑 Estimated pages: {statistics['estimated_pages']}")
        logger.info(f"   💰 Total cost: ${statistics['total_cost']:.4f}")
        
        # Step 8.5: Generate HTML report
        logger.info(f"📋 STEP 8.5: Generating HTML report")
        report_path = None  # Initialize to avoid scope issues
        try:
            # Calculate actual generation time if available
            generation_end_time = datetime.now()
            generation_time_minutes = None  # Could be calculated if we track start time
            
            # Create agent statistics for the report
            agent_statistics = {
                "total_attempts": sum(chapter.get("attempts", 0) for chapter in chapters),
                "total_target_words": len(chapters) * target_words_per_chapter,
                "total_generated_words": statistics['total_words'],
                "overall_completion_rate": f"{statistics['overall_completion_rate']:.1f}%",
                "estimated_pages": statistics['estimated_pages'],
                "chapter_breakdown": [
                    {
                        "chapter": chapter.get("number", i),
                        "title": chapter.get("title", f"Chapter {i}"),
                        "target_words": chapter.get("target_words", target_words_per_chapter),
                        "original_words": chapter.get("original_word_count", 0),
                        "final_words": chapter.get("final_word_count", 0),
                        "estimated_pages": round(chapter.get("final_word_count", 0) / 250, 1),
                        "attempts": chapter.get("attempts", 0),
                        "completion_rate": f"{chapter.get('completion_rate', 0):.1f}%",
                        "cost": chapter.get("cost", 0)
                    }
                    for i, chapter in enumerate(chapters, 1)
                ]
            }
            
            # Generate the HTML report
            report_path = generate_book_report(
                book_title=req.topic,
                book_dir=book_dir,
                statistics=statistics,
                agent_statistics=agent_statistics,
                generation_time_minutes=generation_time_minutes
            )
            
            logger.info(f"✅ HTML REPORT GENERATED:")
            logger.info(f"   📋 Report file: {report_path.name}")
            logger.info(f"   📁 Location: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate HTML report: {e}")
            # Continue without failing the entire process
        
        logger.info(f"🎉 BOOK GENERATION COMPLETED!")
        logger.info(f"📊 COMPREHENSIVE STATISTICS:")
        logger.info(f"   📖 Title: {req.topic}")
        logger.info(f"   📄 Chapters: {statistics['total_chapters']}")
        logger.info(f"   🎯 Target Total Words: {statistics['total_target_words']:,}")
        logger.info(f"   ✅ Actual Total Words: {statistics['total_words']:,} ({statistics['overall_completion_rate']:.1f}%)")
        logger.info(f"   📑 Estimated Pages: {statistics['estimated_pages']}")
        logger.info(f"   🔄 Total Attempts: {statistics['total_attempts']}")
        logger.info(f"   💰 Total Cost: ${statistics['total_cost']:.4f}")
        logger.info(f"   📁 Book saved to: {book_dir}")
        
        # Log detailed per-chapter breakdown
        logger.info(f"📋 DETAILED CHAPTER BREAKDOWN:")
        for ch_stat in statistics["chapters"]:
            logger.info(f"   Ch{ch_stat['number']}: '{ch_stat['title']}'")
            logger.info(f"      📝 Words: {ch_stat['original_words']} → {ch_stat['final_words']}/{ch_stat['target_words']} ({ch_stat['completion_rate']:.1f}%)")
            logger.info(f"      📑 Pages: ~{ch_stat['estimated_pages']}")
            logger.info(f"      🔄 Attempts: {ch_stat['attempts']}")
            logger.info(f"      💰 Cost: ${ch_stat['cost']:.4f}")
        
        md_path = book_file
        
        # Save HTML with proper book styling
        from .book_styles import get_style
        
        # Get the book style (default to modern)
        book_style = get_style("modern")
        
        # Convert markdown to proper HTML
        import re
        html_body = book_content
        
        # Convert markdown headers (handle multiple # levels)
        html_body = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
        
        # Convert other markdown elements
        # Bold and italic
        html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
        html_body = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_body)
        
        # Code blocks and inline code
        html_body = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html_body, flags=re.DOTALL)
        html_body = re.sub(r'`(.+?)`', r'<code>\1</code>', html_body)
        
        # Convert paragraphs and line breaks
        html_body = re.sub(r'\n\n+', '</p><p>', html_body)
        html_body = f'<p>{html_body}</p>'
        
        # Fix headers that got wrapped in paragraphs
        for i in range(1, 6):
            html_body = html_body.replace(f'<p><h{i}', f'<h{i}').replace(f'</h{i}></p>', f'</h{i}>')
        
        # Fix other elements
        html_body = html_body.replace('<p><hr></p>', '<hr>')
        html_body = html_body.replace('<p><pre>', '<pre>').replace('</pre></p>', '</pre>')
        html_body = html_body.replace('---', '<hr>')
        
        # Create styled HTML with MathJax support
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{req.topic}</title>
    
    <!-- MathJax Configuration -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <style>
        {book_style.css_styles}
        
        /* Additional book-specific styling */
        .book-header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
        }}
        
        .chapter {{
            margin-bottom: 40px;
            page-break-before: always;
        }}
        
        .chapter-title {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        /* Math styling */
        .MathJax {{
            outline: 0;
        }}
        
        mjx-container[jax="CHTML"] {{
            line-height: 0;
        }}
        
        @media print {{
            .chapter {{ page-break-before: always; }}
            body {{ font-size: 12pt; }}
        }}
    </style>
</head>
<body>
    <div class="book-header">
        <h1>{req.topic}</h1>
        <p>Generated by Book Creator AI</p>
    </div>
    
    <div class="book-content">
        {html_body}
    </div>
</body>
</html>"""
        
        # Save styled HTML
        html_path = book_dir / f"{safe_title}.html"
        html_path.write_text(html_content, encoding='utf-8')
        
        # Also create different style versions
        style_variants = ["academic", "modern", "compact", "ebook"]
        style_files = {}
        
        for style_name in style_variants:
            try:
                variant_style = get_style(style_name)
                variant_html = html_content.replace(book_style.css_styles, variant_style.css_styles)
                variant_path = book_dir / f"{safe_title}_{style_name}.html"
                variant_path.write_text(variant_html, encoding='utf-8')
                style_files[style_name] = str(variant_path)
            except Exception as e:
                logger.warning(f"⚠️ Could not create {style_name} style: {e}")
        
        # Statistics logging is handled by the new architecture above
        
        return {
            "success": True, 
            "result": {
                "topic": req.topic,
                "chapters": statistics["total_chapters"],
                "total_cost": statistics["total_cost"],
                "files": {
                    "markdown": str(md_path),
                    "html": str(html_path),
                    "directory": str(book_dir),
                    "styles": style_files,
                    "report": str(report_path) if report_path else None,
                    "chapter_files": [str(ch["file_path"]) for ch in chapters]
                },
                "book_styles_created": len(style_files) + 1,  # +1 for main HTML
                "statistics": statistics,
                "agent_statistics": {
                    "total_target_words": statistics["total_target_words"],
                    "total_generated_words": statistics["total_words"],
                    "overall_completion_rate": f"{statistics['overall_completion_rate']:.1f}%",
                    "estimated_pages": statistics["estimated_pages"],
                    "total_attempts": statistics["total_attempts"],
                    "chapter_breakdown": [
                        {
                            "chapter": ch_stat['number'],
                            "title": ch_stat['title'],
                            "target_words": ch_stat['target_words'],
                            "original_words": ch_stat['original_words'],
                            "final_words": ch_stat['final_words'],
                            "estimated_pages": ch_stat['estimated_pages'],
                            "attempts": ch_stat['attempts'],
                            "completion_rate": f"{ch_stat['completion_rate']:.1f}%",
                            "cost": ch_stat['cost']
                        }
                        for ch_stat in statistics["chapters"]
                    ]
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Simple workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Style endpoints
@app.get("/styles")
def get_styles():
    """Get available book styles"""
    return {"styles": list_styles()}

@app.get("/styles/{style_name}")
def get_style_details(style_name: str):
    """Get details for a specific style"""
    try:
        style = get_style(style_name)
        return {"style": style.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Style not found: {style_name}")

# RAG endpoints (only available if RAG is enabled)
if Config.RAG_ENABLED:
    
    @app.post("/upload")
    async def upload_file(file: UploadFile = File(...)):
        """Upload and process file for RAG"""
        try:
            logger.info(f"📤 Uploading file: {file.filename}")
            
            # Save uploaded file
            file_path = UPLOADS_DIR / file.filename
            content = await file.read()
            file_path.write_bytes(content)
            
            # Process and ingest file
            result = ingest_file(str(file_path))
            
            return {
                "success": True,
                "filename": file.filename,
                "size": len(content),
                "ingestion_result": result
            }
        except Exception as e:
            logger.error(f"❌ File upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/upload-html")
    async def upload_html_file(file: UploadFile = File(...)):
        """Upload and process HTML file from Google Docs"""
        try:
            logger.info(f"📄 Uploading HTML file: {file.filename}")
            
            # Validate file type
            if not file.filename.lower().endswith(('.html', '.htm', '.zip')):
                raise HTTPException(
                    status_code=400, 
                    detail="Only HTML and ZIP files are supported"
                )
            
            # Save uploaded file
            file_path = UPLOADS_DIR / file.filename
            content = await file.read()
            file_path.write_bytes(content)
            
            # Create temporary extraction directory
            temp_dir = create_temp_extraction_dir()
            
            try:
                # Process HTML file
                processor = HTMLProcessor()
                result = processor.process_html_upload(file_path, temp_dir)
                
                # Save processed markdown to uploads for potential book generation
                markdown_filename = f"{file.filename.split('.')[0]}_processed.md"
                markdown_path = UPLOADS_DIR / markdown_filename
                markdown_path.write_text(result['markdown_content'], encoding='utf-8')
                
                # Copy images to uploads directory if any
                if result['images']:
                    images_dir = UPLOADS_DIR / f"{file.filename.split('.')[0]}_images"
                    images_dir.mkdir(exist_ok=True)
                    
                    for img in result['images']:
                        if img.get('local_path') and Path(img['local_path']).exists():
                            dest_path = images_dir / Path(img['local_path']).name
                            shutil.copy2(img['local_path'], dest_path)
                            img['saved_path'] = str(dest_path)
                
                logger.info(f"✅ HTML processed: {result['word_count']} words, {len(result['images'])} images")
                
                return {
                    "success": True,
                    "filename": file.filename,
                    "processed_markdown": markdown_filename,
                    "original_size": len(content),
                    "processing_result": {
                        "title": result['title'],
                        "word_count": result['word_count'],
                        "estimated_chapters": result['estimated_chapters'],
                        "images_count": len(result['images']),
                        "structure": result['structure']
                    },
                    "markdown_content": result['markdown_content'][:500] + "..." if len(result['markdown_content']) > 500 else result['markdown_content'],
                    "images": result['images']
                }
                
            finally:
                # Clean up temporary directory
                cleanup_temp_dir(temp_dir)
                
        except Exception as e:
            logger.error(f"❌ HTML upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/ingest")
    async def ingest_directory_endpoint(directory_path: str = Form(...)):
        """Ingest directory of files"""
        try:
            logger.info(f"📚 Ingesting directory: {directory_path}")
            result = ingest_directory(directory_path)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"❌ Directory ingestion failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/rag/stats")
    def rag_stats():
        """Get RAG collection statistics"""
        try:
            stats = get_collection_stats()
            return stats
        except Exception as e:
            logger.error(f"❌ RAG stats failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/rag/query")
    def rag_query(query: str = Form(...), k: int = Form(Config.RAG_TOP_K)):
        """Query RAG system"""
        try:
            logger.info(f"🔍 RAG query: {query}")
            results = fact_pack(query, k=k)
            return {"success": True, "results": results}
        except Exception as e:
            logger.error(f"❌ RAG query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/rag/clear")
    def clear_rag():
        """Clear RAG collection"""
        try:
            logger.info("🗑️ Clearing RAG collection")
            result = clear_collection()
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"❌ RAG clear failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Development server runner
if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Starting Book Creator API server (RAG: {'enabled' if Config.RAG_ENABLED else 'disabled'})")
    uvicorn.run(app, host="0.0.0.0", port=8000) 