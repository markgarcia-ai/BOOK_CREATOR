import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022")
WRITER_MODEL = os.getenv("WRITER_MODEL", "claude-3-5-sonnet-20241022")
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "claude-3-5-sonnet-20241022")

# Cost Tracking
MAX_COST_PER_PROJECT = float(os.getenv("MAX_COST_PER_PROJECT", "50.00"))
MAX_TOKENS_PER_SECTION = int(os.getenv("MAX_TOKENS_PER_SECTION", "8000"))

# Paths
ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
CHAPTERS = BOOK / "chapters"
ASSETS = BOOK / "assets" / "img"
EXPORTS = ROOT / "exports"
DATA = ROOT / "data"
LOGS = ROOT / "logs"

# Ensure directories exist
for path in [BOOK, CHAPTERS, ASSETS, EXPORTS, DATA, LOGS]:
    path.mkdir(parents=True, exist_ok=True)

# Cost tracking (rough estimates for Claude)
COST_PER_INPUT_TOKEN = 0.03 / 1000  # $0.03 per 1K input tokens (10x increase)
COST_PER_OUTPUT_TOKEN = 0.15 / 1000  # $0.15 per 1K output tokens (10x increase)
