# Brief MCP — Agentic Research Briefer

A minimal HTTP MCP server + CLI that **searches → reads → summarises → saves** any topic.

```
CLI (brief.js) ──HTTP──> server.js /tools/... ──> Tavily (search)
                                  │
                                  ├──> Ollama  (local LLM, free)
                                  └──> ./output/brief_YYYY-MM-DD.md
```

---

## Stack

| Layer | Tool | Cost |
|---|---|---|
| Search | [Tavily](https://app.tavily.com) | Free tier (1 000 searches/mo) |
| LLM | [Ollama](https://ollama.com) | Free, local |
| Model | `llama3` (default) | Free |
| Server | Express.js | — |

---

## Setup (< 10 minutes)

### 1 — Clone & install

```bash
git clone <this-repo> brief-mcp
cd brief-mcp
pip install flask requests python-dotenv readability-lxml
```

### 2 — Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```
MCP_HTTP_TOKEN=any-secret-string
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx   # from https://app.tavily.com
```

### 3 — Start Ollama

```bash
# Install from https://ollama.com, then:
ollama pull llama3
ollama serve          # starts on http://localhost:11434
```

> **LM Studio alternative**: start the local server in LM Studio's Developer tab,
> then set in `.env`:
> ```
> OLLAMA_BASE_URL=http://localhost:1234/v1
> OLLAMA_MODEL=lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF
> ```
> and change the `/api/chat` path in `server.py` to `/chat/completions` (OpenAI format).

### 4 — Start the server

```bash
python server.py
# Brief MCP server running → http://localhost:3000
```

### 5 — Run the CLI

```bash
python brief.py "multimodal large language models"
```

Output:
```
🔍  Searching for: "multimodal large language models"
   Found 6 results.

📄  Fetching content from 3 domains…
   ✓ lilianweng.github.io
   ✓ en.wikipedia.org
   ✓ mmmu-benchmark.github.io

🧠  Summarizing with local LLM…

✅  Saved → /path/to/output/brief_2025-05-18.md
```

---

## API Reference

All endpoints require:
```
Authorization: Bearer <MCP_HTTP_TOKEN>
Content-Type: application/json
```

### `GET /tools`
Returns tool manifest.

```bash
curl http://localhost:3000/tools \
  -H "Authorization: Bearer changeme"
```

---

### `POST /tools/search_web`
```json
{ "query": "llm agents", "k": 5 }
```
Response:
```json
[{ "title": "...", "url": "...", "snippet": "...", "source": "example.com" }]
```

---

### `POST /tools/fetch_readable`
```json
{ "url": "https://example.com/article" }
```
Response:
```json
{ "url": "...", "title": "...", "text": "main article text..." }
```

---

### `POST /tools/summarize_with_citations`
```json
{
  "topic": "quantum computing",
  "docs": [
    { "title": "IBM Quantum", "url": "https://...", "text": "..." }
  ]
}
```
Response:
```json
{
  "bullets": ["Quantum computers use qubits instead of bits [1]", "..."],
  "sources": [{ "i": 1, "title": "IBM Quantum", "url": "https://..." }]
}
```

---

### `POST /tools/save_markdown`
```json
{ "filename": "brief_2025-05-18.md", "content": "# Brief\n..." }
```
Response:
```json
{ "path": "/absolute/path/output/brief_2025-05-18.md" }
```

---

## cURL Examples

```bash
TOKEN=changeme
BASE=http://localhost:3000

# List tools
curl $BASE/tools -H "Authorization: Bearer $TOKEN"

# Search
curl -X POST $BASE/tools/search_web \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"AI agents 2025","k":3}'

# Fetch readable
curl -X POST $BASE/tools/fetch_readable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://lilianweng.github.io/posts/2023-06-23-agent/"}'

# Summarize
curl -X POST $BASE/tools/summarize_with_citations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI agents",
    "docs": [{"title":"Agents","url":"https://example.com","text":"LLM agents use tools..."}]
  }'

# Save
curl -X POST $BASE/tools/save_markdown \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.md","content":"# Test\n- bullet"}'
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `401 Unauthorized` | Check `MCP_HTTP_TOKEN` in `.env` matches your `curl`/client |
| `TAVILY_API_KEY not set` | Add key to `.env` and restart server |
| `Ollama error` | Run `ollama serve` and confirm `ollama run llama3` works |
| `LLM did not return valid JSON` | Lower temperature; model may need a larger context window — try `llama3:8b` |
| `fetch_readable` returns empty | Site blocks bots; increase `k` and skip to next result |
