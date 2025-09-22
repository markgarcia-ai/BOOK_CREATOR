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
import sys
sys.path.append(str(Path(__file__).parent.parent))
from rag.retrieve import fact_pack, get_collection_stats
from rag.ingest import ingest_file, ingest_directory, clear_collection
from rag.pdf_processor import DocumentProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Book Creator API with RAG", version="3.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "book"
EXPORTS_DIR = ROOT / "exports"
UPLOADS_DIR = ROOT / "uploads"
RAG_DIR = ROOT / "rag"
RAG_DB_DIR = RAG_DIR / "db"

# Ensure directories exist
BOOK_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
RAG_DB_DIR.mkdir(exist_ok=True)

class GenerateReq(BaseModel):
    title: str
    chapters: List[str]
    words_per_chapter: int = 3500

class AgentReq(BaseModel):
    goal: str
    max_steps: int = 8
    model: str = WRITER_MODEL

class OutlineReq(BaseModel):
    topic: str
    chapters: int = 10
    words_per_chapter: int = 3500
    audience: str = "General audience"
    tone: str = "Professional"

class GenerateBookReq(BaseModel):
    topic: str
    target_pages: int = 50
    target_audience: str = "General audience"
    style: str = "informative"
    source_file: Optional[str] = None
    book_style: Optional[str] = None
    font_family: Optional[str] = None
    line_height: Optional[str] = None
    paragraph_spacing: Optional[str] = None
    header_spacing: Optional[str] = None
    max_width: Optional[str] = None
    color_scheme: Optional[str] = None
    use_rag: bool = True  # New field to enable/disable RAG
    rag_query: Optional[str] = None  # Custom RAG query

@app.get("/health")
def health(): 
    return {"ok": True, "status": "Book Creator API with RAG is running"}

@app.get("/status")
def get_status():
    """Get project status including RAG stats"""
    status = T.get_project_status()
    
    # Add RAG statistics
    try:
        rag_stats = get_collection_stats()
        status["rag"] = rag_stats
    except Exception as e:
        status["rag"] = {"error": str(e), "status": "error"}
    
    return status

@app.get("/styles")
def get_styles():
    """Get available predefined book styles and custom options."""
    predefined = {name: {"name": style.name, "description": style.description} for name, style in BOOK_STYLES.items()}
    custom_options = {
        "font_families": ["Arial", "Times New Roman", "Georgia", "Helvetica", "Verdana", "Monaco"],
        "line_heights": ["1.2", "1.3", "1.4", "1.5", "1.6", "1.7"],
        "paragraph_spacings": ["0.5em", "0.8em", "1em", "1.2em", "1.5em", "2em"],
        "header_spacings": ["1em", "1.5em", "2em", "2.5em", "3em"],
        "max_widths": ["600px", "700px", "800px", "900px", "100%"],
        "color_schemes": ["default", "dark", "sepia", "blue"]
    }
    return {"predefined_styles": predefined, "custom_options": custom_options}

@app.post("/upload-source")
async def upload_source(file: UploadFile = File(...)):
    """Upload a source file (PDF, DOCX, TXT, MD) for RAG ingestion"""
    try:
        file_path = UPLOADS_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Automatically ingest into RAG if it's a supported format
        processor = DocumentProcessor()
        if file_path.suffix.lower() in processor.supported_formats:
            try:
                chunks_ingested = ingest_file(file_path)
                return {
                    "filename": file.filename, 
                    "path": str(file_path), 
                    "message": "File uploaded and ingested into RAG successfully",
                    "chunks_ingested": chunks_ingested
                }
            except Exception as e:
                return {
                    "filename": file.filename, 
                    "path": str(file_path), 
                    "message": "File uploaded but RAG ingestion failed",
                    "error": str(e)
                }
        else:
            return {
                "filename": file.filename, 
                "path": str(file_path), 
                "message": "File uploaded successfully (not ingested - unsupported format)"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")

@app.post("/rag/ingest")
async def ingest_rag_files(
    file_path: Optional[str] = Form(None),
    directory_path: Optional[str] = Form(None),
    chunk_size: int = Form(1000),
    overlap: int = Form(200)
):
    """Ingest files into RAG system"""
    try:
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            chunks = ingest_file(path, chunk_size, overlap)
            return {"message": f"Ingested {chunks} chunks from {file_path}", "chunks": chunks}
        
        elif directory_path:
            path = Path(directory_path)
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"Directory not found: {directory_path}")
            chunks = ingest_directory(path, chunk_size, overlap)
            return {"message": f"Ingested {chunks} chunks from {directory_path}", "chunks": chunks}
        
        else:
            raise HTTPException(status_code=400, detail="Either file_path or directory_path must be provided")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG ingestion failed: {e}")

@app.post("/rag/clear")
def clear_rag_collection():
    """Clear all data from RAG collection"""
    try:
        clear_collection()
        return {"message": "RAG collection cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear RAG collection: {e}")

@app.get("/rag/stats")
def get_rag_stats():
    """Get RAG collection statistics"""
    try:
        stats = get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get RAG stats: {e}")

@app.post("/rag/query")
def query_rag(query: str, k: int = 5):
    """Query the RAG system for relevant information"""
    try:
        results = fact_pack(query, k)
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

@app.post("/generate-book")
async def generate_book_endpoint(req: GenerateBookReq):
    """
    Generates a complete book with RAG integration.
    Process: Upload -> RAG -> Generate with context
    """
    logger.info(f"🚀 Starting RAG-enhanced book generation...")
    logger.info(f"📖 Topic: {req.topic}")
    logger.info(f"👥 Audience: {req.target_audience}")
    logger.info(f"📝 Style: {req.style}")
    logger.info(f"📄 Target pages: {req.target_pages}")
    logger.info(f"🔍 Use RAG: {req.use_rag}")
    
    style_options = {
        "book_style": req.book_style,
        "font_family": req.font_family,
        "line_height": req.line_height,
        "paragraph_spacing": req.paragraph_spacing,
        "header_spacing": req.header_spacing,
        "max_width": req.max_width,
        "color_scheme": req.color_scheme,
    }
    # Filter out None values
    style_options = {k: v for k, v in style_options.items() if v is not None}
    
    if style_options:
        logger.info(f"🎨 Book style: {req.book_style if req.book_style else 'Custom'}")
    
    total_cost = 0.0
    all_chapters_content = []
    book_title_slug = req.topic.lower().replace(" ", "_").replace(":", "").replace(",", "")
    
    try:
        # STEP 1: Gather RAG context if enabled
        rag_context = ""
        if req.use_rag:
            logger.info("\n🔍 STEP 1: Gathering RAG context...")
            
            # Use custom query or default to topic
            query = req.rag_query or req.topic
            logger.info(f"🔍 RAG Query: {query}")
            
            try:
                rag_results = fact_pack(query, k=10)  # Get more context for planning
                if rag_results:
                    rag_context = "\n\n".join([
                        f"**Source: {result['source']['title']}**\n{result['text']}"
                        for result in rag_results[:5]  # Use top 5 for planning
                    ])
                    logger.info(f"✅ Retrieved {len(rag_results)} relevant documents from RAG")
                    logger.info(f"📚 RAG context length: {len(rag_context)} characters")
                else:
                    logger.info("⚠️  No RAG results found - proceeding without context")
            except Exception as e:
                logger.warning(f"⚠️  RAG query failed: {e} - proceeding without context")
        
        # STEP 2: Generate Outline with RAG context
        logger.info("\n🧠 STEP 2: Generating comprehensive outline...")
        logger.info(f"🤖 Using model: {PLANNER_MODEL}")
        
        # Estimate words per chapter for target pages
        words_per_chapter_estimate = (req.target_pages * 300) // 8
        
        planner_system_prompt = Path("prompts/planner.md").read_text()
        
        # Enhanced user prompt with RAG context
        user_prompt = f"""
        Create a comprehensive book outline for a {req.target_pages}-page book on "{req.topic}".
        
        Target audience: {req.target_audience}
        Style: {req.style}
        
        The book should have:
        - A compelling title and subtitle
        - A detailed description
        - An estimated total word count
        - A list of 8-12 chapters
        - Each chapter should have a title, a brief summary, and 3-5 key sections
        - Each chapter should target approximately {words_per_chapter_estimate} words
        - Ensure the outline is structured for a {req.style} tone and {req.target_audience} audience
        - Include a 'Conclusion' chapter
        - Avoid using complex LaTeX math syntax in the JSON output. If math is needed, describe it in plain text or use simple inline markdown math.
        """
        
        # Add RAG context if available
        if rag_context:
            user_prompt += f"""
            
            IMPORTANT: Use the following source material to inform your outline:
            {rag_context}
            
            Base your outline on this source material while ensuring comprehensive coverage of the topic.
            """
        
        outline_schema = """
        {
            "title": "string",
            "subtitle": "string",
            "description": "string",
            "audience": "string",
            "tone": "string",
            "total_target_words": "integer",
            "chapters": [
                {
                    "chapter_number": "integer",
                    "title": "string",
                    "summary": "string",
                    "target_words": "integer",
                    "sections": [
                        {"title": "string", "summary": "string"}
                    ]
                }
            ]
        }
        """
        
        outline_json, outline_metadata = T.llm.complete_json(
            model=PLANNER_MODEL,
            system=planner_system_prompt,
            user=user_prompt,
            schema_hint=outline_schema
        )
        total_cost += outline_metadata["cost"]
        logger.info(f"✅ Outline generated successfully!")
        logger.info(f"📊 Cost: ${outline_metadata['cost']:.4f}")
        logger.info(f"🔤 Tokens: {outline_metadata['input_tokens']} input, {outline_metadata['output_tokens']} output")
        logger.info(f"📚 Book title: {outline_json.get('title', req.topic)}")
        logger.info(f"📑 Chapters planned: {len(outline_json.get('chapters', []))}")
        
        # Save outline
        T.write_file(BOOK_DIR / "toc.json", json.dumps(outline_json, indent=2))
        
        # STEP 3: Write Chapters with RAG context
        logger.info("\n✍️  STEP 3: Writing chapters with RAG context...")
        logger.info(f"🤖 Using model: {WRITER_MODEL}")
        
        writer_system_prompt = Path("prompts/writer.md").read_text()
        chapter_schema = """
        {
            "chapter_number": "integer",
            "title": "string",
            "content": "string"
        }
        """
        
        for i, chapter_brief in enumerate(outline_json["chapters"]):
            logger.info(f"📝 Writing Chapter {i+1}/{len(outline_json['chapters'])}: {chapter_brief['title']}")
            
            # Get RAG context for this specific chapter
            chapter_rag_context = ""
            if req.use_rag:
                try:
                    chapter_query = f"{req.topic} {chapter_brief['title']} {chapter_brief['summary']}"
                    chapter_rag_results = fact_pack(chapter_query, k=5)
                    if chapter_rag_results:
                        chapter_rag_context = "\n\n".join([
                            f"**Source: {result['source']['title']}**\n{result['text']}"
                            for result in chapter_rag_results
                        ])
                        logger.info(f"🔍 Retrieved {len(chapter_rag_results)} relevant documents for chapter {i+1}")
                except Exception as e:
                    logger.warning(f"⚠️  RAG query failed for chapter {i+1}: {e}")
            
            chapter_user_prompt = f"""
            Write a comprehensive chapter for the book "{outline_json['title']}".
            
            Chapter {chapter_brief['chapter_number']}: {chapter_brief['title']}
            Summary: {chapter_brief['summary']}
            Target Words: {chapter_brief['target_words']}
            Sections: {json.dumps(chapter_brief['sections'], indent=2)}
            
            Ensure the content is detailed, engaging, and adheres to the overall book's target audience ({outline_json['audience']}) and tone ({outline_json['tone']}).
            Format the chapter using Markdown. Use appropriate headings (##, ###, ####).
            If mathematical equations are necessary, use standard Markdown inline math ($...$) or display math ($$...$$) and ensure they are correctly formatted for rendering with MathJax.
            Avoid using raw LaTeX commands that are not compatible with standard Markdown math rendering.
            """
            
            # Add RAG context for this chapter
            if chapter_rag_context:
                chapter_user_prompt += f"""
                
                IMPORTANT: Use the following source material to inform this chapter:
                {chapter_rag_context}
                
                Base your chapter content on this source material while ensuring it fits the chapter's focus and the overall book structure.
                """
            
            chapter_json, chapter_metadata = T.llm.complete_json(
                model=WRITER_MODEL,
                system=writer_system_prompt,
                user=chapter_user_prompt,
                schema_hint=chapter_schema
            )
            total_cost += chapter_metadata["cost"]
            logger.info(f"✅ Chapter {i+1} completed!")
            logger.info(f"💰 Cost: ${chapter_metadata['cost']:.4f}")
            logger.info(f"🔤 Tokens: {chapter_metadata['input_tokens']} input, {chapter_metadata['output_tokens']} output")
            logger.info(f"📄 Content length: {len(chapter_json.get('content', ''))} characters")
            
            all_chapters_content.append(chapter_json["content"])
            T.write_file(BOOK_DIR / "chapters" / f"{chapter_brief['chapter_number']:02d}-{book_title_slug}-{chapter_brief['title'].replace(' ','-').lower()}.md", chapter_json["content"])
        
        # STEP 4: Assemble and Save Book
        logger.info("\n📚 STEP 4: Assembling complete book...")
        full_markdown_content = f"# {outline_json['title']}\n\n"
        if outline_json.get('subtitle'):
            full_markdown_content += f"## {outline_json['subtitle']}\n\n"
        full_markdown_content += f"*Generated for {outline_json['audience']} audience in {outline_json['tone']} style*\n\n"
        full_markdown_content += f"*Total estimated pages: {req.target_pages}*\n\n"
        if req.use_rag:
            full_markdown_content += f"*This book was generated using RAG-enhanced AI with source material*\n\n"
        full_markdown_content += "\n\n".join(all_chapters_content)
        
        output_md_path = EXPORTS_DIR / f"{book_title_slug}.md"
        T.write_file(output_md_path, full_markdown_content)
        logger.info(f"💾 Saving book to file...")
        logger.info(f"✅ Book saved: {output_md_path} ({output_md_path.stat().st_size} bytes)")
        
        # STEP 5: Build HTML version with MathJax and Styling
        logger.info("\n🌐 STEP 5: Building HTML version with styling...")
        output_html_path = EXPORTS_DIR / f"{book_title_slug}.html"
        T.build_book_with_style(output_html_path, outline_json['title'], full_markdown_content, style_options)
        logger.info(f"✅ HTML version created: {output_html_path} ({output_html_path.stat().st_size} bytes)")
        
        logger.info(f"🎉 RAG-ENHANCED BOOK GENERATION COMPLETE!")
        logger.info(f"📚 Book Details:")
        logger.info(f"  • Title: {outline_json['title']}")
        logger.info(f"  • Chapters: {len(outline_json['chapters'])}")
        logger.info(f"  • Estimated Pages: {req.target_pages}")
        logger.info(f"  • Total Cost: ${total_cost:.4f}")
        logger.info(f"  • RAG Enhanced: {req.use_rag}")
        
        return {
            "success": True,
            "title": outline_json['title'],
            "chapters": len(outline_json['chapters']),
            "estimated_pages": req.target_pages,
            "total_cost": total_cost,
            "markdown_path": str(output_md_path),
            "html_path": str(output_html_path),
            "style_options": style_options,
            "rag_enhanced": req.use_rag,
            "rag_context_used": bool(rag_context)
        }
        
    except Exception as e:
        logger.error(f"❌ Book generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Book generation failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
