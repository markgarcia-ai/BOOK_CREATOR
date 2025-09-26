import json, requests, typer
from rich import print, box
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import os
import sys
from pathlib import Path
from typing import Optional

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.book_types import BOOK_TYPES, calculate_cost_estimate, get_book_recommendations

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
    book_type: Optional[str] = typer.Option(None, "--book-type", help="Book type (quick_guide, tutorial, comprehensive, textbook, handbook, manual, workbook, research)"),
    chapters: int = typer.Option(8, "--chapters", help="Number of chapters"),
    words_per_chapter: int = typer.Option(2000, "--words-per-chapter", help="Words per chapter"),
    source_file: Optional[str] = typer.Option(None, "--source-file", help="Source file from uploads folder (e.g., 'ai_foundations.md')")
):
    """Run simple book generation workflow with book type selection"""
    
    # Validate and apply book type if provided
    selected_book_type = None
    if book_type:
        if book_type not in BOOK_TYPES:
            print(f"[red]❌ Invalid book type: {book_type}[/red]")
            print(f"[yellow]Available types: {', '.join(BOOK_TYPES.keys())}[/yellow]")
            return
        
        selected_book_type = BOOK_TYPES[book_type]
        print(f"[green]📚 Using book type: {selected_book_type.name}[/green]")
        print(f"[cyan]🎯 Target audience: {selected_book_type.target_audience}[/cyan]")
        print(f"[cyan]✍️  Writing style: {selected_book_type.writing_style}[/cyan]")
        
        # Apply book type defaults if user didn't override them
        if chapters == 8:  # Default value, user didn't specify
            chapters = selected_book_type.recommended_chapters
            print(f"[dim]📄 Using book type default chapters: {chapters}[/dim]")
        
        if words_per_chapter == 2000:  # Default value, user didn't specify
            words_per_chapter = selected_book_type.words_per_chapter
            print(f"[dim]📊 Using book type default words per chapter: {words_per_chapter:,}[/dim]")
    else:
        print("[yellow]💡 Tip: Use --book-type to generate content optimized for specific book types[/yellow]")
        print(f"[yellow]   Available: {', '.join(BOOK_TYPES.keys())}[/yellow]")
    
    # Check if source file exists and read it
    source_content = None
    if source_file:
        uploads_dir = Path("uploads")
        source_path = uploads_dir / source_file
        
        if source_path.exists():
            try:
                source_content = source_path.read_text(encoding='utf-8')
                print(f"[green]✓ Found source file: {source_file}[/green]")
                print(f"[cyan]📄 Content size: {len(source_content):,} characters[/cyan]")
            except Exception as e:
                print(f"[red]❌ Error reading source file: {e}[/red]")
                return
        else:
            print(f"[red]❌ Source file not found: {source_path}[/red]")
            print(f"[yellow]Available files in uploads:[/yellow]")
            if uploads_dir.exists():
                for file in uploads_dir.glob("*"):
                    if file.is_file():
                        print(f"  - {file.name}")
            else:
                print("  [dim]No uploads directory found[/dim]")
            return
    
    request_data = {
        "topic": topic,
        "chapters": chapters,
        "words_per_chapter": words_per_chapter
    }
    
    # Add book type information if provided
    if selected_book_type:
        request_data["book_type"] = book_type
        request_data["book_type_info"] = {
            "name": selected_book_type.name,
            "target_audience": selected_book_type.target_audience,
            "writing_style": selected_book_type.writing_style,
            "content_approach": selected_book_type.content_approach,
            "tone_description": selected_book_type.tone_description,
            "section_emphasis": selected_book_type.section_emphasis,
            "prompt_modifiers": selected_book_type.prompt_modifiers
        }
    
    # Add source content if provided
    if source_content:
        request_data["source_content"] = source_content
    
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

@app.command()
def books(
    filter_by: Optional[str] = typer.Option(None, "--filter", help="Filter by audience (beginners, intermediate, advanced, professionals)"),
    max_cost: Optional[float] = typer.Option(None, "--max-cost", help="Maximum cost in USD"),
    max_pages: Optional[int] = typer.Option(None, "--max-pages", help="Maximum pages"),
    custom: Optional[bool] = typer.Option(False, "--custom", help="Calculate cost for custom book"),
    wide: Optional[bool] = typer.Option(False, "--wide", help="Use wide table format for large terminals")
):
    """
    📚 Show available book types, specifications, and cost estimates
    """
    console.print("\n[bold blue]📚 Book Creator - Available Book Types[/bold blue]\n")
    
    # Get terminal width
    terminal_width = console.size.width
    is_wide_terminal = terminal_width >= 120 or wide
    
    if custom:
        # Interactive custom book calculator
        console.print("[bold yellow]Custom Book Calculator[/bold yellow]\n")
        
        chapters = typer.prompt("Number of chapters", type=int, default=5)
        words_per_chapter = typer.prompt("Words per chapter", type=int, default=1500)
        use_rag = typer.confirm("Use RAG enhancement?", default=False)
        
        estimate = calculate_cost_estimate(chapters, words_per_chapter, use_rag)
        
        # Custom book table
        custom_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        custom_table.add_column("Specification", style="cyan")
        custom_table.add_column("Value", style="green")
        
        custom_table.add_row("Chapters", str(chapters))
        custom_table.add_row("Words per Chapter", f"{words_per_chapter:,}")
        custom_table.add_row("Total Words", f"{estimate['total_words']:,}")
        custom_table.add_row("Estimated Tokens", f"{estimate['estimated_tokens']:,}")
        custom_table.add_row("Estimated Pages", str(estimate['estimated_pages']))
        custom_table.add_row("[bold]Estimated Time[/bold]", f"[bold orange3]{estimate['estimated_time_formatted']}[/bold orange3]")
        custom_table.add_row("RAG Enhancement", "Yes" if use_rag else "No")
        custom_table.add_row("[bold]Estimated Cost[/bold]", f"[bold green]${estimate['estimated_cost_usd']:.3f}[/bold green]")
        
        console.print(custom_table)
        console.print("\n[dim]💡 Tip: Use --filter, --max-cost, or --max-pages to find suitable predefined book types[/dim]")
        return
    
    # Create main book types table with responsive widths
    console.print(f"[dim]Terminal width: {terminal_width} columns[/dim]")
    
    if is_wide_terminal:
        # Wide format for large terminals
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED, expand=True)
        table.add_column("Book Type", style="cyan", width=22)
        table.add_column("Description", style="white", width=40)
        table.add_column("Chapters", justify="center", style="yellow", width=8)
        table.add_column("Words/Ch", justify="center", style="blue", width=10)
        table.add_column("Pages", justify="center", style="green", width=6)
        table.add_column("Time", justify="center", style="orange3", width=8)
        table.add_column("Audience", style="magenta", width=15)
        table.add_column("Cost", justify="right", style="bold green", width=10)
    else:
        # Compact format for smaller terminals
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE, expand=True)
        table.add_column("Type", style="cyan", width=14)
        table.add_column("Description", style="white", no_wrap=False)
        table.add_column("Ch", justify="center", style="yellow", width=3)
        table.add_column("Words", justify="center", style="blue", width=6)
        table.add_column("Pages", justify="center", style="green", width=5)
        table.add_column("Time", justify="center", style="orange3", width=6)
        table.add_column("Cost", justify="right", style="bold green", width=7)
    
    # Filter books if needed
    filtered_books = {}
    for key, book_type in BOOK_TYPES.items():
        # Apply filters
        if filter_by:
            audience_lower = book_type.target_audience.lower()
            if filter_by.lower() not in audience_lower:
                continue
        
        if max_cost and book_type.estimated_cost_usd > max_cost:
            continue
            
        if max_pages and book_type.estimated_pages > max_pages:
            continue
            
        filtered_books[key] = book_type
    
    # Add rows to table based on format
    for key, book_type in filtered_books.items():
        if is_wide_terminal:
            # Wide format with all columns
            table.add_row(
                book_type.name,
                book_type.description,
                str(book_type.recommended_chapters),
                f"{book_type.words_per_chapter:,}",
                str(book_type.estimated_pages),
                book_type.estimated_time_formatted,
                book_type.target_audience,
                f"${book_type.estimated_cost_usd:.3f}"
            )
        else:
            # Compact format with essential columns only
            # Truncate description for smaller terminals
            short_desc = book_type.description
            if len(short_desc) > 30:
                short_desc = short_desc[:27] + "..."
            
            table.add_row(
                book_type.name,
                short_desc,
                str(book_type.recommended_chapters),
                f"{book_type.words_per_chapter//1000}k" if book_type.words_per_chapter >= 1000 else str(book_type.words_per_chapter),
                str(book_type.estimated_pages),
                book_type.estimated_time_formatted,
                f"${book_type.estimated_cost_usd:.2f}"
            )
    
    console.print(table)
    
    # Show format tip for narrow terminals
    if not is_wide_terminal:
        console.print(f"\n[dim]💡 Terminal is {terminal_width} columns wide. Use --wide for full table or resize terminal for better view.[/dim]")
    
    # Show usage examples
    console.print("\n[bold yellow]📖 Usage Examples:[/bold yellow]")
    usage_table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
    usage_table.add_column("Command", style="green")
    usage_table.add_column("Description", style="white")
    
    usage_table.add_row(
        "python scripts/cli.py simple 'AI Guide' --book-type tutorial",
        "Create a tutorial-style book with optimized content"
    )
    usage_table.add_row(
        "python scripts/cli.py simple 'ML Handbook' --book-type handbook",
        "Create a professional handbook with best practices"
    )
    usage_table.add_row(
        "python scripts/cli.py simple 'Research Study' --book-type research",
        "Generate academic research compendium"
    )
    usage_table.add_row(
        "python scripts/cli.py books --filter beginners --max-cost 0.10",
        "Find beginner books under $0.10"
    )
    usage_table.add_row(
        "python scripts/cli.py books --custom",
        "Calculate cost for custom specifications"
    )
    
    console.print(usage_table)
    
    # Show cost and time breakdown info
    console.print(f"\n[bold blue]💰 Cost & Time Information:[/bold blue]")
    console.print("• Costs include content generation, enhancement, and restructuring")
    console.print("• Time estimates include content generation + processing overhead")
    console.print("• RAG enhancement adds ~30% to cost and ~40% to time")
    console.print("• Estimates based on current Claude API rates and system performance")
    console.print("• Actual costs and times may vary based on content complexity")
    
    if filtered_books:
        console.print(f"\n[green]✨ Showing {len(filtered_books)} book type(s)[/green]")
        if len(filtered_books) != len(BOOK_TYPES):
            console.print(f"[dim]({len(BOOK_TYPES) - len(filtered_books)} filtered out)[/dim]")
    else:
        console.print("\n[yellow]⚠️ No book types match your filters[/yellow]")

if __name__ == "__main__":
    app() 