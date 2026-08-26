<div align="center">
  <h1>⚡ Axon v1.0.0 ⚡</h1>
  <p><b>The Official Launch Release: "The Bleeding Edge, Summarized."</b></p>
  <p>A hosted OSINT intelligence feed for founders and builders.</p>
  
  <p>
    <a href="https://axon-phi-ruby.vercel.app"><b>Explore Live Demo →</b></a>
  </p>
</div>

Axon continuously scans the frontier of technical discourse — ArXiv, Hacker News, GitHub, Reddit, and elite AI labs — distilling the global firehose into a high-density, 3-minute daily brief.

Built to solve information overload, Axon filters out the noise (no tutorials, no fluff) and surfaces the raw nodes where technology is being built, debated, and shipped.

---

## 🛠️ Performance-First Architecture

Axon is split into a high-performance Python ingestion engine and a reactive SvelteKit interface:

```mermaid
graph TD
    Sources[HN, ArXiv, GitHub, Reddit, AI Labs, Expert Blogs] -->|Fetcher| Ingestion[FastAPI Ingestion Engine]
    Ingestion -->|Groq LLaMA 3.3| Analysis[AI Analyzer: Classification & Insights]
    Analysis -->|PostgreSQL| Storage[(Database & Cache)]
    Storage -->|REST API| UI[SvelteKit Web Dashboard]
    UI -->|PWA| Mobile[Native-feel Mobile App]
    UI -->|Chat| AI[Article-Scoped Q&A]
```

### Core Stack
- **Frontend**: SvelteKit 5 (Runes), Tailwind CSS 4, Lucide Icons.
- **Backend**: FastAPI, SQLModel, PostgreSQL.
- **Intelligence**: Groq (LLaMA 3.3 70B) for instant, 0-latency summaries and Q&A.
- **Auth**: Better-Auth with cross-subdomain session persistence.

---

## ✨ v1.0.0 Launch Features

- **⚡ Real-time Signal Tracking** — Background ingestion every 4 hours via APScheduler.
- **🧠 Zero-Latency AI Insights** — Every signal gets a dense, two-paragraph context summary.
- **💬 Article-Scoped Chat** — Chat directly with any research paper or technical blog.
- **📱 PWA & Mobile-First** — Installable on iOS/Android with a gesture-based UI and native navigation.
- **🔍 Content Extraction** — Full-text extraction via readability parsing (public pages we can fetch).
- **✨ Sleek Minimalist UI** — High-contrast monochrome theme with pulsing skeleton loaders and fluid animations.
- **💾 Cloud Sync** — Authenticated saves and reading history synced across devices.
- **📈 Global Trends** — Live tracking of moving keywords and momentum across all tech sub-cultures.

---

## 🚀 Getting Started

### 1. Clone & Setup (private repo — collaborators only)
```bash
git clone https://github.com/BemnetMussa/Axon.git
cd Axon
```

### 2. Backend (FastAPI)
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Add your GROQ_API_KEY
uvicorn app.main:app --reload
```

### 3. Frontend (SvelteKit)
```bash
cd fronted
npm install
npm run dev
```

### 4. Run the tests
```bash
# Backend (pytest — runs against in-memory SQLite, no services needed)
cd backend
pip install -r requirements-dev.txt
python -m pytest

# Frontend (Vitest)
cd fronted
npm test
```

---

## 📂 Project Structure

- `backend/app/` — FastAPI core, ingestion engine, and AI analysis pipelines.
- `fronted/src/` — SvelteKit application, design system, and auth-client.
- `fronted/static/` — PWA assets and brand identity.
- `scripts/` — Automated environment setup and deployment helpers.

---

## Licensing

Axon is **open-core**. The curation engine and hosted product are proprietary. A public client may be released separately under an open-source license later.

Details: [OPEN_CORE.md](OPEN_CORE.md) · [LICENSE](LICENSE)

---

## Feedback

Questions and product feedback: [@BemnetMussa](https://x.com/BemnetMussa).
Invited collaborators: see [CONTRIBUTING.md](CONTRIBUTING.md).

**[Live Demo](https://axon-phi-ruby.vercel.app)** · **[Architecture](backend/ARCHITECTURE.md)** · **[Privacy](https://axon-phi-ruby.vercel.app/privacy)** · **[License](LICENSE)** · **[Open-core](OPEN_CORE.md)**

---
<div align="center">
  <sub>Built for builders. © 2026 AXON.</sub>
</div>

**Scheduler note:** Auto-ingestion uses APScheduler inside the API process. It only runs while that process is **continuously up**—deploy the backend on an always-on host (e.g. a container or VM), not a model that cold-stops between requests, or the 4-hour job will not fire reliably. Set `INGEST_INTERVAL_HOURS` in the API environment to change the cadence (default `4`).

### Know if ingest is running (no guessing)

- **`GET /health`** on the API (public, no auth) returns JSON with:
  - `scheduler.next_run_at_utc` — when APScheduler will run next (if the in-process job is enabled)
  - `last_scheduled_ingest` — timestamp and outcome of the last scheduled run
- **`GET /`** — short status plus pointer to `/health`

Backend env toggles:

| Variable | Effect |
|----------|--------|
| `INGEST_INTERVAL_HOURS` | Hours between scheduled runs (default `4`) |
| `INGEST_RUN_ON_STARTUP` | If `true`, queue one ingest when the API starts (good right after deploy) |
| `DISABLE_SCHEDULER` | If `true`, do not start APScheduler (use when ingest is driven only by external cron) |

### Vercel frontend + cron-triggered ingest

The SvelteKit app can trigger your **hosted FastAPI** on a schedule so ingest still runs even if you rely mainly on Vercel for the UI:

1. Add **`CRON_SECRET`** in the Vercel project (Settings → Environment Variables). Use a long random string. Vercel Cron sends `Authorization: Bearer <CRON_SECRET>` to your route.
2. Ensure **`INTERNAL_API_URL`**, **`AXON_INTERNAL_SECRET`**, and (optional) **`CRON_INGEST_USER_ID`** are set on Vercel so the serverless function can call `POST {INTERNAL_API_URL}/ingest`.
3. [`fronted/vercel.json`](fronted/vercel.json) defines `GET /api/cron/ingest` once per day at **00:00 UTC** (`0 0 * * *`). Vercel's Hobby tier only permits daily cron — upgrade to Pro if you need a faster cadence (e.g. `0 */4 * * *`). The backend's APScheduler still runs every 4h on the always-on host regardless.
4. **Avoid double ingest:** if your API already runs APScheduler 24/7, you do **not** need Vercel cron—pick one. If you use **only** Vercel cron for ingest, set **`DISABLE_SCHEDULER=1`** on the API.

**Custom domain on Vercel:** update `BETTER_AUTH_URL`, OAuth redirect URIs, and `CORS_ALLOWED_ORIGINS` on the API to match `https://yourdomain.com`.

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 15 ([Supabase](https://supabase.com) free tier, or Docker for local dev)
- [Groq API key](https://console.groq.com) (free tier — 14,400 req/day)
- GitHub personal access token (optional, improves GitHub API rate limits)

### 1. Clone (private — collaborators only)

```bash
git clone https://github.com/BemnetMussa/Axon.git
cd Axon
```

### 2. Set Up PostgreSQL

**Option A: Supabase (recommended — free, hosted, no setup)**

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Project Settings → Database → Connection string → URI**
3. Copy the connection string and paste it in your `.env` as `DATABASE_URL`

**Option B: Local Docker**

```bash
cd backend
docker compose up db -d
```

This starts Postgres on port `5433` (host) mapped to `5432` (container) with user `axon`, password `axon123`, database `axon_db`.

### 3. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — add your GROQ_API_KEY (required) and GITHUB_TOKEN (optional)

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://127.0.0.1:8000`. On first startup it creates the database tables automatically. The background scheduler will ingest new articles every 4 hours.

### 4. Seed Data

In a separate terminal, trigger the first ingestion and analysis:

```bash
# Replace SECRET with the AXON_INTERNAL_SECRET from backend/.env
curl -X POST http://127.0.0.1:8000/ingest \
  -H "X-Axon-Internal-Secret: SECRET" \
  -H "X-Axon-User-Id: local-dev"
curl -X POST http://127.0.0.1:8000/analyze \
  -H "X-Axon-Internal-Secret: SECRET" \
  -H "X-Axon-User-Id: local-dev"
```

### 5. Frontend Setup

```bash
cd fronted

npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Project Structure

```
axon/
├── .github/
│   ├── workflows/ci.yml        # CI pipeline (backend + frontend checks)
│   ├── ISSUE_TEMPLATE/         # Bug report & feature request templates
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app, routes, scheduler
│   │   ├── models.py           # SQLModel schemas (Article, Trend)
│   │   ├── core/
│   │   │   └── database.py     # Engine, session management
│   │   └── services/
│   │       ├── fetcher.py      # Ingestion from all sources
│   │       ├── analyzer.py     # Classification, insights, chat (Groq)
│   │       └── extractor.py    # Full article content extraction
│   ├── requirements.txt
│   ├── compose.yaml            # Docker Compose (web + db)
│   ├── Dockerfile
│   └── .env.example
├── fronted/                    # SvelteKit web UI
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts          # API client with pagination
│   │   │   ├── ui.ts           # Navigation, helpers, theme utils
│   │   │   └── components/
│   │   │       ├── feed/       # ArticleCard, FeedHeader, FeedPanel
│   │   │       ├── navigation/ # DesktopSidebar, MobileBottomNav
│   │   │       └── reader/     # ReaderPanel, ChatDock
│   │   ├── routes/
│   │   │   └── +page.svelte    # App shell — all state lives here
│   │   └── service-worker.ts   # PWA offline support
│   ├── static/
│   │   └── manifest.json       # PWA manifest
│   └── package.json
├── Axon_cli/
│   └── axon.py                 # Rich-based terminal interface (legacy)
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

---

## API Endpoints

| Method | Endpoint                          | Description                                     |
| ------ | --------------------------------- | ----------------------------------------------- |
| GET    | `/`                               | Health check + scheduler status                 |
| GET    | `/articles?limit=40&cursor=123`   | List articles (cursor-based pagination)         |
| GET    | `/articles/trending`              | Fetch algorithmically sorted top performing articles |
| GET    | `/articles/{id}/content`          | Extract and return full article content          |
| GET    | `/saved`                          | Retrieve the authenticated user's saved articles |
| POST   | `/articles/{id}/save`             | Toggle the save status of an article             |
| GET    | `/trends`                         | Top 10 trending keywords                        |
| GET    | `/brief/{id}`                     | Generate a structured deep brief                 |
| POST   | `/ingest`                         | Trigger ingestion from all sources               |
| POST   | `/analyze`                        | Classify + generate insights for new articles    |
| POST   | `/articles/{id}/chat`             | Chat about an article `{ "question": "..." }`    |
| POST   | `/articles/{id}/view`             | Track a view                                     |

---

## Data Sources

| Source                                                     | What it pulls                             | Category default |
| ---------------------------------------------------------- | ----------------------------------------- | ---------------- |
| Hacker News                                                | Top stories, Ask HN, Show HN             | AI / Concerns    |
| ArXiv                                                      | cs.AI and cs.LG papers                   | Signal           |
| GitHub                                                     | Trending repos by stars and topics        | Momentum         |
| Reddit                                                     | Tech/AI subreddits via RSS               | Concerns         |
| Lobsters                                                   | Top technical discussions                 | Concerns         |
| Product Hunt                                               | New product launches via RSS              | Discovery        |
| TechCrunch / The Verge / Ars Technica                      | AI and tech news via RSS                  | AI               |
| OpenAI / Anthropic / DeepMind                              | Blog RSS feeds                            | AI               |
| NVIDIA / Pinecone / Modal / Cerebras                       | Infrastructure blogs                      | AI               |
| Karpathy / Simon Willison / Lilian Weng / Fast.ai / Altman | Expert blogs                              | Momentum         |

Articles are filtered through a quality gate that removes fluff (career advice, tutorials, listicles) and blacklisted domains while promoting viral signals that cross engagement thresholds.

---

## AI Layer

Axon uses **Groq** (LLaMA 3.3 70B) for three things:

1. **Insights** — auto-generated on ingestion. Two dense paragraphs: what this is, and why it matters.
2. **Deep Briefs** — on-demand. Three sections: Technical Primitive, Market Impact, Opportunity.
3. **Article Chat** — conversational Q&A scoped to a specific article's full content.

---

## Categories

Articles are classified by `analyzer.py` into:

| Category      | Meaning                                        |
| ------------- | ---------------------------------------------- |
| **AI**        | Model releases, lab announcements, infra news  |
| **Signal**    | Research breakthroughs (ArXiv, academic)        |
| **Momentum**  | Rising projects, expert builds, GitHub trending |
| **Discovery** | Usable tools, frameworks, demos, playgrounds   |
| **Concerns**  | Community problems, discourse, debates          |

---

## Environment Variables

Create `backend/.env` from the example:

```bash
# Supabase (or any PostgreSQL)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres

# Required
GROQ_API_KEY=gsk_your_key_here

# Optional
GITHUB_TOKEN=ghp_your_token_here       # avoids GitHub rate limits
INGEST_INTERVAL_HOURS=4                # default 4 hours
DB_ECHO=false                          # set to "true" to log SQL queries
```

The frontend reads `VITE_API_BASE_URL` (defaults to `http://127.0.0.1:8000`).

---

## Docker

To run the full backend stack:

```bash
cd backend
docker compose up --build
```

This starts both FastAPI and PostgreSQL. The API will be available at `http://localhost:8000`.

---

## Feedback

Axon is open-core. The curation engine is proprietary; public pull requests to that engine are not accepted at this time.

Product feedback: [@BemnetMussa](https://x.com/BemnetMussa). Collaborators with repo access: [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Tech Stack

| Layer    | Technology                                         |
| -------- | -------------------------------------------------- |
| Backend  | Python, FastAPI, SQLModel, PostgreSQL, APScheduler  |
| Frontend | Svelte 5, SvelteKit 2, Tailwind CSS v4, TypeScript |
| AI       | Groq Cloud (LLaMA 3.3 70B)                        |
| Sources  | httpx, feedparser, readability-lxml                |
| PWA      | Service Worker, Web App Manifest                   |

---

## License

**Proprietary (open-core)** — see [LICENSE](LICENSE) and [OPEN_CORE.md](OPEN_CORE.md).

---

## Links

- **Live Demo:** [axon-phi-ruby.vercel.app](https://axon-phi-ruby.vercel.app)
- **Twitter:** [@BemnetMussa](https://x.com/BemnetMussa)
- **Privacy:** [axon-phi-ruby.vercel.app/privacy](https://axon-phi-ruby.vercel.app/privacy)
- **Terms:** [axon-phi-ruby.vercel.app/terms](https://axon-phi-ruby.vercel.app/terms)
- **Open-core:** [OPEN_CORE.md](OPEN_CORE.md)
