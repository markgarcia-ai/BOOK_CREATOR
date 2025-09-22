"""
Load prompts from external markdown files
"""
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"

def load_prompt(prompt_name: str) -> str:
    """Load a prompt from the prompts directory"""
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    return prompt_file.read_text(encoding='utf-8')

def get_planner_prompt() -> str:
    """Get the planner system prompt"""
    return load_prompt("planner")

def get_writer_prompt() -> str:
    """Get the writer system prompt"""
    return load_prompt("writer")

def get_editor_prompt() -> str:
    """Get the editor system prompt"""
    return load_prompt("editor")

def get_image_prompt() -> str:
    """Get the image generation prompt"""
    return load_prompt("image")

def get_agent_prompt() -> str:
    """Get the agent system prompt"""
    return load_prompt("agent")

# Cache for loaded prompts
_prompt_cache: Dict[str, str] = {}

def get_cached_prompt(prompt_name: str) -> str:
    """Get a cached prompt or load it if not cached"""
    if prompt_name not in _prompt_cache:
        _prompt_cache[prompt_name] = load_prompt(prompt_name)
    return _prompt_cache[prompt_name]
