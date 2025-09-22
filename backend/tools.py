import json
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from .settings import BOOK, CHAPTERS, ASSETS, EXPORTS, ROOT

def write_file(relpath: str, text: str) -> Dict[str, Any]:
    """Write text to a file and return metadata"""
    p = (BOOK / relpath).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if content changed
    before_hash = None
    if p.exists():
        before_hash = hashlib.md5(p.read_text().encode()).hexdigest()
    
    p.write_text(text)
    after_hash = hashlib.md5(text.encode()).hexdigest()
    
    return {
        "path": str(p),
        "bytes": len(text.encode()),
        "updated": before_hash != after_hash,
        "hash": after_hash
    }

def read_file(relpath: str) -> Dict[str, Any]:
    """Read a file and return content with metadata"""
    p = (BOOK / relpath).resolve()
    if not p.exists():
        return {"error": f"File not found: {relpath}"}
    
    content = p.read_text()
    return {
        "path": str(p),
        "content": content,
        "bytes": len(content.encode()),
        "hash": hashlib.md5(content.encode()).hexdigest()
    }

def build_book(fmt: str = "pdf") -> Dict[str, Any]:
    """Build book using Pandoc"""
    EXPORTS.mkdir(parents=True, exist_ok=True)
    out = EXPORTS / f"book.{fmt}"
    
    # Find all markdown files in chapters
    md_files = sorted(CHAPTERS.glob("*.md"))
    if not md_files:
        return {"error": "No markdown files found in chapters directory"}
    
    # Build Pandoc command
    cmd = [
        "pandoc", "-s", 
        "--from", "markdown+footnotes+raw_tex",
        "--citeproc", 
        "--metadata-file", str(BOOK / "config.yml"),
        "-o", str(out)
    ] + [str(f) for f in md_files]
    
    try:
        subprocess.check_call(cmd, cwd=str(ROOT))
        return {
            "export": str(out),
            "chapters": [m.name for m in md_files],
            "format": fmt,
            "success": True
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": f"Pandoc build failed: {e}",
            "format": fmt,
            "success": False
        }

def list_chapters() -> Dict[str, Any]:
    """List all available chapters"""
    md_files = sorted(CHAPTERS.glob("*.md"))
    return {
        "chapters": [f.stem for f in md_files],
        "count": len(md_files)
    }

def get_project_status() -> Dict[str, Any]:
    """Get overall project status"""
    chapters = list_chapters()
    config_exists = (BOOK / "config.yml").exists()
    toc_exists = (BOOK / "toc.yaml").exists()
    
    return {
        "chapters": chapters["chapters"],
        "chapter_count": chapters["count"],
        "config_exists": config_exists,
        "toc_exists": toc_exists,
        "exports": list(EXPORTS.glob("*")) if EXPORTS.exists() else []
    }

def create_project_structure(title: str) -> Dict[str, Any]:
    """Create basic project structure"""
    # Create config.yml
    config_content = f'title: "{title}"\n'
    config_result = write_file("config.yml", config_content)
    
    # Create basic toc.yaml
    toc_content = f"""title: "{title}"
chapters: []
"""
    toc_result = write_file("toc.yaml", toc_content)
    
    return {
        "config": config_result,
        "toc": toc_result,
        "title": title
    }
