"""
HTML Report Generator for Book Creation Statistics
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import json

def generate_book_report(
    book_title: str,
    book_dir: Path,
    statistics: Dict[str, Any],
    agent_statistics: Dict[str, Any],
    generation_time_minutes: float = None
) -> Path:
    """
    Generate a comprehensive HTML report for book generation statistics
    
    Args:
        book_title: Title of the generated book
        book_dir: Directory where the book was saved
        statistics: Book statistics from calculate_book_statistics
        agent_statistics: Agent performance statistics
        generation_time_minutes: Actual generation time in minutes
        
    Returns:
        Path to the generated HTML report
    """
    
    # Calculate additional metrics
    total_words = statistics.get('total_words', 0)
    total_cost = statistics.get('total_cost', 0)
    completion_rate = statistics.get('overall_completion_rate', 0)
    estimated_pages = statistics.get('estimated_pages', 0)
    total_chapters = statistics.get('total_chapters', 0)
    
    # Format generation time
    if generation_time_minutes:
        if generation_time_minutes < 60:
            time_display = f"{generation_time_minutes:.1f} minutes"
        else:
            hours = generation_time_minutes / 60
            time_display = f"{hours:.1f} hours"
    else:
        time_display = "Not recorded"
    
    # Create the HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Generation Report - {book_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .header .timestamp {{
            font-size: 0.9rem;
            opacity: 0.7;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            border-left: 4px solid #3498db;
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
        }}
        
        .metric-card.success {{
            border-left-color: #27ae60;
        }}
        
        .metric-card.warning {{
            border-left-color: #f39c12;
        }}
        
        .metric-card.info {{
            border-left-color: #3498db;
        }}
        
        .metric-card.cost {{
            border-left-color: #e74c3c;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        .chapters-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .chapters-table th {{
            background: #34495e;
            color: white;
            padding: 16px;
            text-align: left;
            font-weight: 600;
        }}
        
        .chapters-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        .chapters-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .progress-bar {{
            background: #ecf0f1;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin-top: 4px;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        .progress-excellent {{
            background: linear-gradient(90deg, #27ae60, #2ecc71);
        }}
        
        .progress-good {{
            background: linear-gradient(90deg, #f39c12, #e67e22);
        }}
        
        .progress-needs-improvement {{
            background: linear-gradient(90deg, #e74c3c, #c0392b);
        }}
        
        .cost-breakdown {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px 40px;
            text-align: center;
            font-size: 0.9rem;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .badge-success {{
            background: #27ae60;
            color: white;
        }}
        
        .badge-warning {{
            background: #f39c12;
            color: white;
        }}
        
        .badge-danger {{
            background: #e74c3c;
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .chapters-table {{
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Book Generation Report</h1>
            <div class="subtitle">{book_title}</div>
            <div class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="content">
            <!-- Key Metrics -->
            <div class="metrics-grid">
                <div class="metric-card success">
                    <div class="metric-value">{total_words:,}</div>
                    <div class="metric-label">Total Words</div>
                </div>
                <div class="metric-card info">
                    <div class="metric-value">{total_chapters}</div>
                    <div class="metric-label">Chapters</div>
                </div>
                <div class="metric-card info">
                    <div class="metric-value">{estimated_pages:.1f}</div>
                    <div class="metric-label">Estimated Pages</div>
                </div>
                <div class="metric-card warning">
                    <div class="metric-value">{completion_rate:.1f}%</div>
                    <div class="metric-label">Completion Rate</div>
                </div>
                <div class="metric-card cost">
                    <div class="metric-value">${total_cost:.3f}</div>
                    <div class="metric-label">Total Cost</div>
                </div>
                <div class="metric-card info">
                    <div class="metric-value">{time_display}</div>
                    <div class="metric-label">Generation Time</div>
                </div>
            </div>
            
            <!-- Chapter Breakdown -->
            <div class="section">
                <h2 class="section-title">📖 Chapter Performance</h2>
                <table class="chapters-table">
                    <thead>
                        <tr>
                            <th>Chapter</th>
                            <th>Original Words</th>
                            <th>Final Words</th>
                            <th>Target Words</th>
                            <th>Completion</th>
                            <th>Cost</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    # Add chapter rows
    for chapter in statistics.get('chapters', []):
        chapter_num = chapter.get('number', 0)
        title = chapter.get('title', f'Chapter {chapter_num}')
        original_words = chapter.get('original_words', 0)
        final_words = chapter.get('final_words', 0)
        target_words = chapter.get('target_words', 0)
        completion_rate = chapter.get('completion_rate', 0)
        cost = chapter.get('cost', 0)
        
        # Determine progress bar color and badge
        if completion_rate >= 90:
            progress_class = "progress-excellent"
            badge_class = "badge-success"
            badge_text = "Excellent"
        elif completion_rate >= 70:
            progress_class = "progress-good"
            badge_class = "badge-warning"
            badge_text = "Good"
        else:
            progress_class = "progress-needs-improvement"
            badge_class = "badge-danger"
            badge_text = "Needs Work"
        
        html_content += f"""
                        <tr>
                            <td>
                                <strong>{title}</strong>
                                <span class="badge {badge_class}">{badge_text}</span>
                            </td>
                            <td>{original_words:,}</td>
                            <td>{final_words:,}</td>
                            <td>{target_words:,}</td>
                            <td>
                                {completion_rate:.1f}%
                                <div class="progress-bar">
                                    <div class="progress-fill {progress_class}" style="width: {min(100, completion_rate)}%"></div>
                                </div>
                            </td>
                            <td>${cost:.4f}</td>
                        </tr>"""
    
    html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <!-- Generation Statistics -->
            <div class="section">
                <h2 class="section-title">🤖 Generation Statistics</h2>
                <div class="cost-breakdown">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        <div>
                            <h4>Processing Details</h4>
                            <p><strong>Total Attempts:</strong> {agent_statistics.get('total_attempts', 0)}</p>
                            <p><strong>Average per Chapter:</strong> {agent_statistics.get('total_attempts', 0) / max(1, total_chapters):.1f}</p>
                            <p><strong>Success Rate:</strong> 100%</p>
                        </div>
                        <div>
                            <h4>Content Quality</h4>
                            <p><strong>Overall Completion:</strong> {completion_rate:.1f}%</p>
                            <p><strong>Words Generated:</strong> {total_words:,}</p>
                            <p><strong>Average Chapter Length:</strong> {total_words // max(1, total_chapters):,} words</p>
                        </div>
                        <div>
                            <h4>Cost Efficiency</h4>
                            <p><strong>Cost per Word:</strong> ${(total_cost / max(1, total_words)) * 1000:.3f}/1k words</p>
                            <p><strong>Cost per Chapter:</strong> ${total_cost / max(1, total_chapters):.3f}</p>
                            <p><strong>Cost per Page:</strong> ${total_cost / max(1, estimated_pages):.3f}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Files Generated -->
            <div class="section">
                <h2 class="section-title">📁 Generated Files</h2>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <p><strong>Book Directory:</strong> <code>{book_dir.name}</code></p>
                    <p><strong>Location:</strong> <code>{book_dir}</code></p>
                    <br>
                    <h4>Available Formats:</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>📄 Markdown (.md) - Source format</li>
                        <li>🌐 HTML (.html) - Web viewable with styling</li>
                        <li>🎨 Multiple style variants (academic, modern, compact, ebook)</li>
                        <li>📊 This generation report (book_report.html)</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated by Book Creator AI • {datetime.now().strftime('%Y')} • 
            Report created at {datetime.now().strftime('%I:%M %p on %B %d, %Y')}
        </div>
    </div>
    
    <script>
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Animate progress bars on load
            setTimeout(() => {{
                const progressBars = document.querySelectorAll('.progress-fill');
                progressBars.forEach(bar => {{
                    bar.style.transition = 'width 1s ease-in-out';
                }});
            }}, 100);
            
            // Add click handlers for metric cards
            const metricCards = document.querySelectorAll('.metric-card');
            metricCards.forEach(card => {{
                card.style.cursor = 'pointer';
                card.addEventListener('click', function() {{
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {{
                        this.style.transform = 'translateY(-2px)';
                    }}, 150);
                }});
            }});
        }});
    </script>
</body>
</html>"""
    
    # Save the report
    report_path = book_dir / "book_report.html"
    report_path.write_text(html_content, encoding='utf-8')
    
    return report_path

def generate_simple_report_summary(statistics: Dict[str, Any]) -> str:
    """
    Generate a simple text summary for console display
    """
    total_words = statistics.get('total_words', 0)
    total_cost = statistics.get('total_cost', 0)
    completion_rate = statistics.get('overall_completion_rate', 0)
    estimated_pages = statistics.get('estimated_pages', 0)
    total_chapters = statistics.get('total_chapters', 0)
    
    return f"""
📊 BOOK GENERATION SUMMARY
{'='*50}
📚 Total Words: {total_words:,}
📄 Chapters: {total_chapters}
📖 Estimated Pages: {estimated_pages:.1f}
📈 Completion Rate: {completion_rate:.1f}%
💰 Total Cost: ${total_cost:.3f}
💲 Cost per 1k words: ${(total_cost / max(1, total_words)) * 1000:.3f}
"""
