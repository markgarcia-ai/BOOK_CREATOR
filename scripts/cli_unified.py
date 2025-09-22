import json, requests, typer
from rich import print, box
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import os
from pathlib import Path
from typing import Optional

app = typer.Typer(help="Book Creator Unified CLI")
console = Console()

API = "http://127.0.0.1:8000"

def get_api_features():
    """Get API features and configuration"""
    try:
        response = requests.get(f"{API}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("features", {}), data.get("config", {})
    except:
        return {}, {}

def check_rag_available():
    """Check if RAG features are available"""
    features, _ = get_api_features()
    return features.get("rag_enabled", False)

@app.command()
def health():
    """Check API health and show configuration"""
    try:
        response = requests.get(f"{API}/health")
        response.raise_for_status()
        data = response.json()
        
        print("[green]✓ API is healthy[/]")
        print(f"Version: [cyan]{data.get('version', 'unknown')}[/cyan]")
        
        # Show features
        features = data.get("features", {})
        print("\n[bold blue]📋 Available Features:[/bold blue]")
        feature_table = Table(box=box.SIMPLE)
        feature_table.add_column("Feature", style="cyan")
        feature_table.add_column("Status", style="green")
        
        for feature, enabled in features.items():
            status = "✅ Enabled" if enabled else "❌ Disabled"
            feature_table.add_row(feature.replace('_', ' ').title(), status)
        
        print(feature_table)
        
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ API connection failed: {e}[/]")
        print("[yellow]Make sure the API server is running with: python -m backend.main[/]")

@app.command()
def config():
    """Show current configuration"""
    try:
        response = requests.get(f"{API}/config")
        response.raise_for_status()
        config_data = response.json()
        
        print("[bold blue]⚙️  Current Configuration:[/bold blue]")
        for key, value in config_data.items():
            if not key.startswith('_'):
                print(f"  [cyan]{key}[/cyan]: [yellow]{value}[/yellow]")
                
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Configuration fetch failed: {e}[/]")

@app.command()
def styles():
    """List all available book styles"""
    try:
        response = requests.get(f"{API}/styles")
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[bold blue]📚 Available Book Styles[/bold blue]")
        
        # Create styles table
        table = Table(title="Book Styles", box=box.SIMPLE)
        table.add_column("Style", style="cyan")
        table.add_column("Description", style="yellow")
        
        for style_info in data['styles']:
            table.add_row(style_info['name'], style_info['description'])
        
        print(table)
        
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Styles fetch failed: {e}[/]")

@app.command()
def generate_book(
    title: str = typer.Argument(..., help="Book title"),
    target_audience: str = typer.Option("General audience", "--audience", help="Target audience"),
    style: str = typer.Option("informative", "--style", help="Writing style"),
    target_pages: int = typer.Option(10, "--target-pages", help="Target page count"),
    chapters: int = typer.Option(8, "--chapters", help="Number of chapters"),
    book_style: str = typer.Option("modern", "--book-style", help="Book visual style"),
    font_family: Optional[str] = typer.Option(None, "--font-family", help="Font family"),
    line_height: Optional[str] = typer.Option(None, "--line-height", help="Line height"),
    paragraph_spacing: Optional[str] = typer.Option(None, "--paragraph-spacing", help="Paragraph spacing"),
    header_spacing: Optional[str] = typer.Option(None, "--header-spacing", help="Header spacing"),
    max_width: Optional[str] = typer.Option(None, "--max-width", help="Max content width"),
    color_scheme: Optional[str] = typer.Option(None, "--color-scheme", help="Color scheme"),
    use_rag: bool = typer.Option(False, "--rag/--no-rag", help="Use RAG enhancement"),
    rag_query: Optional[str] = typer.Option(None, "--rag-query", help="Custom RAG query")
):
    """Generate a complete book"""
    
    # Check RAG availability if requested
    if use_rag and not check_rag_available():
        print("[yellow]⚠️  RAG requested but not available, proceeding without RAG[/yellow]")
        use_rag = False
    
    request_data = {
        "title": title,
        "target_audience": target_audience,
        "style": style,
        "target_pages": target_pages,
        "chapters": chapters,
        "book_style": book_style,
        "use_rag": use_rag
    }
    
    # Add optional parameters if provided
    if font_family:
        request_data["font_family"] = font_family
    if line_height:
        request_data["line_height"] = line_height
    if paragraph_spacing:
        request_data["paragraph_spacing"] = paragraph_spacing
    if header_spacing:
        request_data["header_spacing"] = header_spacing
    if max_width:
        request_data["max_width"] = max_width
    if color_scheme:
        request_data["color_scheme"] = color_scheme
    if rag_query:
        request_data["rag_query"] = rag_query
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating book...", total=None)
            
            response = requests.post(f"{API}/generate-book", json=request_data, timeout=600)
            response.raise_for_status()
            data = response.json()
            
            progress.update(task, completed=True)
        
        if data.get("success"):
            print(f"\n[green]✅ Book generation completed![/green]")
            print(f"📚 Title: [cyan]{data['title']}[/cyan]")
            print(f"📄 Chapters: [yellow]{data['chapters']}[/yellow]")
            print(f"✅ Successful: [green]{data['successful_chapters']}[/green]")
            print(f"❌ Failed: [red]{data['failed_chapters']}[/red]")
            print(f"💰 Total Cost: [yellow]${data['total_cost']:.4f}[/yellow]")
            
            if data.get("rag_enhanced"):
                print(f"🔍 RAG Enhanced: [green]Yes[/green]")
            
            print(f"\n[bold blue]📁 Generated Files:[/bold blue]")
            files = data.get("files", {})
            for file_type, file_path in files.items():
                if file_path:
                    print(f"  [cyan]{file_type.title()}[/cyan]: {file_path}")
        else:
            print(f"[red]❌ Book generation failed[/red]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Request failed: {e}[/]")

@app.command()
def outline(
    topic: str = typer.Argument(..., help="Book topic"),
    target_audience: str = typer.Option("General audience", "--audience", help="Target audience"),
    style: str = typer.Option("informative", "--style", help="Writing style"),
    target_pages: int = typer.Option(10, "--target-pages", help="Target page count")
):
    """Generate book outline"""
    request_data = {
        "topic": topic,
        "target_audience": target_audience,
        "style": style,
        "target_pages": target_pages
    }
    
    try:
        response = requests.post(f"{API}/generate-outline", json=request_data, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            outline = data["outline"]
            print(f"\n[bold blue]📋 Book Outline: {outline.get('title', topic)}[/bold blue]")
            
            chapters = outline.get("chapters", [])
            for i, chapter in enumerate(chapters, 1):
                print(f"\n[cyan]Chapter {i}: {chapter.get('title', 'Untitled')}[/cyan]")
                if chapter.get('summary'):
                    print(f"  {chapter['summary']}")
        else:
            print(f"[red]❌ Outline generation failed[/red]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Request failed: {e}[/]")

@app.command()
def agent(
    goal: str = typer.Argument(..., help="Agent goal"),
    max_steps: int = typer.Option(8, "--steps", help="Maximum steps"),
    model: str = typer.Option("claude-3-5-sonnet-20241022", "--model", help="Model to use")
):
    """Run reasoning agent"""
    request_data = {
        "goal": goal,
        "max_steps": max_steps,
        "model": model
    }
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running agent...", total=None)
            
            response = requests.post(f"{API}/agent/run", json=request_data, timeout=900)
            response.raise_for_status()
            data = response.json()
            
            progress.update(task, completed=True)
        
        print(f"\n[bold green]🤖 Agent Result:[/bold green] {data['result']}")
        
        # Show trace
        trace = data.get("trace", [])
        if trace:
            print(f"\n[bold blue]📋 Agent Trace:[/bold blue]")
            trace_table = Table(box=box.SIMPLE)
            trace_table.add_column("Step", justify="right")
            trace_table.add_column("Tool")
            trace_table.add_column("Observation", max_width=60)
            
            for i, item in enumerate(trace, 1):
                tool = item["action"]["tool"]
                obs = str(item["observation"])[:120].replace("\n", " ")
                if len(str(item["observation"])) > 120:
                    obs += "..."
                trace_table.add_row(str(i), tool, obs)
            
            print(trace_table)
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Request failed: {e}[/]")

@app.command()
def simple(
    topic: str = typer.Argument(..., help="Book topic"),
    chapters: int = typer.Option(8, "--chapters", help="Number of chapters"),
    words_per_chapter: int = typer.Option(2000, "--words-per-chapter", help="Words per chapter")
):
    """Run simple book generation workflow"""
    request_data = {
        "topic": topic,
        "chapters": chapters,
        "words_per_chapter": words_per_chapter
    }
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running simple workflow...", total=None)
            
            response = requests.post(f"{API}/simple-workflow", json=request_data, timeout=600)
            response.raise_for_status()
            data = response.json()
            
            progress.update(task, completed=True)
        
        if data.get("success"):
            print(f"[green]✅ Simple workflow completed![/green]")
            print(f"Result: {data.get('result', 'No details available')}")
        else:
            print(f"[red]❌ Simple workflow failed[/red]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Request failed: {e}[/]")

# RAG commands (only show if RAG is available)
@app.command()
def upload(
    file_path: str = typer.Argument(..., help="Path to file to upload")
):
    """Upload file for RAG processing"""
    if not check_rag_available():
        print("[red]❌ RAG functionality not available[/red]")
        return
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"[red]❌ File not found: {file_path}[/red]")
        return
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            response = requests.post(f"{API}/upload", files=files, timeout=300)
            response.raise_for_status()
            data = response.json()
        
        if data.get("success"):
            print(f"[green]✅ File uploaded successfully![/green]")
            print(f"📁 Filename: [cyan]{data['filename']}[/cyan]")
            print(f"📊 Size: [yellow]{data['size']:,} bytes[/yellow]")
            
            if data.get("ingestion_result"):
                result = data["ingestion_result"]
                print(f"📚 Processed: [green]{result.get('chunks_created', 0)} chunks[/green]")
        else:
            print(f"[red]❌ File upload failed[/red]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Upload failed: {e}[/]")

@app.command()
def rag_stats():
    """Show RAG collection statistics"""
    if not check_rag_available():
        print("[red]❌ RAG functionality not available[/red]")
        return
    
    try:
        response = requests.get(f"{API}/rag/stats")
        response.raise_for_status()
        data = response.json()
        
        print("[bold blue]📊 RAG Collection Statistics:[/bold blue]")
        for key, value in data.items():
            if not key.startswith('_'):
                print(f"  [cyan]{key.replace('_', ' ').title()}[/cyan]: [yellow]{value}[/yellow]")
                
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ RAG stats failed: {e}[/]")

@app.command()
def rag_query(
    query: str = typer.Argument(..., help="Search query"),
    k: int = typer.Option(6, "--top-k", help="Number of results")
):
    """Query RAG collection"""
    if not check_rag_available():
        print("[red]❌ RAG functionality not available[/red]")
        return
    
    try:
        response = requests.post(f"{API}/rag/query", data={"query": query, "k": k})
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            results = data["results"]
            print(f"\n[bold blue]🔍 RAG Query Results for: '{query}'[/bold blue]")
            
            for i, result in enumerate(results, 1):
                print(f"\n[cyan]Result {i}:[/cyan]")
                print(f"  [yellow]Text:[/yellow] {result['text'][:200]}...")
                print(f"  [yellow]Source:[/yellow] {result['source'].get('title', 'Unknown')}")
                print(f"  [yellow]Confidence:[/yellow] {result['confidence']}")
        else:
            print(f"[red]❌ RAG query failed[/red]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ RAG query failed: {e}[/]")

@app.command()
def rag_clear():
    """Clear RAG collection"""
    if not check_rag_available():
        print("[red]❌ RAG functionality not available[/red]")
        return
    
    confirm = typer.confirm("Are you sure you want to clear the RAG collection?")
    if not confirm:
        print("[yellow]❌ Operation cancelled[/yellow]")
        return
    
    try:
        response = requests.delete(f"{API}/rag/clear")
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print("[green]✅ RAG collection cleared![/green]")
        else:
            print(f"[red]❌ RAG clear failed[/red]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ RAG clear failed: {e}[/]")

if __name__ == "__main__":
    app() 