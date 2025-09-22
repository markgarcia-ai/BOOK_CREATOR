import json
import time
from typing import Dict, List, Any, Tuple
from .llm import complete_json
from .settings import WRITER_MODEL
from .prompt_loader import get_agent_prompt
from . import tools as T
from rag.retrieve import fact_pack
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
    max_steps: int = 12
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
    context = {"goal": goal, "completed_tasks": []}
    
    for step in range(max_steps):
        # Prepare context for the agent
        recent_trace = trace[-3:] if len(trace) > 3 else trace
        
        user_prompt = f"""GOAL: {goal}

RECENT ACTIONS:
{json.dumps(recent_trace, indent=2) if recent_trace else "No recent actions"}

COMPLETED TASKS: {context.get('completed_tasks', [])}

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
            if tool in ["save_chapter", "build_book", "create_outline"]:
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

def execute_tool(tool: str, args: Dict[str, Any], context: Dict[str, Any], model: str) -> Dict[str, Any]:
    """Execute a tool and return the observation"""
    
    try:
        if tool == "retrieve_facts":
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
    
    return run_agent(goal, model, max_steps=15)
