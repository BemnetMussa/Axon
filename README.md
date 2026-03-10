# Axon

**An open-source intelligence feed for builders.** Axon continuously scans technical sources — ArXiv, Hacker News, GitHub, Reddit, expert blogs, and AI lab announcements — filters out noise, and presents what matters through a clean web interface with AI-powered analysis.

Instead of checking dozens of sites every day, you open Axon.

---

## How It Works

```
Sources (HN, ArXiv, GitHub, Reddit, Lobsters, AI labs, expert blogs)
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
FastAPI ── REST API serving articles, trends, briefs, and chat
    │
    ▼
SvelteKit Web UI ── feed / reader / AI chat
```

Axon fetches signals, classifies them into five categories (**AI**, **Signal**, **Momentum**, **Discovery**, **Concerns**), generates a two-paragraph AI insight for each, and serves them through a responsive web dashboard where you can read, save, search, and chat with any article.

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 15 (Docker recommended)
- [Groq API key](https://console.groq.com) (free tier — 14,400 req/day)
- GitHub personal access token (optional, improves GitHub API rate limits)

### 1. Clone

```bash
git clone https://github.com/bemnetmussa/axon.git
cd axon
```

### 2. Start PostgreSQL

**Docker (recommended):**

```bash
cd backend
docker compose up db -d
```

This starts Postgres on port `5433` (host) mapped to `5432` (container) with user `axon`, password `axon123`, database `axon_db`.

**Or manually:**

```bash
createdb axon_db
```

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

The API is now running at `http://127.0.0.1:8000`. On first startup it creates the database tables automatically.

### 4. Seed Data

In a separate terminal, trigger ingestion and analysis:

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
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, routes, CORS
│   │   ├── models.py            # SQLModel schemas (Article, Trend)
│   │   ├── core/
│   │   │   └── database.py      # Engine, session management
│   │   └── services/
│   │       ├── fetcher.py       # Ingestion from all sources
│   │       └── analyzer.py      # Classification, insights, chat (Groq)
│   ├── requirements.txt
│   ├── compose.yaml             # Docker Compose (web + db)
│   ├── Dockerfile
│   └── .env.example
├── fronted/                     # SvelteKit web UI
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   ├── ui.ts            # Navigation, helpers
│   │   │   └── components/
│   │   │       ├── feed/        # ArticleCard, FeedHeader, FeedPanel
│   │   │       ├── navigation/  # DesktopSidebar, MobileBottomNav
│   │   │       └── reader/      # ReaderPanel, ChatDock
│   │   └── routes/
│   │       ├── +layout.svelte
│   │       └── +page.svelte     # App shell — all state lives here
│   └── package.json
└── Axon_cli/
    └── axon.py                  # Rich-based terminal interface (legacy)
```

---

## API Endpoints

| Method | Endpoint                      | Description                                  |
| ------ | ----------------------------- | -------------------------------------------- |
| GET    | `/`                           | Health check                                 |
| GET    | `/articles?limit=100`         | List articles (Reddit capped at ~30%)        |
| GET    | `/trends`                     | Top 10 trending keywords                     |
| GET    | `/brief/{article_id}`         | Generate a structured deep brief             |
| POST   | `/ingest`                     | Trigger ingestion from all sources           |
| POST   | `/analyze`                    | Classify + generate insights for new articles|
| POST   | `/articles/{article_id}/chat` | Chat about an article `{ "question": "..." }`|
| POST   | `/articles/{article_id}/view` | Track a view                                 |

---

## Data Sources

| Source         | What it pulls                          | Category default |
| -------------- | -------------------------------------- | ---------------- |
| Hacker News    | Ask HN, Show HN with 10+ comments     | Problem / Project|
| ArXiv          | cs.AI and cs.LG papers                | Breakthrough     |
| GitHub         | Repos created in last 30 days, 20+ stars | Project       |
| Reddit         | (via RSS/API)                          | Problem          |
| Lobsters       | Top technical discussions              | Problem          |
| OpenAI / Anthropic / DeepMind | Blog RSS feeds          | AI               |
| NVIDIA / Pinecone / Modal / Cerebras | Infrastructure blogs | AI           |
| Karpathy / Simon Willison / Lilian Weng / Fast.ai / Altman | Expert blogs | Project |

Articles are filtered through a quality gate (`is_gold`) that removes fluff (career advice, tutorials, listicles) and blacklisted domains while promoting viral signals that cross engagement thresholds.

---

## AI Layer

Axon uses **Groq** (LLaMA 3.3 70B) for three things:

1. **Insights** — auto-generated on ingestion. Two dense paragraphs: what this is, and why it matters.
2. **Deep Briefs** — on-demand. Three sections: Technical Primitive, Market Impact, Opportunity.
3. **Article Chat** — conversational Q&A scoped to a specific article's context.

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
DATABASE_URL=postgresql://axon:axon123@127.0.0.1:5432/axon_db
GROQ_API_KEY=gsk_your_key_here
GITHUB_TOKEN=ghp_your_token_here  # optional, avoids GitHub rate limits
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

Contributions are welcome. Here's the flow:

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Submit a pull request

**Areas where help is needed:**

- New data sources (Product Hunt, TechCrunch RSS, Hacker News front page)
- Smarter classification logic in `analyzer.py`
- Frontend polish — animations, accessibility, mobile UX
- Scheduled ingestion (cron / background worker)
- User accounts and persistent saved articles
- Deployment guides (Vercel, Railway, Fly.io)

---

## Tech Stack

| Layer    | Technology                                        |
| -------- | ------------------------------------------------- |
| Backend  | Python, FastAPI, SQLModel, PostgreSQL, Groq       |
| Frontend | Svelte 5, SvelteKit 2, Tailwind CSS v4, TypeScript|
| AI       | Groq Cloud (LLaMA 3.3 70B)                       |
| Sources  | httpx, feedparser, readability-lxml               |

---

## License

MIT — see [LICENSE](LICENSE).

---

## Contact

- GitHub Issues: [github.com/bemnetmussa/axon/issues](https://github.com/bemnetmussa/axon/issues)
- Twitter: [@BemnetMussa](https://x.com/BemnetMussa)
