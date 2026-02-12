# Desktop AI Automation Hub

A Docker-ready FastAPI application to run AI-assisted desktop workflows for community management.

## What this app does

- **Desktop task automation** via script jobs (open files, run workflows, publish content steps).
- **Strict web access control** with 3 modes:
  - `offline` (no internet)
  - `allowlist` (only approved domains)
  - `open` (full access)
- **Structured + unstructured knowledge database**:
  - Structured JSON data for entities, campaigns, and metadata.
  - Unstructured text notes, extracted content, and AI outputs.
- **Image intelligence pipeline**:
  - Store inbound and uploaded images with metadata (hash, dimensions, mime, source).
  - Generate visual context, captions, TikTok/Reel and YouTube ideas from images.
  - Works with **Ollama vision models** (default `llava:7b`).
- **Task scheduling** using cron or one-time execution.
- **Full audit logging** for every action and decision.
- **WhatsApp Business API integration hooks**:
  - Receive inbound instructions.
  - If an inbound message includes an image, download/store/analyze it automatically.
  - Send outbound messages only to your approved contact.
- **Pluggable LLM providers**, including local Ollama.

---

## Architecture

- **FastAPI** API server
- **PostgreSQL** as primary database
- **SQLAlchemy** ORM models
- **APScheduler** background scheduler
- **Ollama/OpenAI-compatible provider abstraction**

---

## Quick start (Docker)

```bash
docker compose up --build
```

API docs:
- http://localhost:8000/docs

---

## Environment

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

Important values:
- `WEB_ACCESS_MODE=offline|allowlist|open`
- `WEB_ALLOWLIST_DOMAINS=example.com,news.ycombinator.com`
- `WHATSAPP_ALLOWED_TO=+15551230000`
- `LLM_PROVIDER=ollama|openai_compatible`
- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- `OLLAMA_VISION_MODEL=llava:7b`
- `MEDIA_STORAGE_DIR=data/media`

---

## Image workflows

### 1) Upload an image and get ideas
`POST /media/images` (multipart form-data):
- `file`: image file
- `objective`: optional instruction (e.g. "Create IG caption + TikTok idea")

### 2) Re-analyze a stored image
`POST /media/images/analyze`
```json
{
  "asset_id": 1,
  "objective": "Write caption and YouTube short hook"
}
```

### 3) List stored images
`GET /media/images`

---

## Example flow

1. Add knowledge (`POST /knowledge/items`).
2. Create a script task (`POST /tasks`).
3. Optionally schedule (`POST /tasks/{task_id}/schedule`).
4. Track logs (`GET /logs`).
5. Receive WhatsApp command (`POST /whatsapp/webhook`).
6. Upload/analyze images (`POST /media/images`).

---

## Script tasks

Script tasks can execute files only from the internal `scripts/` directory.
This prevents arbitrary command execution outside approved automation scripts.

Included example:
- `scripts/open_file_list.py` reads a JSON list of local files and attempts to open them.

---

## Security guardrails

- Web policy enforcement before any search/navigation call.
- Restricted script path execution.
- Outbound WhatsApp messages limited to one configured contact.
- Inbound WhatsApp images are fetched only via authenticated Graph API calls.
- Audit entries for every API operation and scheduler run.

---

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
