# Book Agent CLI — Project Checklist ✅

A terminal-driven **book studio** that uses **AI agents + RAG** to plan, write, fact-check, illustrate, and **compile** a book to **PDF/EPUB/DOCX** — all from the command line.

> **Progress legend:** `[ ] todo` · `[~] in progress` · `[x] done`

---

## 0) Project Bootstrap
- [ ] Initialize repo (`git init`, `.gitignore`, `README.md`)
- [ ] Python 3.11 virtualenv + `requirements.txt`
- [ ] Create folders: `backend/`, `rag/`, `prompts/`, `scripts/`, `book/`, `exports/`, `data/uploads/`
- [ ] `.env` with API keys; add `.env.example`
- [ ] **Makefile** targets: `dev`, `build`, `outline`, `ingest`, `clean`
- [ ] Optional: `Dockerfile` for reproducible runs

---

## 1) Planner & Outline (Spec as Contract)
- [ ] CLI: `book create --title --chapters --wpc --tone --audience`
- [ ] Planner agent produces **ToC** with chapter/section **slugs** and **targets**
- [ ] Save canonical plan → `book/toc.yaml`
- [ ] Define **planner schema** (chapters, sections, images per section)
- [ ] Unit test: outline contains required slugs, no duplicates

**Planner output schema (must implement)**
```json
{
  "chapters": [
    {
      "slug": "intro",
      "title": "Introduction",
      "target_words": 3000,
      "sections": [{"slug":"background","title":"Background","target_words":1200}],
      "images": [{"slug":"system-arch","prompt":"...","caption":"..."}]
    }
  ]
}
```

---

## 2) RAG — Ingestion & Retrieval
- [ ] CLI: `book ingest <path|url>` stores raw files under `data/uploads/`
- [ ] Chunking policy (≈800–1200 tokens, ~15% overlap)
- [ ] Embeddings (e.g., `sentence-transformers/all-mpnet-base-v2` or API) ✅ normalize & store metadata
- [ ] Vector DB (Chroma/pgvector) persisted under `rag/db/`
- [ ] Retrieval returns **fact packs** (top‑k) with source metadata + confidence
- [ ] Command: `book retrieve --q "query" --k 8` (for debugging)

**Fact pack item (RAG → Writer)**
```json
{
  "text": "quoted or summarized snippet...",
  "citeKey": "doe2022",
  "source": {"title":"Paper/Doc","url":"https://...","page":12},
  "confidence": 0.82
}
```

---

## 3) Drafting (Writer Agent)
- [ ] Generate per‑section Markdown with:
  - [ ] Headings (`##`, `###`) and clear structure
  - [ ] In‑text citations `[@citeKey]` for non‑obvious claims
  - [ ] Figure placeholders `{{FIG:slug:"caption"}}`
  - [ ] Ending **Summary** + **Key Takeaways**
- [ ] Token‑aware: keep each section < ~2k words (8k token loops)
- [ ] Idempotent writes with hashing (skip if identical)
- [ ] CLI: `book draft chapter <slug>|all`

**Writer rules (hard)**
- Use only provided **fact packs** for claims; if missing → insert `[[NEEDS_SOURCE]]`
- Never leave unresolved placeholders when finalizing

---

## 4) Images (Generation / Fetching)
- [ ] Image agent resolves all `{{FIG:...}}` → `book/assets/img/<slug>.png`
- [ ] Store **alt**, **caption**, **license**, **source_url** in metadata
- [ ] Option: thumbnail preview → approve → upscale
- [ ] CLI: `book images resolve <slug>|all`

**Image spec**
```json
{"slug":"system-arch","prompt":"...","alt":"...","caption":"...","license":"...","source_url":null}
```

---

## 5) Editor & Quality Control (QC)
- [ ] Lints: `[[NEEDS_SOURCE]]`, missing figures, missing citations, orphan refs
- [ ] Style checks: reading level, passive voice, duplicate paragraphs
- [ ] CLI: `book qc run|show`
- [ ] Block **export** if blocking issues remain

**QC report**
```json
{"blocking": true, "issues": [{"type":"missing_source","where":"ch1:sec2","message":"Claim lacks citation"}]}
```

---

## 6) Citations & Bibliography
- [ ] Maintain `book/assets/bib.json` (CSL JSON)
- [ ] Include CSL style (e.g., `book/assets/styles/ieee.csl`)
- [ ] Ensure all `[@key]` resolve; generate reference list
- [ ] CLI helper: `book cite add|list|check` (optional)

---

## 7) Build & Export
- [ ] Pandoc command with `--citeproc` and resource path to `book/`
- [ ] PDF engine `xelatex` + `book/assets/styles/template.tex`
- [ ] `book build --format pdf|epub|docx` → artifacts in `exports/`
- [ ] Validate build: figures numbered, citations resolved, TOC present

---

## 8) CLI UX (Terminal Frontend)
- [ ] Typer + Rich: colored statuses, progress bars, tables
- [ ] Commands:
  - [ ] `book health`
  - [ ] `book create …`
  - [ ] `book outline generate|show`
  - [ ] `book ingest <path|url>`
  - [ ] `book retrieve --q "..." --k 8`
  - [ ] `book draft chapter <slug>|all`
  - [ ] `book images resolve <slug>|all`
  - [ ] `book qc run|show`
  - [ ] `book build --format pdf|epub|docx`
  - [ ] `book resume`
  - [ ] `book cost show --by chapter|section`

---

## 9) Costs, Tokens, & Limits
- [ ] Track tokens_in/out by section and totals
- [ ] Track embedding tokens + image count
- [ ] Estimate $ using provider prices (Cin/Cout/Cemb/Cimg)
- [ ] Project caps: stop generation if limits exceeded
- [ ] Print a cost summary at end of build

---

## 10) Reliability & Ops
- [ ] Safe resume after interruptions (chapter/section job model)
- [ ] Exponential backoff & retries on API/rate limits
- [ ] Content hashing to avoid redundant writes
- [ ] Logs per section → `logs/` with prompt hashes & model versions

---

## 11) Security & Licensing
- [ ] Never commit `.env` (keys in env vars only)
- [ ] Respect third‑party content licenses; store attribution for images
- [ ] Optional S3/GCS for assets & exports (later); local by default

---

## 12) Tests & QA
- [ ] Smoke test: `book health`, `book create`, one chapter draft, build PDF
- [ ] Unit tests for planners, chunkers, retrieval, writer schema
- [ ] QC tests: ensure build fails on `[[NEEDS_SOURCE]]` or broken refs
- [ ] Golden file tests for Pandoc output metadata

---

## 13) Acceptance Criteria (MVP)
- [ ] Create a project from CLI and generate ToC with slugs and targets
- [ ] Ingest ≥3 sources; retrieval returns **fact packs**
- [ ] Draft **two chapters** with citations and ≥1 figure each
- [ ] QC flags missing sources and blocks export until resolved
- [ ] Build **PDF** with numbered figures and references
- [ ] Show cost & token report at end of run

---

## 14) Stretch Goals (Phase 2+)
- [ ] EPUB/DOCX parity with PDF styling
- [ ] Versioning + diffs per chapter
- [ ] “Rewrite as …” presets (simplify/expand/tone)
- [ ] Multi‑model routing (value model vs frontier polish)
- [ ] Parallel chapter jobs (RQ/Celery + Redis)
- [ ] Provenance report (sources, image licenses) export

---

## 15) Agentic AI (Reasoning Agent + Tools)

This section implements a **reasoning agent** that plans actions and calls tools (RAG, writer, file ops, build) in a **think–act–observe** loop. It enables one command like:

```bash
python scripts/cli.py agent --goal "Draft Chapter 1 from the outline using RAG and export PDF"
```

### 15.1 Tools (backend/tools.py)

```python
# backend/tools.py
from pathlib import Path
import subprocess, json
BOOK = Path(__file__).resolve().parents[1] / "book"
CHAPTERS = BOOK / "chapters"
ASSETS = BOOK / "assets" / "img"
EXPORTS = Path(__file__).resolve().parents[1] / "exports"

def write_file(relpath: str, text: str) -> dict:
    p = (BOOK / relpath).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    before = p.read_text() if p.exists() else None
    p.write_text(text)
    return {"path": str(p), "bytes": len(text.encode()), "updated": before != text}

def build_book(fmt: str = "pdf") -> dict:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    out = EXPORTS / f"book.{fmt}"
    md_files = sorted((CHAPTERS).glob("*.md"))
    cmd = [
        "pandoc", "-s", "--from", "markdown+footnotes+raw_tex",
        "--citeproc", "--metadata-file", str(BOOK/"config.yml"),
        "-o", str(out), *map(str, md_files)
    ]
    subprocess.check_call(cmd)
    return {"export": str(out), "chapters": [m.name for m in md_files]}
```

### 15.2 RAG wrappers (rag/retrieve.py)

```python
# rag/retrieve.py (augment with a function usable by the agent)
import chromadb
client = chromadb.PersistentClient(path="rag/db")
col = client.get_or_create_collection("book")

def fact_pack(query: str, k: int = 6):
    res = col.query(query_texts=[query], n_results=k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    return [
        {
            "text": d,
            "citeKey": (m.get("citeKey") or m.get("source") or "source:unknown"),
            "source": {"title": m.get("title") or m.get("source"), "url": m.get("url"), "page": m.get("page")},
            "confidence": 0.75,  # placeholder
        } for d, m in zip(docs, metas)
    ]
```

### 15.3 LLM wrapper (backend/llm.py)

```python
# backend/llm.py
import os, json
from typing import List, Dict

# Replace with your provider client (OpenAI/Anthropic/etc.)
def chat(model: str, messages: List[Dict], max_tokens: int = 1200, response_format: str | None = None):
    # Pseudo-implementation stub; integrate your real SDK here.
    # Must return a string content. Keep interface stable.
    raise NotImplementedError("Plug in your model provider here")

def complete_json(model: str, system: str, user: str, schema_hint: str) -> dict:
    prompt = f"{system}

Return ONLY valid JSON matching schema:
{schema_hint}

USER:
{user}"
    out = chat(model, [{"role":"user","content":prompt}], max_tokens=1400)
    return json.loads(out)
```

### 15.4 Writer tool (calls LLM to draft a section)

```python
# backend/writer.py
import json
from .llm import complete_json

WRITER_SCHEMA = json.dumps({
  "type": "object",
  "properties": {"markdown":{"type":"string"}},
  "required": ["markdown"]
})

WRITER_SYSTEM = (
    "You write book sections in Markdown using headings (##, ###), in-text citations [@key], "
    "and figure placeholders as {{FIG:slug:"caption"}}. If a non-obvious claim lacks support, "
    "insert [[NEEDS_SOURCE]]. End with a 'Summary' and 'Key Takeaways' list."
)

def write_section(model: str, brief: dict, facts: list) -> str:
    user = json.dumps({"brief": brief, "facts": facts}, ensure_ascii=False)
    out = complete_json(model, WRITER_SYSTEM, user, WRITER_SCHEMA)
    return out["markdown"]
```

### 15.5 The Reasoning Agent (backend/agent.py)

```python
# backend/agent.py
import json, time
from typing import Dict, Callable, Any, List
from .llm import complete_json
from . import tools as T
from rag.retrieve import fact_pack
from .writer import write_section

AGENT_SYSTEM = (
  "You are a book-building reasoning agent. You decide the next best ACTION and ARGUMENTS as JSON.
"
  "Available tools: retrieve_facts, write_section, save_chapter, build_book, finish.
"
  "Rules:
"
  " - Think step-by-step, but OUTPUT ONLY JSON per step.
"
  " - Prefer retrieving fact packs before writing.
"
  " - Save chapters under 'chapters/{slug}.md'.
"
  " - When done, use 'finish' with a short summary and pointers to outputs.
"
)

AGENT_SCHEMA = json.dumps({
  "type":"object",
  "properties":{
    "tool":{"type":"string"},
    "args":{"type":"object"}
  },
  "required":["tool","args"]
})

def run_agent(goal: str, model: str = "your-writer-model", max_steps: int = 8) -> tuple[list, str]:
    trace: List[dict] = []
    context = {"goal": goal}
    for step in range(max_steps):
        user = json.dumps({"goal": goal, "trace": trace[-3:]}, ensure_ascii=False)
        plan = complete_json(model, AGENT_SYSTEM, user, AGENT_SCHEMA)
        tool = plan["tool"]; args = plan.get("args", {})
        obs = {}
        if tool == "retrieve_facts":
            obs = {"facts": fact_pack(args.get("query", goal), k=args.get("k", 6))}
        elif tool == "write_section":
            brief = args.get("brief", {"topic": goal, "target_words": 1200})
            facts = args.get("facts") or (trace and trace[-1].get("observation",{}).get("facts",[])) or []
            md = write_section(model, brief, facts)
            obs = {"markdown": md}
        elif tool == "save_chapter":
            rel = args.get("path", "chapters/auto.md")
            md  = args.get("markdown") or (trace and trace[-1].get("observation",{}).get("markdown"))
            obs = T.write_file(rel, md or "")
        elif tool == "build_book":
            obs = T.build_book(args.get("format","pdf"))
        elif tool == "finish":
            trace.append({"action": plan, "observation": {"done": True}})
            return trace, args.get("summary","done")
        else:
            obs = {"error": f"unknown tool '{tool}'"}
        trace.append({"action": plan, "observation": obs})
    return trace, "max_steps_reached"
```

### 15.6 API endpoint (backend/main.py)

```python
# backend/main.py (additions)
from pydantic import BaseModel
from .agent import run_agent

class AgentReq(BaseModel):
    goal: str
    max_steps: int = 8
    model: str = "your-writer-model"

@app.post("/agent/run")
def agent_run(req: AgentReq):
    trace, result = run_agent(req.goal, req.model, req.max_steps)
    return {"result": result, "trace": trace}
```

### 15.7 CLI command (scripts/cli.py)

```python
# scripts/cli.py (additions)
@app.command()
def agent(goal: str, steps: int = 8, model: str = "your-writer-model"):
    r = requests.post(f"{API}/agent/run", json={"goal": goal, "max_steps": steps, "model": model}, timeout=900)
    r.raise_for_status()
    data = r.json()
    print("[bold]Result:[/]", data["result"])
    # Pretty-print a compact trace
    from rich import box
    from rich.table import Table
    t = Table(title="Agent Trace", box=box.SIMPLE)
    t.add_column("Step", justify="right"); t.add_column("Tool"); t.add_column("Observation (truncated)")
    for i, item in enumerate(data["trace"], 1):
        tool = item["action"]["tool"]
        obs  = str(item["observation"])[:120].replace("\n"," ")
        t.add_row(str(i), tool, obs + ("..." if len(str(item["observation"]))>120 else ""))
    print(t)
```

### 15.8 Agent prompt to use

When you run `book agent`, the agent receives this **system prompt** (abbrev) and your **goal**. You can modify strategy by changing `AGENT_SYSTEM` (e.g., force `retrieve_facts` first, define chapter slug to write, etc.).

**Tip:** Start with goals like:
- _“Write the Introduction chapter using the outline in book/toc.yaml, save to chapters/01-intro.md, then build PDF.”_
- _“Draft Chapter 2 (Energy Storage) at ~1500 words using RAG on uploaded PDFs; save and do not build.”_

---

## Quickstart (optional)
```bash
# macOS
brew install python@3.11 redis pandoc git
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make dev   # run API
python scripts/cli.py agent --goal "Draft Chapter 1 and export PDF"
```
