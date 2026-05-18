# server.py — Brief MCP HTTP Server
# Endpoints: GET /tools, POST /tools/search_web, fetch_readable,
#            summarize_with_citations, save_markdown
# Auth: Authorization: Bearer <MCP_HTTP_TOKEN>
# Search: Tavily (free tier)  |  LLM: Ollama (local, free)
#
# Install: pip install flask requests python-dotenv readability-lxml
# Run:     python server.py

import os
import re
import json
import pathlib
from functools import wraps
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from readability import Document   # readability-lxml

load_dotenv()

app = Flask(__name__)

PORT         = int(os.getenv("PORT", 3000))
TOKEN        = os.getenv("MCP_HTTP_TOKEN", "changeme")
TAVILY_KEY   = os.getenv("TAVILY_API_KEY", "")
OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OUTPUT_DIR   = pathlib.Path(os.getenv("OUTPUT_DIR", "./output"))

# ── Tool manifest ─────────────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "search_web",
        "description": "Search the web via Tavily and return top results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string",  "description": "Search query"},
                "k":     {"type": "integer", "description": "Number of results (default 5)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_readable",
        "description": "Fetch a URL and return main article text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "summarize_with_citations",
        "description": "Use local LLM to produce 5 bullet summary with [N] citations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "docs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url":   {"type": "string"},
                            "text":  {"type": "string"},
                        },
                    },
                },
            },
            "required": ["topic", "docs"],
        },
    },
    {
        "name": "save_markdown",
        "description": "Save content to a markdown file and return the path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content":  {"type": "string"},
            },
            "required": ["filename", "content"],
        },
    },
]

# ── Auth decorator ────────────────────────────────────────────────────────────
def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if header != f"Bearer {TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper

# ── GET /tools ────────────────────────────────────────────────────────────────
@app.get("/tools")
@auth_required
def list_tools():
    return jsonify({"tools": TOOLS})

# ── POST /tools/search_web ────────────────────────────────────────────────────
@app.post("/tools/search_web")
@auth_required
def search_web():
    body  = request.get_json(force=True) or {}
    query = body.get("query", "").strip()
    k     = int(body.get("k", 5))

    if not query:
        return jsonify({"error": "query required"}), 400
    if not TAVILY_KEY:
        return jsonify({"error": "TAVILY_API_KEY not set"}), 500

    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_KEY,
                "query": query,
                "max_results": k,
                "search_depth": "basic",
                "include_answer": False,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

    results = [
        {
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "snippet": r.get("content", ""),
            "source":  urlparse(r.get("url", "")).hostname or "",
        }
        for r in data.get("results", [])
    ]
    return jsonify(results)

# ── POST /tools/fetch_readable ────────────────────────────────────────────────
@app.post("/tools/fetch_readable")
@auth_required
def fetch_readable():
    body = request.get_json(force=True) or {}
    url  = body.get("url", "").strip()

    if not url:
        return jsonify({"error": "url required"}), 400

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; BriefBot/1.0)"},
            timeout=10,
        )
        resp.raise_for_status()
        doc   = Document(resp.text)
        raw   = re.sub(r"<[^>]+>", " ", doc.summary())
        text  = re.sub(r"\s+", " ", raw).strip()[:8000]
        title = doc.title()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"url": url, "title": title, "text": text})

# ── POST /tools/summarize_with_citations ──────────────────────────────────────
@app.post("/tools/summarize_with_citations")
@auth_required
def summarize_with_citations():
    body  = request.get_json(force=True) or {}
    topic = body.get("topic", "").strip()
    docs  = body.get("docs", [])

    if not topic or not isinstance(docs, list):
        return jsonify({"error": "topic and docs[] required"}), 400

    context = "\n\n---\n\n".join(
        f'[{i+1}] Title: {d.get("title","")}\nURL: {d.get("url","")}\n{d.get("text","")[:2000]}'
        for i, d in enumerate(docs)
    )

    prompt = (
        f'You are a research assistant. Using ONLY the sources below, '
        f'write exactly 5 bullet points summarizing "{topic}".\n\n'
        "Rules:\n"
        "- Each bullet ≤ 200 characters (including the inline citation).\n"
        "- Each bullet MUST end with at least one [N] citation matching a source number.\n"
        '- Return ONLY valid JSON: { "bullets": ["...[1]", ...], '
        '"sources": [{"i":1,"title":"...","url":"..."}] }\n'
        "- No markdown fences, no extra text outside the JSON.\n\n"
        f"Sources:\n{context}"
    )

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=120,
        )
        if not resp.ok:
            return jsonify({"error": f"Ollama error: {resp.text}"}), 502

        raw_text = resp.json().get("message", {}).get("content", "")

        match = re.search(r"\{[\s\S]*\}", raw_text)
        if not match:
            return jsonify({"error": "LLM did not return valid JSON",
                            "raw": raw_text[:400]}), 502

        parsed  = json.loads(match.group())
        bullets = [b[:200] for b in (parsed.get("bullets") or [])[:5]]
        sources = parsed.get("sources") or [
            {"i": i + 1, "title": d.get("title", ""), "url": d.get("url", "")}
            for i, d in enumerate(docs)
        ]
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"bullets": bullets, "sources": sources})

# ── POST /tools/save_markdown ─────────────────────────────────────────────────
@app.post("/tools/save_markdown")
@auth_required
def save_markdown():
    body     = request.get_json(force=True) or {}
    filename = body.get("filename", "").strip()
    content  = body.get("content",  "").strip()

    if not filename or not content:
        return jsonify({"error": "filename and content required"}), 400

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", pathlib.Path(filename).name)
    full = (OUTPUT_DIR / safe).resolve()
    full.write_text(content, encoding="utf-8")

    return jsonify({"path": str(full)})

# ── Start ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Brief MCP server running → http://localhost:{PORT}")
    print(f"Auth token   : {TOKEN}")
    print(f"Ollama URL   : {OLLAMA_URL}  (model: {OLLAMA_MODEL})")
    print(f"Tavily key   : {'set ✓' if TAVILY_KEY else 'MISSING ✗'}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
