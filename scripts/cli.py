import json, requests, typer
from rich import print, box
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import os
from pathlib import Path

app = typer.Typer(help="Book Agent CLI")
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
        print("[yellow]Make sure the API server is running with: python -m backend.main[/]")

@app.command()
def styles():
    """List all available book styles"""
    try:
        response = requests.get(f"{API}/styles")
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[bold blue]📚 Available Book Styles[/bold blue]")
        print(f"Default style: [cyan]{data['default_style']}[/cyan]")
        
        # Create styles table
        table = Table(title="Book Styles", box=box.SIMPLE)
        table.add_column("Style", style="cyan")
        table.add_column("Description", style="yellow")
        
        for style_name, description in data['available_styles'].items():
            table.add_row(style_name.title(), description)
        
        print(table)
        
        print(f"\n[bold]🎨 Custom Style Options:[/bold]")
        custom_options = data['custom_style_options']
        print(f"  • Font Families: {', '.join(custom_options['font_families'])}")
        print(f"  • Line Heights: {', '.join(custom_options['line_heights'])}")
        print(f"  • Paragraph Spacing: {', '.join(custom_options['paragraph_spacings'])}")
        print(f"  • Header Spacing: {', '.join(custom_options['header_spacings'])}")
        print(f"  • Max Widths: {', '.join(custom_options['max_widths'])}")
        print(f"  • Color Schemes: {', '.join(custom_options['color_schemes'])}")
        
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Error getting styles: {e}[/]")

@app.command()
def status():
    """Get project status"""
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
        
        print(table)
        
        if data.get("chapters"):
            print("\n[bold]Chapters:[/]")
            for chapter in data["chapters"]:
                print(f"  • {chapter}")
                
    except requests.exceptions.RequestException as e:
        print(f"[red]Error getting status: {e}[/]")

@app.command()
def upload(file_path: str):
    """Upload a markdown source file"""
    try:
        if not os.path.exists(file_path):
            print(f"[red]✗ File not found: {file_path}[/]")
            return
            
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/markdown')}
            response = requests.post(f"{API}/upload-source", files=files, timeout=60)
            response.raise_for_status()
        
        data = response.json()
        print(f"[green]✓ File uploaded successfully[/]")
        print(f"Filename: {data['filename']}")
        print(f"Size: {data['file_size']} bytes")
        print(f"Path: {data['file_path']}")
        
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Upload failed: {e}[/]")

@app.command()
def generate_book(
    topic: str,
    target_audience: str = "general",
    style: str = "informative",
    target_pages: int = 50,
    source_file: str = None,
    book_style: str = "modern",
    font_family: str = None,
    line_height: str = None,
    paragraph_spacing: str = None,
    header_spacing: str = None,
    max_width: str = None,
    color_scheme: str = None
):
    """Generate a complete 50-page book with customizable styling"""
    try:
        print(f"\n[bold blue]🚀 Starting AI Book Generation[/bold blue]")
        print(f"📖 Topic: [cyan]{topic}[/cyan]")
        print(f"👥 Audience: [cyan]{target_audience}[/cyan]")
        print(f"📝 Style: [cyan]{style}[/cyan]")
        print(f"📄 Target pages: [cyan]{target_pages}[/cyan]")
        print(f"🎨 Book style: [cyan]{book_style}[/cyan]")
        
        # Prepare custom style if any custom options are provided
        custom_style = None
        if any([font_family, line_height, paragraph_spacing, header_spacing, max_width, color_scheme]):
            custom_style = {}
            if font_family:
                custom_style["font_family"] = font_family
            if line_height:
                custom_style["line_height"] = line_height
            if paragraph_spacing:
                custom_style["paragraph_spacing"] = paragraph_spacing
            if header_spacing:
                custom_style["header_spacing"] = header_spacing
            if max_width:
                custom_style["max_width"] = max_width
            if color_scheme:
                custom_style["color_scheme"] = color_scheme
            
            print(f"🎨 Custom style: [cyan]{custom_style}[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🤖 AI is generating your book...", total=None)
            
            payload = {
                "topic": topic,
                "target_audience": target_audience,
                "style": style,
                "target_pages": target_pages,
                "book_style": book_style
            }
            
            if source_file:
                payload["source_file_path"] = source_file
            
            if custom_style:
                payload["custom_style"] = custom_style
            
            response = requests.post(f"{API}/generate-book", json=payload, timeout=1800)
            response.raise_for_status()
            
            progress.update(task, description="[green]✅ Book generation completed!")
        
        data = response.json()
        
        if data.get("success"):
            print(f"\n[bold green]🎉 BOOK GENERATION SUCCESSFUL![/bold green]")
            
            # Display book info
            print(f"\n[bold]📚 Book Details:[/bold]")
            print(f"  • Title: [cyan]{data['book_title']}[/cyan]")
            print(f"  • Chapters: [cyan]{data['total_chapters']}[/cyan]")
            print(f"  • Estimated Pages: [cyan]{data['estimated_pages']}[/cyan]")
            print(f"  • Total Cost: [yellow]${data.get('total_cost', 0):.4f}[/yellow]")
            print(f"  • Style: [cyan]{data.get('book_style', 'modern')}[/cyan]")
            
            if data.get('custom_style'):
                print(f"  • Custom Style: [cyan]{data['custom_style']}[/cyan]")
            
            # Display files created
            print(f"\n[bold]📁 Files Created:[/bold]")
            for format_type, file_path in data['files_created'].items():
                if file_path:
                    file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
                    print(f"  • {format_type.upper()}: [green]{file_path}[/green] ({file_size:,} bytes)")
            
            # Display outline
            outline = data.get('outline', {})
            if outline:
                print(f"\n[bold blue]📋 Book Structure:[/bold blue]")
                print(f"Total estimated pages: [cyan]{outline.get('total_estimated_pages', target_pages)}[/cyan]")
                
                table = Table(title="Chapter Breakdown", box=box.SIMPLE)
                table.add_column("#", justify="right")
                table.add_column("Chapter", style="cyan")
                table.add_column("Pages", justify="right")
                table.add_column("Subtopics", style="yellow")
                
                for chapter in outline.get('chapters', []):
                    subtopics = ', '.join(chapter.get('subtopics', [])[:3])
                    if len(chapter.get('subtopics', [])) > 3:
                        subtopics += "..."
                    table.add_row(
                        str(chapter.get('number', '')),
                        chapter.get('title', ''),
                        str(chapter.get('estimated_pages', '')),
                        subtopics
                    )
                
                print(table)
            
            # Next steps
            print(f"\n[bold green]🎯 NEXT STEPS:[/bold green]")
            print(f"[bold]1. View your book:[/bold]")
            markdown_file = data['files_created'].get('markdown')
            if markdown_file:
                print(f"   • Open markdown: [cyan]open {markdown_file}[/cyan]")
                print(f"   • View in terminal: [cyan]cat {markdown_file}[/cyan]")
            
            html_file = data['files_created'].get('html')
            if html_file:
                print(f"   • Open HTML: [cyan]open {html_file}[/cyan]")
            
            print(f"\n[bold]2. Create additional formats:[/bold]")
            print(f"   • PDF: [cyan]pandoc {markdown_file} -o book.pdf[/cyan]")
            print(f"   • EPUB: [cyan]pandoc {markdown_file} -o book.epub[/cyan]")
            print(f"   • DOCX: [cyan]pandoc {markdown_file} -o book.docx[/cyan]")
            
            print(f"\n[bold]3. Try different styles:[/bold]")
            print(f"   • Academic: [cyan]python scripts/cli.py generate-book \"{topic}\" --book-style academic[/cyan]")
            print(f"   • Compact: [cyan]python scripts/cli.py generate-book \"{topic}\" --book-style compact[/cyan]")
            print(f"   • E-book: [cyan]python scripts/cli.py generate-book \"{topic}\" --book-style ebook[/cyan]")
            
            print(f"\n[bold]4. Custom styling:[/bold]")
            print(f"   • Custom font: [cyan]python scripts/cli.py generate-book \"{topic}\" --font-family \"Times New Roman\"[/cyan]")
            print(f"   • Custom spacing: [cyan]python scripts/cli.py generate-book \"{topic}\" --paragraph-spacing \"2em\"[/cyan]")
            
        else:
            print(f"[red]✗ Book generation failed[/]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Book generation failed: {e}[/]")

@app.command()
def ingest(path: str):
    """Ingest files into RAG system"""
    import subprocess
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Ingesting files...", total=None)
            subprocess.check_call(["python", "rag/ingest.py", path])
            progress.update(task, description="[green]Ingestion complete!")
        
        print("[green]✓ Files ingested successfully[/]")
    except subprocess.CalledProcessError as e:
        print(f"[red]✗ Ingestion failed: {e}[/]")

@app.command()
def outline(
    topic: str, 
    chapters: int = 10,
    words_per_chapter: int = 3500,
    audience: str = "General audience",
    tone: str = "Professional"
):
    """Generate book outline"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating outline...", total=None)
            
            response = requests.post(f"{API}/outline/generate", json={
                "topic": topic,
                "chapters": chapters,
                "words_per_chapter": words_per_chapter,
                "audience": audience,
                "tone": tone
            }, timeout=120)
            response.raise_for_status()
            
            progress.update(task, description="[green]Outline generated!")
        
        data = response.json()
        outline = data["outline"]
        
        # Display outline
        print(f"\n[bold blue]{outline['title']}[/bold blue]")
        print(f"[italic]{outline['description']}[/italic]")
        print(f"Audience: {outline['audience']} | Tone: {outline['tone']}")
        print(f"Target: {outline['total_target_words']:,} words across {len(outline['chapters'])} chapters\n")
        
        # Create chapters table
        table = Table(title="Book Outline", box=box.SIMPLE)
        table.add_column("#", justify="right")
        table.add_column("Chapter", style="cyan")
        table.add_column("Sections", justify="right")
        table.add_column("Words", justify="right")
        
        for i, chapter in enumerate(outline["chapters"], 1):
            sections = len(chapter.get("sections", []))
            words = chapter.get("target_words", 0)
            table.add_row(str(i), chapter["title"], str(sections), f"{words:,}")
        
        print(table)
        print(f"\n[green]✓ Outline saved to book/toc.yaml[/]")
        
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Outline generation failed: {e}[/]")

@app.command()
def agent(
    goal: str, 
    steps: int = 8, 
    model: str = "claude-3-5-haiku-20241022"
):
    """Run reasoning agent"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Agent working...", total=None)
            
            response = requests.post(f"{API}/agent/run", json={
                "goal": goal,
                "max_steps": steps,
                "model": model
            }, timeout=900)
            response.raise_for_status()
            
            progress.update(task, description="[green]Agent completed!")
        
        data = response.json()
        
        print(f"\n[bold green]Result:[/bold green] {data['result']}")
        
        # Display trace
        if data.get("trace"):
            print("\n[bold]Agent Trace:[/bold]")
            table = Table(box=box.SIMPLE)
            table.add_column("Step", justify="right", style="cyan")
            table.add_column("Tool", style="green")
            table.add_column("Observation", style="yellow")
            
            for item in data["trace"]:
                step = item.get("step", "?")
                tool = item["action"]["tool"]
                obs = str(item["observation"])[:100].replace("\n", " ")
                if len(str(item["observation"])) > 100:
                    obs += "..."
                table.add_row(str(step), tool, obs)
            
            print(table)
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Agent execution failed: {e}[/]")

@app.command()
def build(format: str = "html"):
    """Build book to specified format"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Building {format.upper()}...", total=None)
            
            response = requests.post(f"{API}/build", params={"format": format}, timeout=300)
            response.raise_for_status()
            
            progress.update(task, description=f"[green]{format.upper()} built successfully!")
        
        data = response.json()
        
        if data.get("success"):
            print(f"[green]✓ Book built successfully: {data['export']}[/]")
            print(f"Chapters included: {', '.join(data['chapters'])}")
        else:
            print(f"[red]✗ Build failed: {data.get('error', 'Unknown error')}[/]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Build failed: {e}[/]")

@app.command()
def retrieve(query: str, k: int = 5):
    """Retrieve facts from RAG system"""
    import subprocess
    try:
        result = subprocess.run(
            ["python", "rag/retrieve.py", query],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[red]✗ Retrieval failed: {e}[/]")

@app.command()
def create(
    title: str,
    chapters: int = 10,
    words_per_chapter: int = 3500,
    audience: str = "General audience",
    tone: str = "Professional"
):
    """Create a new book project"""
    try:
        # Create project structure
        import subprocess
        subprocess.check_call(["python", "-c", f"""
from backend import tools as T
result = T.create_project_structure('{title}')
print('Project created:', result['title'])
"""])
        
        print(f"[green]✓ Project '{title}' created[/]")
        print(f"Run 'book outline \"{title}\" --chapters {chapters}' to generate outline")
        
    except Exception as e:
        print(f"[red]✗ Project creation failed: {e}[/]")

@app.command()
def simple(
    topic: str,
    chapters: int = 5,
    words_per_chapter: int = 2000
):
    """Run simple workflow: outline -> write -> build"""
    try:
        goal = f"Create a complete book about '{topic}' with {chapters} chapters, {words_per_chapter} words each, and export to HTML"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running simple workflow...", total=None)
            
            response = requests.post(f"{API}/agent/run", json={
                "goal": goal,
                "max_steps": 15,
                "model": "claude-3-5-haiku-20241022"
            }, timeout=1200)
            response.raise_for_status()
            
            progress.update(task, description="[green]Workflow completed!")
        
        data = response.json()
        print(f"\n[bold green]Workflow Result:[/bold green] {data['result']}")
        
        if data.get("trace"):
            print(f"\n[bold]Completed {len(data['trace'])} steps[/bold]")
            
    except requests.exceptions.RequestException as e:
        print(f"[red]✗ Simple workflow failed: {e}[/]")

if __name__ == "__main__":
    app()
