# Axon Backend — Architecture & Development Report

> A complete, plain-language account of what the Axon backend is, how it's built,
> and how every piece fits together. Read this top-to-bottom and you'll understand
> the whole system without opening the code.

> **Open-core:** Public clones ship the API shell + community stubs. The full
> curation / AI engine loads from a local `private/services/` overlay (maintainers)
> or runs on the hosted product. See [OPEN_CORE.md](../OPEN_CORE.md).

---

## 1. What this backend is, in one paragraph

Axon's backend is a **fan-out intelligence aggregator**. On a timer, it reaches out
to ~25 published endpoints across the tech world (Hacker News, GitHub, ArXiv, AI-lab
blogs, expert RSS feeds, tech news), pulls in everything new *at the same time*, runs
it through a **dedupe → score → rank → filter → enrich** pipeline, and then hands the
survivors to an **AI analysis stage** that writes a human-readable insight for each one,
turns it into a searchable vector, and tracks trending keywords. A FastAPI HTTP layer
serves all of this to the SvelteKit frontend. The "product" isn't any single source —
it's this accumulated, cleaned, ranked, AI-distilled pipeline.

---

## 2. Tech stack

| Layer | Technology | Why |
|---|---|---|
| Web framework | **FastAPI** (ASGI) | Async-native — essential for talking to 25 sites at once |
| Server | **Gunicorn + Uvicorn workers** | Production process manager (see Dockerfile) |
| Database | **PostgreSQL + pgvector** | Relational store + vector column for semantic search |
| ORM / models | **SQLModel** (SQLAlchemy under the hood) | Typed models that double as table definitions |
| AI / LLM | **Groq — LLaMA 3.3 70B** (8B fallback) | Near-zero-latency inference for insights, briefs, chat |
| Embeddings | **fastembed** (384-dim, local) | Turns articles into vectors with no external API |
| Scheduling | **APScheduler** | Fires the ingest job every N hours |
| HTTP client | **httpx** (async) | Concurrent outbound requests |
| Feed parsing | **feedparser** | Parses RSS/Atom XML into article objects |
| Article extraction | **readability-lxml** | Pulls clean body text out of a web page |
| Rate limiting | **slowapi** | Per-user request limits |

Full dependency list lives in `requirements.txt`.

---

## 3. The big picture

```
        every 6h (APScheduler)  ──or──  manual POST /ingest  ──or──  Vercel Cron
                                  │
                                  ▼
                       ingest_intelligence()          ← orchestrator (fetcher.py)
                                  │
                 asyncio.gather(...) fires ALL sources at once
        ┌───────┬────────┬───────┬───────┬─────────┬────────┐
        HN    GitHub   ArXiv   AI-labs  Experts   TechNews  …   (parallel)
        └───────┴────────┴───────┴───────┴─────────┴────────┘
                                  │  ~150+ raw signals
                                  ▼
        1. DEDUPE   drop URLs already in Postgres + collapse cross-source near-dups
        2. SCORE    engagement_score = traction × recency × source-trust
        3. RANK     sort by score
        4. FILTER   is_gold() drops junk · cap 8/source · cap 100/run
        5. CLASSIFY assign category once (single source of truth)
        6. HYDRATE  fetch full article body for survivors (parallel, capped)
        7. STORE    INSERT into Postgres (is_processed = false)
                                  │
                                  ▼
                       analyze_articles()              ← AI stage (analyzer.py)
                                  │  runs OFF the event loop (asyncio.to_thread)
        • classify   →  AI / Signal / Momentum / Discovery / Concerns
        • insight    →  Groq LLaMA writes a 400–600 word brief from the full body
        • embed      →  384-dim vector (pgvector) for semantic search
        • trends     →  tally keyword frequency per day
                                  │
                                  ▼
                          FastAPI HTTP layer (main.py)
                                  │
                       SvelteKit frontend (via internal proxy)
```

Two ideas are worth internalizing:

1. **Fetch and "think" are separate stages.** Ingestion is fast and network-only.
   The expensive LLM work is a *second* step that runs on a background thread so it
   never blocks the API. The `is_processed` flag is the handoff: ingest drops raw rows
   in, analysis later picks up whatever is unprocessed.
2. **Everything fans out.** Talking to 25 sites sequentially would take ~40s; firing
   them concurrently makes the whole run take about as long as the *slowest single
   source*. The same concurrency trick is reused for full-content extraction.

---

## 4. Project structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app: all HTTP endpoints, scheduler, auth middleware
│   ├── models.py               # SQLModel tables (Article, Trend, Digest, SavedArticle, Feedback)
│   ├── core/
│   │   └── database.py         # Engine creation, init_db(), session factories
│   └── services/
│       ├── fetcher.py          # ALL data sources + ingestion pipeline + scoring
│       ├── analyzer.py         # Groq insights, classification, embeddings, trends, digests
│       └── extractor.py        # Full article body extraction (readability)
├── migration.py                # One-off column-add migration helper
├── requirements.txt
├── Dockerfile                  # Gunicorn + Uvicorn production image
├── compose.yaml / docker-compose.yml   # Local pgvector Postgres
└── vercel.json                 # Serverless deploy config (@vercel/python)
```

---

## 5. Where the data comes from

All sources live in `app/services/fetcher.py` as `hunt_*` coroutines — one per *kind*
of source. The backend speaks three "languages":

### JSON APIs (structured data)
| Function | Source | What it pulls |
|---|---|---|
| `hunt_hn_top` | Hacker News (Firebase API) | Front-page top 20 stories + their point counts |
| `hunt_hn_discussions` | Hacker News (Algolia API) | Ask HN / Show HN with `num_comments > 5` |
| `hunt_lobsters` | Lobste.rs `hottest.json` | Top technical discussions (RSS fallback) |
| `hunt_github_trending` | GitHub Search API | Repos **created recently** with star traction |
| `hunt_arxiv` | ArXiv Export API | Latest `cs.AI` + `cs.LG` papers |

### RSS / Atom feeds (the bulk — ~17 feeds)
| Function | Sources |
|---|---|
| `hunt_ai_labs` | OpenAI, DeepMind, Google AI, HuggingFace |
| `hunt_anthropic` | Anthropic (via sitemap.xml — see below) |
| `hunt_infrastructure` | NVIDIA, Together AI, Google Research |
| `hunt_expert_blogs` | Karpathy, Simon Willison, Lilian Weng, Fast.ai, Sam Altman, BAIR |
| `hunt_tech_news` | TechCrunch, The Verge, Ars Technica |
| `hunt_product_launches` | Product Hunt |

> **Important:** the backend does **not** scrape arbitrary HTML. Every source is an
> endpoint each site *publishes on purpose* (an API or an RSS feed). That's why it's
> fast and stable — and why a feed silently moving/dying (a 404) is the main failure
> mode. Each hunter now calls `_check_feed()`, which logs a warning when a feed returns
> zero entries, so dead feeds can't disappear unnoticed again.

### Special case: Anthropic (no RSS, ingested via sitemap)
Anthropic publishes **no RSS feed** (every feed URL 404s), but its `robots.txt` allows
crawling and its **`sitemap.xml`** lists all 224 `/news/` pages, each with a `lastmod`
date. `hunt_anthropic` parses the sitemap, takes the newest pages, and reads `og:title` +
meta `description` from each for a clean card — a robust feed substitute that avoids
fragile HTML scraping.

### Sources that were removed (no working feed exists)
Pinecone, Modal, and Cerebras were dropped — they are JS-rendered sites that publish
**no RSS feed and no usable sitemap** (every known URL 404s). They were replaced with the
verified-live feeds above (HuggingFace, Google AI, Google Research, Together AI, BAIR).

---

## 6. The ingestion pipeline (step by step)

Entry point: `ingest_intelligence(session, context_id=None)` in `fetcher.py`.

1. **Fan-out fetch.** A single `httpx.AsyncClient` is shared across all hunters, fired
   together with `asyncio.gather`. A `context_id` (e.g. `"GitHub"`, `"AI"`) can restrict
   the run to a subset; with no context, all sources run.
2. **Flatten.** All per-source result lists are merged into one `raw_signals` list
   (~150+ dicts per full run).
3. **Score.** `_score_signals()` attaches an `engagement_score` to every signal (see §7).
4. **Rank.** `raw_signals` is sorted by score, descending. *(This replaced an old
   `random.shuffle` — selection is now signal-driven, not a lottery.)*
5. **Dedupe vs DB.** Only the URLs in this run are checked against Postgres
   (`WHERE url IN (...)`), so we never load the entire URL history into memory.
6. **Filter, near-dedupe & cap.** Walking the ranked list:
   - `is_gold()` rejects blacklisted domains and fluff-titled junk.
   - **Near-duplicate collapse:** `_is_near_dup()` drops an item whose title strongly
     overlaps (Jaccard ≥ 0.6) one already kept *from a different source* — i.e. the same
     story syndicated across feeds. Because the list is score-sorted, the highest-scored
     copy survives. Same-source overlaps are left alone (usually distinct posts).
   - `MAX_PER_SOURCE = 8` keeps any one source from dominating.
   - `MAX_TOTAL_PER_RUN = 100` caps the batch.
7. **Classify.** `classify_article()` assigns the category **once, here** — the single
   source of truth. (The analyzer no longer re-classifies.)
8. **Hydrate full content.** `_hydrate_full_content()` fetches the readable body text
   for the selected articles, `FULL_CONTENT_CONCURRENCY = 8` at a time. Aggregator
   domains (GitHub, HN, ArXiv, Lobsters, Product Hunt) are skipped because their snippet
   *is* the payload.
9. **Store.** Each survivor becomes an `Article` row (`is_processed = false`,
   `category`, `full_content` and `engagement_score` persisted), flushed individually so
   one bad row can't abort the whole batch.

### Quality gate: `is_gold()`
Rejects an item if its domain is in `DOMAIN_BLACKLIST` (medium, dev.to, linkedin, …) or
its title/name contains a `TITLE_FLUFF` word (career, interview, roadmap, tutorial, …).
**The junk filters always run first** — a high engagement count no longer buys a junk
item a free pass (the old bypass is why all-time-famous repos like `developer-roadmap`
and `awesome-*` lists used to slip in).

### GitHub "trending," specifically
The GitHub query searches for repos **`created:>` recently** (last week / last month)
sorted by stars — i.e. *young repos that already pulled real traction*, which is what
"trending" actually means. A GitHub-only junk-name filter (`GITHUB_NAME_FLUFF`) drops
newly-created list/learning repos (`awesome-*`, `*-books`, `cheatsheet`, …). Each repo's
date is set to its real `created_at` so recency scoring reflects how new the project is.

---

## 7. The scoring system

`_score_signals()` gives every candidate a single comparable number:

```
engagement_score = source_weight × (0.55 × engagement + 0.45 × recency)
```

- **engagement** — the item's `likes` (HN points / GitHub stars / Lobsters score),
  normalized **within its own source** across the current run. This is the key trick:
  GitHub stars (thousands) and HN points (hundreds) live on wildly different scales, so
  comparing them raw is meaningless. Normalizing each source to 0–1 makes them fair, and
  pure-RSS sources (which carry no number, `likes = 0`) simply lean on recency + trust.
- **recency** — exponential decay on the article's age, `exp(-age_hours / 72)`
  (a ~3-day scale). Fresh items score higher.
- **source_weight** — a hand-set trust multiplier (`SOURCE_WEIGHTS`). OpenAI/DeepMind/
  Karpathy sit highest (~1.4–1.6); aggregated tech news sits lowest (~0.9).

The score is used to **rank before selection** and is **persisted** to the
`engagement_score` column (which previously was always `0.0`).

---

## 8. The AI analysis layer

The five categories — assigned **once at ingest** by `classify_article()` (source + URL +
keyword rules), not here — are:
- **AI** — model releases, lab news, infrastructure
- **Signal** — research papers / breakthroughs (ArXiv, journals)
- **Momentum** — trending repos, expert voices
- **Discovery** — tools, launches, things you can try today
- **Concerns** — community problems, debates, discourse

Entry point: `analyze_articles(session)` in `analyzer.py`. It processes all rows where
`is_processed == false`, in batches of `BATCH_SIZE = 8` with a `BATCH_DELAY = 12s`
pause between batches (to stay under Groq rate limits). For each article:

1. **Insight** — `generate_insight()` calls Groq to write a 400–600 word, Substack-style
   summary. **It writes from the hydrated `full_content`** (falling back to the
   snippet), with the prompt context raised to 6,000 chars — so insights are grounded in
   the real article, not a one-sentence RSS blurb.
2. **Embed** — the whole batch is embedded in a single `fastembed` call (`title + insight`)
   into a 384-dim vector, stored in the pgvector column for semantic search.
3. **Trends** — after the batch loop, `update_trends()` extracts keywords **and bigrams**
   from HTML-/URL-cleaned text, weights bigrams 2× (with a min-frequency gate) so specific
   phrases ("language model") beat generic single words ("model"), and upserts a per-day
   `Trend` row — which powers day-over-day velocity ("New / Surging / Rising / Steady").

### Resilience
- `_call_groq_with_fallback()` retries on the smaller `llama3-8b-8192` model when the
  70B model is rate-limited.
- `retry_failed_insights()` re-generates insights for any article whose first pass
  failed or came back empty.

### Other AI features (on-demand, via API)
- `generate_deep_brief()` — a structured 3-part brief (Technical Primitive / Market
  Impact / Opportunity) for a single article.
- `chat_about_article()` — answers a user's question about a specific article using its
  full content + insight as context.
- `generate_chat_suggestions()` — 5 article-specific starter questions (cached 6h).
- `generate_weekly_digest()` — a "Weekly Synthesis" markdown digest from the week's top
  articles, with a deterministic fallback when the LLM is unavailable.

---

## 9. The data model

Defined in `app/models.py` (SQLModel tables):

| Table | Key fields | Purpose |
|---|---|---|
| **Article** | `id`, `url` (unique), `title`, `source`, `published_date`, `content_snippet`, `full_content`, `insight`, `category`, `is_processed`, `views`, `likes`, `engagement_score`, `embedding` (Vector 384) | The core record — one per signal |
| **Trend** | `keyword` (indexed), `count`, `trend_date` | Per-day keyword frequency for velocity |
| **Digest** | `created_at`, `content` | Stored weekly synthesis markdown |
| **SavedArticle** | `user_id` + `article_id` (composite PK) | A user's bookmarks |
| **Feedback** | `user_id`, `rating` (1–5), `comment` | User feedback submissions |

`engagement_score` and the engagement columns were added to existing databases via
`migration.py`. New databases get the full schema from `init_db()` / `create_all`.

---

## 10. The API surface

All routes are defined in `main.py`. Grouped by purpose:

### Ingestion & analysis (operational)
| Method | Route | Notes |
|---|---|---|
| POST | `/ingest` | Run a fetch. **Ops/cron only — not user-facing.** 5/hour, 6-hour global cooldown unless `context_id` given |
| POST | `/analyze` | Run the AI analysis pass over unprocessed articles |
| POST | `/retry-insights` | Re-generate failed/empty insights |

### Articles & feed
| Method | Route | Notes |
|---|---|---|
| GET | `/articles` | Cursor pagination, ordered by `id DESC` (insertion order) |
| GET | `/articles/trending` | "Hot" sort: `(views + 5·likes) / (hours+2)^1.8`, last 7 days |
| GET | `/articles/count-since?since_id=` | Lightweight "how many new" check (for the new-signals badge) |
| GET | `/articles/{id}/content` | Full body; lazily extracted + cached on first request |
| GET | `/search/semantic?query=` | pgvector cosine-distance search over embeddings |

### Per-article AI
| Method | Route | Notes |
|---|---|---|
| GET | `/brief/{id}` | Structured 3-part deep brief |
| GET | `/articles/{id}/suggestions` | 5 chat starters. 30/min, cached 6h |
| POST | `/articles/{id}/chat` | Ask a question about the article. 20/min |

### Engagement & user data
| Method | Route | Notes |
|---|---|---|
| POST | `/articles/{id}/view` | Increment view count, set `last_viewed` |
| GET | `/saved` | A user's saved articles (requires user id) |
| POST | `/articles/{id}/save` | Toggle bookmark on/off |
| POST | `/feedback` | Submit 1–5 rating + comment. 5/hour |

### Digests, trends, syndication
| Method | Route | Notes |
|---|---|---|
| GET | `/digests/latest` | Most recent weekly digest |
| POST | `/digests/generate` | Generate a new weekly digest. 3/hour |
| GET | `/trends` | Top keywords with velocity labels |
| GET | `/rss` | Public RSS 2.0 feed of the latest 20 articles |

### Health & status
| Method | Route | Notes |
|---|---|---|
| GET | `/` | Root status incl. `scheduler_running` |
| GET | `/health` | Uptime/observability: scheduler state, last-ingest result, interval |

---

## 11. Security & auth model

The backend is **not** meant to be hit directly by browsers. The SvelteKit frontend
authenticates the user (Better-Auth), then proxies API calls through an internal route
that attaches two headers:

- `X-Axon-Internal-Secret` — a shared secret (`AXON_INTERNAL_SECRET`)
- `X-Axon-User-Id` — the authenticated user's id

The `require_internal_auth` middleware (`main.py`) rejects any request missing/mismatching
these with **401**, *except* the public paths: `GET /`, `GET /health`, and CORS preflight
`OPTIONS`. FastAPI docs (`/docs`, `/openapi.json`, `/redoc`) return **404** unless
`EXPOSE_API_DOCS=true`. This is why a misconfigured
`INTERNAL_API_URL` or a secret mismatch between the two deployments shows up as
"Couldn't refresh the feed" — the proxy's call gets 401'd.

**Rate limiting** (slowapi) is keyed by `X-Axon-User-Id` (falling back to IP), so limits
are per-user. A `429` returns a friendly message + `Retry-After: 60`.

---

## 12. Scheduling & background work

- **APScheduler** registers `scheduled_ingest` on an `IntervalTrigger` (default every
  4 hours; override with `INGEST_INTERVAL_HOURS`). It runs ingest, then runs analysis
  via `asyncio.to_thread()` so the blocking Groq/sleep work never freezes the event loop.
- The scheduler **only fires while the process is alive** — it needs a long-lived host
  (container/VM), not serverless cold-starts. Set `DISABLE_SCHEDULER=1` and drive ingest
  with an external cron (e.g. Vercel Cron → frontend `/api/cron/ingest`) in serverless
  deployments.
- `INGEST_RUN_ON_STARTUP=1` queues one ingest immediately on boot.
- Scheduler status (running?, last-ingest time, ok/fail, detail) is exposed on `/health`.

**Read vs. ingest separation (important).** Ingestion — the only thing that hits external
sites — is owned exclusively by the scheduler (and the Vercel cron). A **user refreshing
the feed never triggers a scrape**: pull-to-refresh just reads the latest rows from
Postgres (`GET /articles` / `GET /articles/count-since`) and shows "up to date" when
nothing is new. This keeps user actions cheap and O(1), decouples them from slow
third-party APIs, and means the feed scales with reads, not with outbound fetches.

---

## 13. Database & vector search

`core/database.py` builds the SQLAlchemy engine from either discrete `DB_*` env vars or a
single `DATABASE_URL` (auto-rewriting the legacy `postgres://` prefix and requiring SSL
for non-local hosts). `pool_pre_ping` + `pool_recycle=300` keep pooled connections
healthy (important behind Supabase's pooler). `init_db()` tests the connection, ensures
the `vector` extension exists, and syncs the schema. Semantic search uses pgvector's
`cosine_distance` operator against the 384-dim `embedding` column.

---

## 14. Deployment

- **Docker** (`Dockerfile`) — Python 3.12 slim, non-root user, runs
  `gunicorn app.main:app -k uvicorn.workers.UvicornWorker` with 2 workers on port 8000.
  This is the recommended target because the APScheduler timer stays alive.
- **Vercel** (`vercel.json`) — deploys `app/main.py` via `@vercel/python`. Serverless,
  so the in-process scheduler won't fire reliably; pair with `DISABLE_SCHEDULER=1` + an
  external cron. Public `/health` is exempt from auth for uptime checks.
- **Local Postgres** — `docker-compose.yml` brings up a `pgvector/pgvector:pg15`
  instance for development.

---

## 15. Configuration (environment variables)

| Variable | Required | Purpose |
|---|---|---|
| `AXON_INTERNAL_SECRET` | **yes** | Shared secret the frontend proxy must send; app refuses to start without it |
| `GROQ_API_KEY` | yes (for AI) | Groq LLM access; insights go offline without it |
| `DATABASE_URL` *or* `DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT`/`DB_NAME` | yes | Postgres connection |
| `GITHUB_TOKEN` / `GITHUB_AUTH_STYLE` | optional | Raises GitHub API rate limits (`token` vs `bearer` PAT style) |
| `INGEST_INTERVAL_HOURS` | optional (def 4) | Scheduler cadence + manual-ingest cooldown |
| `DISABLE_SCHEDULER` | optional | Turn off the in-process timer (serverless) |
| `INGEST_RUN_ON_STARTUP` | optional | Queue one ingest on boot |
| `CORS_ALLOWED_ORIGINS` | optional | Comma-separated allowed origins |
| `DB_ECHO` | optional | Log SQL when `true` |

---

## 16. Known limitations & open threads

### Resolved
- ✅ **Near-duplicate dedupe.** A title-overlap (Jaccard) check now collapses the same
  story syndicated across feeds within a run, keeping the highest-scored copy (§6).
- ✅ **Single categorization.** Category is assigned once at ingest; the analyzer no
  longer overwrites it (§6, §8).
- ✅ **Phrase-aware trends.** `update_trends()` now extracts bigrams from cleaned text and
  weights them above generic single words, with HTML/URL markup stripped out (§8).
- ✅ **Anthropic source added.** Ingested via `sitemap.xml` (no RSS exists) with clean
  titles/snippets pulled from each page's `og:title` + meta description (§5).

### Still open (candidates for the next iteration)
1. **Cross-run / semantic dedupe.** The current near-dup check is title-based and scoped
   to a single ingest run. A story re-appearing days later, or worded very differently
   across sources, isn't caught — the stored embeddings could power a stronger pass.
2. **Spam/low-quality repos.** The GitHub fix removed evergreen junk, but star-farmed
   SEO repos can still appear; no reputation/quality signal beyond the name filter.
3. **ArXiv firehose.** Latest `cs.AI`/`cs.LG` by date only — no relevance/citation
   ranking.
4. **Analysis cost/time.** A full run can be ~100 articles × Groq calls with 12s batch
   gaps — fine on a long-lived host, but heavy for short serverless timeouts.

---

*This document reflects the backend as built in `app/` and is intended to stay current —
update it whenever a source, pipeline stage, model, or endpoint changes.*
