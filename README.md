# Axon

**An open-source intelligence feed for builders.** Axon continuously scans technical sources — ArXiv, Hacker News, GitHub, Reddit, Product Hunt, expert blogs, and AI lab announcements — filters out noise, and presents what matters through a clean web interface with AI-powered analysis.

Instead of checking dozens of sites every day, you open Axon.

**[Live Demo →](https://axon-phi-ruby.vercel.app)**

---

## How It Works

```
Sources (HN, ArXiv, GitHub, Reddit, Lobsters, Product Hunt, TechCrunch,
         The Verge, Ars Technica, AI labs, expert blogs)
    │
    ▼
Ingestion ── fetcher.py pulls from APIs/RSS, deduplicates, filters noise
    │
    ▼
Analysis ── analyzer.py classifies into categories, generates AI insights via Groq
    │
    ▼
PostgreSQL ── articles + trends tables
    │
    ▼
FastAPI ── REST API with cursor-based pagination, content extraction, chat
    │
    ▼
SvelteKit Web UI ── feed / reader / AI chat / dark & light mode / PWA
```

Axon fetches signals, classifies them into five categories (**AI**, **Signal**, **Momentum**, **Discovery**, **Concerns**), generates a two-paragraph AI insight for each, and serves them through a responsive web dashboard where you can read, save, search, share, and chat with any article.

---

## Features

- **Auto-ingestion** — background scheduler fetches new signals every 4 hours (configurable)
- **AI insights** — every article gets a concise two-paragraph summary via Groq
- **Article chat** — ask questions about any article, powered by LLaMA 3.3 70B
- **Content extraction** — fetches full article text on demand using readability-lxml
- **Infinite scroll** — cursor-based pagination loads articles as you scroll
- **Share** — native share sheet on mobile, clipboard copy on desktop
- **Dark / Light mode** — toggle in sidebar, persisted to localStorage
- **PWA** — installable on mobile, works offline for cached content
- **Responsive** — full-width desktop layout, mobile-optimized with bottom nav

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 15 ([Supabase](https://supabase.com) free tier, or Docker for local dev)
- [Groq API key](https://console.groq.com) (free tier — 14,400 req/day)
- GitHub personal access token (optional, improves GitHub API rate limits)

### 1. Clone

```bash
git clone https://github.com/bemnetmussa/axon.git
cd axon
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
curl -X POST http://127.0.0.1:8000/ingest
curl -X POST http://127.0.0.1:8000/analyze
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
| GET    | `/articles/{id}/content`          | Extract and return full article content          |
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

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

**Quick version:**

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run checks: `npx svelte-check` (frontend) and verify backend imports
5. Submit a pull request

**Areas where help is needed:**

- Unit and integration tests (backend services, frontend components)
- Accessibility improvements (keyboard nav, screen readers, ARIA)
- Deployment guides (Vercel, Railway, Fly.io, Coolify)
- New data sources and smarter classification logic
- User accounts and persistent saved articles
- Internationalization

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

MIT — see [LICENSE](LICENSE).

---

## Links

- **Live Demo:** [axon-phi-ruby.vercel.app](https://axon-phi-ruby.vercel.app)
- **Issues:** [github.com/bemnetmussa/axon/issues](https://github.com/bemnetmussa/axon/issues)
- **Twitter:** [@BemnetMussa](https://x.com/BemnetMussa)
