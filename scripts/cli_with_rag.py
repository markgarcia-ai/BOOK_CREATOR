import json, requests, typer
from rich import print, box
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from pathlib import Path
from typing import Optional

app = typer.Typer(help="Book Agent CLI with RAG Support")
console = Console()

API = "http://127.0.0.1:8000"

@app.command()
def health():
    """Check API health"""
    try:
        response = requests.get(f"{API}/health")
        response.raise_for_status()
        print("[green]✓ API is healthy[/]")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ API connection failed: {e}[/]")
        print("[yellow]Make sure the API server is running with: python -m backend.main_with_rag[/]")

@app.command()
def status():
    """Get project status including RAG stats"""
    try:
        response = requests.get(f"{API}/status")
        response.raise_for_status()
        data = response.json()
        
        # Create status table
        table = Table(title="Project Status", box=box.SIMPLE)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        table.add_row("Config", "✓" if data.get("config_exists") else "✗", "config.yml")
        table.add_row("Outline", "✓" if data.get("toc_exists") else "✗", "toc.yaml")
        table.add_row("Chapters", str(data.get("chapter_count", 0)), f"{len(data.get('chapters', []))} files")
        table.add_row("Exports", str(len(data.get("exports", []))), "Generated files")
        
        # Add RAG status
        rag_data = data.get("rag", {})
        if rag_data.get("status") == "success":
            table.add_row("RAG", "✓", f"{rag_data.get('total_documents', 0)} documents")
        else:
            table.add_row("RAG", "✗", "No documents or error")
        
        print(table)
        
        if data.get("chapters"):
            print("\n[bold]Chapters:[/]")
            for chapter in data["chapters"]:
                print(f"  • {chapter}")
        
        # Show RAG sources if available
        if rag_data.get("sources"):
            print("\n[bold]RAG Sources:[/]")
            for source, count in rag_data["sources"].items():
                print(f"  • {source}: {count} chunks")
                
    except requests.exceptions.RequestException as e:
        print(f"[red]Error getting status: {e}[/]")

@app.command()
def upload(file_path: Path = typer.Argument(..., exists=True, readable=True)):
    """Upload a source file (PDF, DOCX, TXT, MD) to the API for RAG ingestion."""
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            response = requests.post(f"{API}/upload-source", files=files)
            response.raise_for_status()
            data = response.json()
            print(f"[green]✓ File '{file_path.name}' uploaded successfully![/]")
            print(f"📁 Path: {data.get('path')}")
            print(f"💬 Message: {data.get('message')}")
            if 'chunks_ingested' in data:
                print(f"📚 Chunks ingested: {data['chunks_ingested']}")
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ File upload failed: {e}[/]")

@app.command()
def ingest(
    path: str = typer.Argument(..., help="File or directory path to ingest"),
    chunk_size: int = typer.Option(1000, "--chunk-size", help="Size of text chunks"),
    overlap: int = typer.Option(200, "--overlap", help="Overlap between chunks")
):
    """Ingest files into RAG system"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Ingesting files into RAG...", total=None)
            
            # Determine if it's a file or directory
            path_obj = Path(path)
            if path_obj.is_file():
                data = {"file_path": str(path_obj), "chunk_size": chunk_size, "overlap": overlap}
            else:
                data = {"directory_path": str(path_obj), "chunk_size": chunk_size, "overlap": overlap}
            
            response = requests.post(f"{API}/rag/ingest", data=data)
            response.raise_for_status()
            
            progress.update(task, description="[green]Ingestion complete!")
        
        result = response.json()
        print(f"[green]✓ {result['message']}[/]")
        print(f"📚 Total chunks: {result['chunks']}")
        
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Ingestion failed: {e}[/]")

@app.command()
def rag_stats():
    """Get RAG collection statistics"""
    try:
        response = requests.get(f"{API}/rag/stats")
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            print(f"[green]✓ RAG Collection Stats[/]")
            print(f"📚 Total documents: {data['total_documents']}")
            
            if data.get("sources"):
                print("\n[bold]Sources:[/]")
                table = Table(box=box.SIMPLE)
                table.add_column("Source", style="cyan")
                table.add_column("Chunks", justify="right")
                
                for source, count in data["sources"].items():
                    table.add_row(source, str(count))
                
                print(table)
        else:
            print(f"[red]✗ RAG error: {data.get('error', 'Unknown error')}[/]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Failed to get RAG stats: {e}[/]")

@app.command()
def rag_query(
    query: str = typer.Argument(..., help="Query to search in RAG system"),
    k: int = typer.Option(5, "--k", help="Number of results to return")
):
    """Query the RAG system for relevant information"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching RAG system...", total=None)
            
            response = requests.post(f"{API}/rag/query", json={"query": query, "k": k})
            response.raise_for_status()
            
            progress.update(task, description="[green]Search complete!")
        
        data = response.json()
        results = data["results"]
        
        print(f"[green]✓ Found {len(results)} results for: '{query}'[/]")
        
        for i, result in enumerate(results, 1):
            print(f"\n[bold]Result {i}:[/]")
            print(f"📄 Source: {result['source']['title']}")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"📝 Text: {result['text'][:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ RAG query failed: {e}[/]")

@app.command()
def rag_clear():
    """Clear all data from RAG collection"""
    try:
        response = requests.post(f"{API}/rag/clear")
        response.raise_for_status()
        data = response.json()
        print(f"[green]✓ {data['message']}[/]")
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Failed to clear RAG: {e}[/]")

@app.command("generate-book")
def generate_book_cli(
    topic: str = typer.Argument(..., help="The main topic of the book."),
    target_pages: int = typer.Option(50, "--target-pages", "-p", help="Approximate number of pages for the book."),
    target_audience: str = typer.Option("General audience", "--target-audience", "-a", help="The intended audience for the book."),
    style: str = typer.Option("informative", "--style", "-s", help="The writing style for the book (e.g., informative, technical, narrative)."),
    source_file: Optional[Path] = typer.Option(None, "--source-file", "-f", exists=True, readable=True, help="Optional markdown file to use as source material."),
    book_style: Optional[str] = typer.Option(None, "--book-style", help="Predefined book style (e.g., academic, modern, compact)."),
    font_family: Optional[str] = typer.Option(None, "--font-family", help="Custom font family (e.g., 'Arial', 'Times New Roman')."),
    line_height: Optional[str] = typer.Option(None, "--line-height", help="Custom line height (e.g., '1.5')."),
    paragraph_spacing: Optional[str] = typer.Option(None, "--paragraph-spacing", help="Custom paragraph spacing (e.g., '1em')."),
    header_spacing: Optional[str] = typer.Option(None, "--header-spacing", help="Custom header spacing (e.g., '2em')."),
    max_width: Optional[str] = typer.Option(None, "--max-width", help="Custom maximum content width (e.g., '800px', '100%')."),
    color_scheme: Optional[str] = typer.Option(None, "--color-scheme", help="Custom color scheme (e.g., 'dark', 'sepia')."),
    use_rag: bool = typer.Option(True, "--use-rag/--no-rag", help="Enable or disable RAG enhancement."),
    rag_query: Optional[str] = typer.Option(None, "--rag-query", help="Custom RAG query (defaults to topic).")
):
    """
    Generates a complete book with RAG enhancement.
    Process: Upload -> RAG -> Generate with context
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🤖 AI is generating your RAG-enhanced book...", total=None)
            
            payload = {
                "topic": topic,
                "target_pages": target_pages,
                "target_audience": target_audience,
                "style": style,
                "book_style": book_style,
                "font_family": font_family,
                "line_height": line_height,
                "paragraph_spacing": paragraph_spacing,
                "header_spacing": header_spacing,
                "max_width": max_width,
                "color_scheme": color_scheme,
                "use_rag": use_rag,
                "rag_query": rag_query,
            }
            if source_file:
                payload["source_file"] = str(source_file)

            # Filter out None values from payload
            payload = {k: v for k, v in payload.items() if v is not None}

            response = requests.post(f"{API}/generate-book", json=payload, timeout=1800)
            response.raise_for_status()
            
            progress.update(task, description="✅ RAG-enhanced book generation completed!")
        
        data = response.json()
        if data.get("success"):
            rag_status = "🔍 RAG Enhanced" if data.get("rag_enhanced") else "📝 Standard Generation"
            print(Panel(f"🎉 RAG-ENHANCED BOOK GENERATION SUCCESSFUL!\n\n"
                          f"📚 Book Details:\n"
                          f"  • Title: {data.get('title', topic)}\n"
                          f"  • Chapters: {data.get('chapters')}\n"
                          f"  • Estimated Pages: {data.get('estimated_pages')}\n"
                          f"  • Total Cost: ${data.get('total_cost', 0.0):.4f}\n"
                          f"  • {rag_status}\n"
                          f"  • RAG Context Used: {data.get('rag_context_used', False)}\n\n"
                          f"📁 Files Created:\n"
                          f"  • MARKDOWN: {data.get('markdown_path')} ({Path(data.get('markdown_path')).stat().st_size} bytes)\n"
                          f"  • HTML: {data.get('html_path')} ({Path(data.get('html_path')).stat().st_size} bytes)\n\n"
                          f"🎯 NEXT STEPS:\n"
                          f"1. View your book:\n"
                          f"   • Open markdown: open {data.get('markdown_path')}\n"
                          f"   • View in terminal: cat {data.get('markdown_path')}\n"
                          f"   • Open HTML: open {data.get('html_path')}\n\n"
                          f"2. Create additional formats:\n"
                          f"   • PDF: pandoc {data.get('markdown_path')} -o {Path(data.get('markdown_path')).parent / (Path(data.get('markdown_path')).stem + '.pdf')}\n"
                          f"   • EPUB: pandoc {data.get('markdown_path')} -o {Path(data.get('markdown_path')).parent / (Path(data.get('markdown_path')).stem + '.epub')}\n"
                          f"   • DOCX: pandoc {data.get('markdown_path')} -o {Path(data.get('markdown_path')).parent / (Path(data.get('markdown_path')).stem + '.docx')}\n\n"
                          f"3. Add more source material:\n"
                          f"   • Upload PDF: python scripts/cli_with_rag.py upload path/to/your.pdf\n"
                          f"   • Ingest directory: python scripts/cli_with_rag.py ingest path/to/sources/\n"
                          f"   • Query RAG: python scripts/cli_with_rag.py rag-query 'your search term'\n\n"
                          f"4. Customize your book:\n"
                          f"   • Edit content: nano {data.get('markdown_path')}\n"
                          f"   • Add images: Place in book/assets/img/\n"
                          f"   • Rebuild: python scripts/cli_with_rag.py build\n",
                          title="[bold green]RAG-Enhanced Book Generation Complete![/bold green]", style="green", expand=False))
        else:
            print(f"[red]✗ Book generation failed: {data.get('error', 'Unknown error')}[/]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Book generation failed: {e}[/]")

@app.command()
def styles():
    """List available predefined book styles and custom options."""
    try:
        response = requests.get(f"{API}/styles")
        response.raise_for_status()
        data = response.json()
        
        print("\n📚 Available Book Styles")
        print(f"Default style: {data['predefined_styles']['default']['name'].lower()}")
        
        table = Table(title="Book Styles", box=box.SIMPLE)
        table.add_column("Style", style="cyan")
        table.add_column("Description")
        
        for style_name, style_info in data['predefined_styles'].items():
            if style_name != "default":
                table.add_row(style_name.capitalize(), style_info['description'])
        
        print(table)
        
        print("\n🎨 Custom Style Options:")
        for option, values in data['custom_options'].items():
            print(f"  • {option.replace('_', ' ').title()}: {', '.join(values)}")
        
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Failed to retrieve styles: {e}[/]")

if __name__ == "__main__":
    app()
