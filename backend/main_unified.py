import os, json, subprocess, shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .reasonning_agent import run_agent, run_simple_workflow
from .planner import generate_outline
from .writer import write_chapter
from .llm import complete_json
from . import tools as T
from .settings import WRITER_MODEL, PLANNER_MODEL
from .book_styles import get_style, list_styles, create_custom_style, BOOK_STYLES
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

# Core book generation endpoints
@app.post("/generate-outline")
def generate_outline_endpoint(req: OutlineReq):
    """Generate book outline"""
    try:
        logger.info(f"📋 Generating outline for: {req.topic}")
        outline = generate_outline(
            topic=req.topic,
            target_audience=req.target_audience,
            style=req.style,
            target_pages=req.target_pages
        )
        return {"success": True, "outline": outline}
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
                chapter = write_chapter(chapter_title, chapter_number=i)
                results.append({"chapter": i, "title": chapter_title, "content": chapter})
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
        outline_data = generate_outline(
            topic=req.title,
            target_audience=req.target_audience,
            style=req.style,
            target_pages=req.target_pages
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
                
                # Generate chapter content
                chapter_result = write_chapter(
                    chapter_title, 
                    chapter_number=i,
                    rag_context=rag_context if rag_context else None
                )
                
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
        safe_title = "".join(c for c in req.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()
        
        book_path = EXPORTS_DIR / f"{safe_title}.md"
        book_path.write_text(book_content, encoding='utf-8')
        logger.info(f"✅ Book saved: {book_path} ({len(book_content.encode('utf-8'))} bytes)")
        
        # Step 5: Build HTML
        logger.info("\n🌐 STEP 5: Building HTML with MathJax support...")
        html_path = T.build_html_book(
            markdown_path=str(book_path),
            title=req.title,
            book_style=req.book_style,
            custom_style={
                "font_family": req.font_family,
                "line_height": req.line_height,
                "paragraph_spacing": req.paragraph_spacing,
                "header_spacing": req.header_spacing,
                "max_width": req.max_width,
                "color_scheme": req.color_scheme
            } if any([req.font_family, req.line_height, req.paragraph_spacing, 
                     req.header_spacing, req.max_width, req.color_scheme]) else None
        )
        logger.info(f"✅ HTML book built: {html_path}")
        
        # Step 6: Build PDF (if enabled)
        pdf_path = None
        if Config.PDF_GENERATION:
            try:
                logger.info("\n📄 STEP 6: Building PDF...")
                pdf_path = T.build_pdf_book(str(book_path), safe_title)
                logger.info(f"✅ PDF book built: {pdf_path}")
            except Exception as e:
                logger.warning(f"⚠️ PDF generation failed: {e}")
        
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
        result = run_simple_workflow(req.topic, req.chapters, req.words_per_chapter)
        return {"success": True, "result": result}
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