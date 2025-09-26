"""
Book type definitions and cost estimation for the Book Creator system
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import math

@dataclass
class BookType:
    """Defines a book type with its specifications and cost estimates"""
    name: str
    description: str
    recommended_chapters: int
    words_per_chapter: int
    estimated_tokens_per_chapter: int
    estimated_pages: int
    target_audience: str
    complexity_level: str
    estimated_cost_usd: float
    estimated_time_minutes: int
    use_cases: List[str]
    
    @property
    def total_words(self) -> int:
        return self.recommended_chapters * self.words_per_chapter
    
    @property
    def total_tokens(self) -> int:
        return self.recommended_chapters * self.estimated_tokens_per_chapter
    
    @property
    def estimated_time_formatted(self) -> str:
        """Format estimated time in a human-readable way"""
        if self.estimated_time_minutes < 60:
            return f"{self.estimated_time_minutes}m"
        elif self.estimated_time_minutes < 120:
            hours = self.estimated_time_minutes / 60
            return f"{hours:.1f}h"
        else:
            hours = self.estimated_time_minutes // 60
            minutes = self.estimated_time_minutes % 60
            if minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {minutes}m"

# Book type definitions based on common educational and professional needs
BOOK_TYPES: Dict[str, BookType] = {
    "quick_guide": BookType(
        name="Quick Guide",
        description="Concise overview of key concepts",
        recommended_chapters=3,
        words_per_chapter=800,
        estimated_tokens_per_chapter=6000,
        estimated_pages=10,
        target_audience="Beginners",
        complexity_level="Basic",
        estimated_cost_usd=0.5,
        estimated_time_minutes=8,
        use_cases=["Quick references", "Concept introductions", "Executive summaries"]
    ),
    
    "tutorial": BookType(
        name="Tutorial",
        description="Step-by-step learning guide with examples",
        recommended_chapters=5,
        words_per_chapter=1200,
        estimated_tokens_per_chapter=8000,
        estimated_pages=24,
        target_audience="Beginners to Intermediate",
        complexity_level="Intermediate",
        estimated_cost_usd=0.8,
        estimated_time_minutes=15,
        use_cases=["Learning new skills", "Hands-on training", "Workshops"]
    ),
    
    "comprehensive": BookType(
        name="Comprehensive Guide",
        description="In-depth coverage with detailed explanations",
        recommended_chapters=8,
        words_per_chapter=2000,
        estimated_tokens_per_chapter=12000,
        estimated_pages=64,
        target_audience="Intermediate to Advanced",
        complexity_level="Advanced",
        estimated_cost_usd=1.5,
        estimated_time_minutes=35,
        use_cases=["Complete courses", "Professional development", "Academic study"]
    ),
    
    "textbook": BookType(
        name="University Textbook",
        description="Academic-level content with mathematical rigor",
        recommended_chapters=12,
        words_per_chapter=3000,
        estimated_tokens_per_chapter=18000,
        estimated_pages=144,
        target_audience="University students",
        complexity_level="Advanced",
        estimated_cost_usd=3.5,
        estimated_time_minutes=75,
        use_cases=["University courses", "Research reference", "Graduate studies"]
    ),
    
    "handbook": BookType(
        name="Professional Handbook",
        description="Practical reference for professionals",
        recommended_chapters=10,
        words_per_chapter=1800,
        estimated_tokens_per_chapter=10000,
        estimated_pages=72,
        target_audience="Professionals",
        complexity_level="Intermediate",
        estimated_cost_usd=2.0,
        estimated_time_minutes=45,
        use_cases=["Professional reference", "Industry best practices", "Technical documentation"]
    ),
    
    "manual": BookType(
        name="Technical Manual",
        description="Detailed implementation and procedures",
        recommended_chapters=15,
        words_per_chapter=2500,
        estimated_tokens_per_chapter=15000,
        estimated_pages=150,
        target_audience="Technical professionals",
        complexity_level="Advanced",
        estimated_cost_usd=4.5,
        estimated_time_minutes=90,
        use_cases=["Software documentation", "System administration", "Technical procedures"]
    ),
    
    "workbook": BookType(
        name="Interactive Workbook",
        description="Exercises and practical applications",
        recommended_chapters=6,
        words_per_chapter=1500,
        estimated_tokens_per_chapter=9000,
        estimated_pages=36,
        target_audience="All levels",
        complexity_level="Intermediate",
        estimated_cost_usd=1.2,
        estimated_time_minutes=22,
        use_cases=["Skill practice", "Training exercises", "Self-assessment"]
    ),
    
    "research": BookType(
        name="Research Compendium",
        description="Comprehensive research findings and analysis",
        recommended_chapters=20,
        words_per_chapter=4000,
        estimated_tokens_per_chapter=25000,
        estimated_pages=320,
        target_audience="Researchers and academics",
        complexity_level="Expert",
        estimated_cost_usd=8.0,
        estimated_time_minutes=150,
        use_cases=["Research publications", "Academic reference", "Literature reviews"]
    )
}

def calculate_cost_estimate(chapters: int, words_per_chapter: int, use_rag: bool = False) -> Dict[str, Any]:
    """
    Calculate estimated cost and time for a custom book configuration
    
    Args:
        chapters: Number of chapters
        words_per_chapter: Target words per chapter
        use_rag: Whether to use RAG enhancement
        
    Returns:
        Dictionary with cost and time breakdown
    """
    # Base cost estimates (rough calculations based on token usage)
    base_cost_per_1000_words = 0.02  # Approximate cost per 1000 words (10x increase)
    rag_multiplier = 1.3 if use_rag else 1.0
    
    total_words = chapters * words_per_chapter
    estimated_tokens = total_words * 6  # ~6 tokens per word average
    
    # Cost breakdown
    content_generation_cost = (total_words / 1000) * base_cost_per_1000_words
    enhancement_cost = content_generation_cost * 0.5  # For gap filling and improvements
    restructuring_cost = chapters * 0.01  # Per chapter introduction (10x increase)
    rag_cost = content_generation_cost * 0.3 if use_rag else 0
    
    total_cost = (content_generation_cost + enhancement_cost + restructuring_cost + rag_cost) * rag_multiplier
    
    # Time estimation (based on empirical data from the system)
    # Base time: ~3 minutes per chapter + 0.8 minutes per 1000 words
    base_time_per_chapter = 3  # minutes for chapter processing overhead
    time_per_1000_words = 0.8  # minutes per 1000 words of content generation
    rag_time_multiplier = 1.4 if use_rag else 1.0
    
    content_time = (total_words / 1000) * time_per_1000_words
    processing_time = chapters * base_time_per_chapter
    total_time = (content_time + processing_time) * rag_time_multiplier
    
    return {
        "total_words": total_words,
        "estimated_tokens": estimated_tokens,
        "estimated_pages": math.ceil(total_words / 250),  # ~250 words per page
        "estimated_time_minutes": math.ceil(total_time),
        "estimated_time_formatted": format_time_duration(math.ceil(total_time)),
        "cost_breakdown": {
            "content_generation": content_generation_cost,
            "enhancement": enhancement_cost,
            "restructuring": restructuring_cost,
            "rag_enhancement": rag_cost,
            "total": total_cost
        },
        "time_breakdown": {
            "content_generation": content_time,
            "processing_overhead": processing_time,
            "total": total_time
        },
        "estimated_cost_usd": round(total_cost, 3)
    }

def format_time_duration(minutes: int) -> str:
    """Format time duration in a human-readable way"""
    if minutes < 60:
        return f"{minutes}m"
    elif minutes < 120:
        hours = minutes / 60
        return f"{hours:.1f}h"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {mins}m"

def get_book_recommendations(target_pages: int = None, target_cost: float = None) -> List[str]:
    """
    Get book type recommendations based on constraints
    
    Args:
        target_pages: Maximum desired pages
        target_cost: Maximum desired cost in USD
        
    Returns:
        List of recommended book type keys
    """
    recommendations = []
    
    for key, book_type in BOOK_TYPES.items():
        if target_pages and book_type.estimated_pages > target_pages:
            continue
        if target_cost and book_type.estimated_cost_usd > target_cost:
            continue
        recommendations.append(key)
    
    return recommendations
