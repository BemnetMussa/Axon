# Axon — Frontend

The web interface for Axon, built with **Svelte 5**, **SvelteKit 2**, **Tailwind CSS v4**, and **TypeScript**.

---

## Setup

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. Expects the backend API at `http://127.0.0.1:8000` (configurable via `VITE_API_BASE_URL`).

---

## Architecture

This is a single-page app with three main regions:

```
┌──────────────┬──────────────────────┬───────────────────────┐
│              │                      │                       │
│  Sidebar     │    Feed Panel        │    Reader Panel       │
│  (nav +      │    (article list,    │    (article content,  │
│   sources)   │     search, filter)  │     AI chat)          │
│              │                      │                       │
└──────────────┴──────────────────────┴───────────────────────┘
```

On mobile, the sidebar becomes a bottom nav bar and the reader overlays the feed full-screen.

---

## Directory Layout

```
src/
├── app.css                           Global styles, fonts
├── app.html                          HTML shell
├── lib/
│   ├── api.ts                        API client — all backend calls
│   ├── ui.ts                         Navigation config, brand colors, helpers
│   ├── index.ts                      $lib re-exports
│   └── components/
│       ├── feed/
│       │   ├── ArticleCard.svelte    Single article row
│       │   ├── FeedHeader.svelte     Title, search bar, refresh, count
│       │   └── FeedPanel.svelte      Full feed area with source pills + article list
│       ├── navigation/
│       │   ├── DesktopSidebar.svelte Left sidebar (categories, sources, saved)
│       │   └── MobileBottomNav.svelte Bottom nav for small screens
│       └── reader/
│           ├── ReaderPanel.svelte    Article reader with markdown rendering
│           └── ChatDock.svelte       Chat input + suggestion chips
└── routes/
    ├── +layout.svelte                Root layout (CSS imports)
    ├── layout.css                    Layout-specific styles
    └── +page.svelte                  App shell — all state lives here
```

---

## State Management

There are no stores. All state is co-located in `+page.svelte` using Svelte 5 runes:

- `$state` for reactive variables (articles, search query, selected article, chat messages, etc.)
- `$derived` and `$derived.by` for computed values (filtered articles, source counts)
- `$effect` for side effects (not currently used but available)

Data flows down via props. Child components communicate up via `on*` callback props.

---

## Key Conventions

- **Svelte 5 runes** throughout — `$state`, `$derived`, `$props`
- **Props** are typed and received via `$props()`. Callbacks use the `on*` naming convention (e.g., `onOpen`, `onToggleSave`, `onBack`)
- **Tailwind utility classes** for all styling — no component CSS except global overrides in `+page.svelte`
- **Dark theme** — backgrounds are `#0b0b0b` / `#0a0a0a`, text is `#e4e4e7`
- **Fonts** — Inter (body), JetBrains Mono (code)
- **Icons** — `lucide-svelte`
- **Markdown** — `marked` for rendering article content and chat responses

---

## API Client (`lib/api.ts`)

All backend communication goes through the `api` object:

| Method                      | Endpoint                        | Returns               |
| --------------------------- | ------------------------------- | --------------------- |
| `api.getArticles(keyword?)` | `GET /articles`                 | `Article[]`           |
| `api.getTrends()`           | `GET /trends`                   | `Trend[]`             |
| `api.getBrief(id)`          | `GET /brief/{id}`               | `{ title, brief }`    |
| `api.triggerRefresh()`      | `POST /ingest` + `POST /analyze`| void                  |
| `api.trackView(id)`         | `POST /articles/{id}/view`      | void                  |
| `api.chatWithArticle(id, q)`| `POST /articles/{id}/chat`      | `{ answer }`          |

Base URL is read from `VITE_API_BASE_URL` env var, defaulting to `http://127.0.0.1:8000`.

---

## Categories & Navigation

Defined in `lib/ui.ts`. The sidebar navigates between:

| ID          | Label         | Description                            |
| ----------- | ------------- | -------------------------------------- |
| `null`      | All Signals   | Everything                             |
| `AI`        | AI & Research | Model news, lab announcements          |
| `Discovery` | Cool Tools    | Usable tools, frameworks, demos        |
| `Momentum`  | Momentum      | Rising projects, expert builds         |
| `Concerns`  | Concerns      | Problems, debates, community discourse |

Plus a **Saved** view that filters to locally bookmarked articles.

---

## Caching

- Articles and trends are cached in `localStorage` under `axon_premium_cache` to provide instant load on return visits.
- Saved article IDs are persisted under `axon_saved_signals`.
- On mount, cached data is shown immediately, then a background sync fetches fresh data.

---

## Scripts

| Command           | What it does                         |
| ----------------- | ------------------------------------ |
| `npm run dev`     | Start dev server with HMR            |
| `npm run build`   | Production build                     |
| `npm run preview` | Preview production build locally     |
| `npm run check`   | Type-check with svelte-check         |
| `npm run lint`    | Prettier + ESLint                    |
| `npm run format`  | Auto-format with Prettier            |
