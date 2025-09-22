import json
import time
from typing import Dict, List, Any, Tuple
from .llm import complete_json, chat
from .settings import WRITER_MODEL
from .prompt_loader import get_agent_prompt
from . import tools as T
from rag.retrieve import fact_pack, get_collection_stats
from .writer import write_section, write_chapter
from .planner import generate_outline, validate_outline

# Get agent system prompt from external file
AGENT_SYSTEM = get_agent_prompt()

AGENT_SCHEMA = {
    "type": "object",
    "properties": {
        "tool": {"type": "string"},
        "args": {"type": "object"},
        "reasoning": {"type": "string"}
    },
    "required": ["tool", "args", "reasoning"]
}

def run_agent(
    goal: str, 
    model: str = WRITER_MODEL, 
    max_steps: int = 15
) -> Tuple[List[Dict], str]:
    """
    Run the reasoning agent to accomplish a goal
    
    Args:
        goal: The goal to accomplish
        model: LLM model to use
        max_steps: Maximum number of steps
    
    Returns:
        (trace, final_result)
    """
    
    trace: List[Dict] = []
    context = {"goal": goal, "completed_tasks": [], "rag_content_summary": None}
    
    for step in range(max_steps):
        # Prepare context for the agent
        recent_trace = trace[-3:] if len(trace) > 3 else trace
        
        user_prompt = f"""GOAL: {goal}

RECENT ACTIONS:
{json.dumps(recent_trace, indent=2) if recent_trace else "No recent actions"}

COMPLETED TASKS: {context.get('completed_tasks', [])}

RAG CONTENT SUMMARY: {context.get('rag_content_summary', 'Not analyzed yet')}

What is the next best action to accomplish the goal? Provide your reasoning and choose the appropriate tool with arguments."""

        try:
            plan_result, plan_metadata = complete_json(
                model=model,
                system=AGENT_SYSTEM,
                user=user_prompt,
                schema_hint=json.dumps(AGENT_SCHEMA, indent=2)
            )
            
            tool = plan_result["tool"]
            args = plan_result.get("args", {})
            reasoning = plan_result.get("reasoning", "")
            
            # Execute the tool
            obs = execute_tool(tool, args, context, model)
            
            # Update context based on tool results
            if tool == "analyze_rag_content" and "summary" in obs:
                context["rag_content_summary"] = obs["summary"]
            
            # Record the action and observation
            trace.append({
                "step": step + 1,
                "action": plan_result,
                "observation": obs,
                "metadata": plan_metadata
            })
            
            # Update context
            if tool == "finish":
                return trace, args.get("summary", "Task completed")
            
            # Track completed tasks
            if tool in ["save_chapter", "build_book", "create_outline", "analyze_rag_content", "generate_content_summary"]:
                context["completed_tasks"].append(f"{tool}: {args}")
            
        except Exception as e:
            error_obs = {"error": str(e), "step": step + 1}
            trace.append({
                "step": step + 1,
                "action": {"tool": "error", "args": {}, "reasoning": "Error occurred"},
                "observation": error_obs
            })
            
            if step > 2:  # Don't fail immediately
                return trace, f"Error after {step + 1} steps: {str(e)}"
    
    return trace, "Maximum steps reached"

def analyze_rag_content(model: str, sample_size: int = 10) -> Dict[str, Any]:
    """
    Analyze the RAG database content to understand what's available
    
    Args:
        model: LLM model to use
        sample_size: Number of documents to sample for analysis
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Get RAG collection statistics
        stats = get_collection_stats()
        
        if stats.get("status") != "active" or stats.get("document_count", 0) == 0:
            return {
                "status": "no_content",
                "message": "No content found in RAG database",
                "stats": stats
            }
        
        # Sample some content from different queries
        sample_queries = [
            "machine learning", "artificial intelligence", "data science", 
            "algorithms", "models", "training", "evaluation", "deployment"
        ]
        
        sampled_content = {}
        content_themes = []
        
        for query in sample_queries:
            facts = fact_pack(query, k=3)  # Get top 3 for each query
            if facts:
                sampled_content[query] = facts
                for fact in facts:
                    content_themes.append(fact["text"][:200])  # First 200 chars
        
        # Use LLM to analyze the sampled content
        analysis_prompt = f"""Analyze the following content samples from a RAG database and provide a comprehensive summary:

CONTENT SAMPLES:
{json.dumps(sampled_content, indent=2)}

Please provide:
1. Main topics and themes covered
2. Content quality and depth assessment
3. Suggested book structure based on available content
4. Key subject areas that are well-covered
5. Any gaps or limitations in the content

Return a detailed analysis that would help in planning a book."""

        analysis_result, metadata = chat(
            model=model,
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=2000
        )
        
        return {
            "status": "analyzed",
            "stats": stats,
            "sampled_content": sampled_content,
            "analysis": analysis_result,
            "summary": analysis_result[:500] + "..." if len(analysis_result) > 500 else analysis_result,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stats": {"error": "Could not retrieve stats"}
        }

def generate_content_summary(model: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a markdown summary document of RAG content for agent understanding
    
    Args:
        model: LLM model to use
        analysis_data: Results from analyze_rag_content
    
    Returns:
        Dictionary with markdown summary
    """
    try:
        if analysis_data.get("status") != "analyzed":
            return {
                "status": "error",
                "error": "Analysis data not available or incomplete"
            }
        
        # Create prompt for generating markdown summary
        summary_prompt = f"""Based on the following RAG content analysis, create a comprehensive markdown summary document that an AI agent can use to understand the available content for book creation:

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}

Create a markdown document with the following structure:
# RAG Content Summary

## Overview
- Brief description of the content scope
- Total documents and coverage

## Main Topics
- List of primary topics with descriptions
- Coverage depth for each topic

## Content Quality Assessment
- Quality indicators
- Reliability assessment
- Source diversity

## Recommended Book Structure
- Suggested chapters based on available content
- Content gaps to be aware of
- Best-covered subject areas

## Content Samples
- Representative examples of the content
- Key concepts and themes

## Usage Recommendations
- How to best leverage this content for book creation
- Query strategies for different topics
- Limitations to consider

Make this summary actionable for an AI agent planning and writing a book."""

        summary_result, metadata = chat(
            model=model,
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=3000
        )
        
        # Save the summary as a markdown file
        summary_file_result = T.write_file("rag_content_summary.md", summary_result)
        
        return {
            "status": "generated",
            "markdown": summary_result,
            "file_saved": summary_file_result,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def explore_rag_sources(model: str, max_sources: int = 5) -> Dict[str, Any]:
    """
    Explore different sources in the RAG database
    
    Args:
        model: LLM model to use
        max_sources: Maximum number of sources to explore
    
    Returns:
        Dictionary with source exploration results
    """
    try:
        stats = get_collection_stats()
        sources = stats.get("sources", {})
        
        if not sources:
            return {
                "status": "no_sources",
                "message": "No sources found in RAG database"
            }
        
        source_analysis = {}
        
        # Analyze each source
        for source_name, doc_count in list(sources.items())[:max_sources]:
            # Get sample content from this source
            facts = fact_pack(f"source:{source_name}", k=5)
            
            if facts:
                source_analysis[source_name] = {
                    "document_count": doc_count,
                    "sample_content": facts[:3],  # Top 3 most relevant
                    "topics_covered": [fact["text"][:100] for fact in facts[:3]]
                }
        
        return {
            "status": "explored",
            "total_sources": len(sources),
            "sources_analyzed": len(source_analysis),
            "source_details": source_analysis,
            "all_sources": sources
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def execute_tool(tool: str, args: Dict[str, Any], context: Dict[str, Any], model: str) -> Dict[str, Any]:
    """Execute a tool and return the observation"""
    
    try:
        # PHASE 1: New RAG Analysis Tools
        if tool == "analyze_rag_content":
            sample_size = args.get("sample_size", 10)
            result = analyze_rag_content(model, sample_size)
            return result
        
        elif tool == "generate_content_summary":
            # Use analysis from context or perform new analysis
            analysis_data = context.get("last_analysis")
            if not analysis_data:
                # Perform analysis first
                analysis_data = analyze_rag_content(model)
            result = generate_content_summary(model, analysis_data)
            return result
        
        elif tool == "explore_rag_sources":
            max_sources = args.get("max_sources", 5)
            result = explore_rag_sources(model, max_sources)
            return result
        
        elif tool == "get_rag_statistics":
            stats = get_collection_stats()
            return stats
        
        # Existing tools
        elif tool == "retrieve_facts":
            query = args.get("query", context.get("goal", ""))
            k = args.get("k", 6)
            facts = fact_pack(query, k)
            return {"facts": facts, "count": len(facts)}
        
        elif tool == "write_section":
            brief = args.get("brief", {
                "topic": "General section",
                "target_words": 1200,
                "audience": "General audience",
                "tone": "Professional"
            })
            facts = args.get("facts", [])
            content, metadata = write_section(model, brief, facts)
            return {"markdown": content, "metadata": metadata}
        
        elif tool == "write_chapter":
            chapter_brief = args.get("chapter_brief", {
                "title": "Chapter",
                "audience": "General audience",
                "tone": "Professional"
            })
            sections = args.get("sections", [])
            facts = args.get("facts", [])
            content, metadata = write_chapter(model, chapter_brief, sections, facts)
            return {"markdown": content, "metadata": metadata}
        
        elif tool == "save_chapter":
            rel_path = args.get("path", "chapters/auto.md")
            content = args.get("markdown", "")
            result = T.write_file(rel_path, content)
            return result
        
        elif tool == "build_book":
            fmt = args.get("format", "pdf")
            result = T.build_book(fmt)
            return result
        
        elif tool == "get_status":
            status = T.get_project_status()
            return status
        
        elif tool == "create_outline":
            topic = args.get("topic", "General topic")
            chapters = args.get("chapters", 10)
            words_per_chapter = args.get("words_per_chapter", 3500)
            audience = args.get("audience", "General audience")
            tone = args.get("tone", "Professional")
            
            outline, metadata = generate_outline(
                model, topic, chapters, words_per_chapter, audience, tone
            )
            
            # Save outline to file
            outline_content = json.dumps(outline, indent=2)
            T.write_file("toc.yaml", outline_content)
            
            return {"outline": outline, "metadata": metadata, "saved": True}
        
        elif tool == "finish":
            return {"done": True, "summary": args.get("summary", "Task completed")}
        
        else:
            return {"error": f"Unknown tool: {tool}"}
    
    except Exception as e:
        return {"error": str(e), "tool": tool, "args": args}

def run_simple_workflow(
    topic: str,
    chapters: int = 5,
    words_per_chapter: int = 2000,
    model: str = WRITER_MODEL
) -> Tuple[List[Dict], str]:
    """
    Run a simple workflow: create outline -> write chapters -> build book
    
    Args:
        topic: Book topic
        chapters: Number of chapters
        words_per_chapter: Words per chapter
        model: LLM model to use
    
    Returns:
        (trace, result)
    """
    
    goal = f"Create a complete book about '{topic}' with {chapters} chapters, {words_per_chapter} words each, and export to PDF"
    
    return run_agent(goal, model, max_steps=20)

