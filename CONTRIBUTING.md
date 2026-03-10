# Contributing to Axon

Thanks for your interest in contributing! Axon is an open-source intelligence feed for builders, and contributions of all kinds are welcome — code, docs, bug reports, feature ideas.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. Follow the [Quick Start](README.md#quick-start) guide to get the project running
4. Create a branch from `main`: `git checkout -b feature/your-feature`

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Add your GROQ_API_KEY
uvicorn app.main:app --reload
```

### Frontend

```bash
cd fronted
npm install
npm run dev
```

### Database

Start PostgreSQL via Docker:

```bash
cd backend
docker compose up db -d
```

## Making Changes

### Code Style

**Backend (Python):**
- Follow PEP 8
- Use type hints for function signatures
- Keep services modular — ingestion in `fetcher.py`, AI in `analyzer.py`, extraction in `extractor.py`
- Use SQLModel for all database models

**Frontend (Svelte/TypeScript):**
- Use Svelte 5 runes (`$state`, `$derived`, `$props`) — no legacy stores
- All state lives in `+page.svelte`, passed down as props
- Use Tailwind CSS for styling — no separate CSS files for components
- Run `npx svelte-check` before committing to catch type errors

### Commit Messages

Write clear, concise commit messages:
- `add: new data source for TechCrunch RSS`
- `fix: article card overlap on mobile`
- `update: improve classification logic in analyzer`

### Testing Your Changes

Before submitting a PR:

```bash
# Backend — verify imports
cd backend && python -c "from app.main import app"

# Frontend — type check
cd fronted && npx svelte-check
```

## Submitting a Pull Request

1. Push your branch to your fork
2. Open a PR against `main`
3. Fill in the PR template — describe what changed and why
4. Wait for review — we'll try to respond within a few days

## What to Work On

Check the [issues](https://github.com/bemnetmussa/axon/issues) for tasks labeled:
- `good first issue` — great for first-time contributors
- `help wanted` — areas where we need the most help
- `enhancement` — feature ideas

### High-Impact Areas

- **New data sources** — add feeds from more tech/AI sources
- **Smarter classification** — improve `analyzer.py` category logic
- **Accessibility** — screen reader support, keyboard navigation
- **Tests** — unit tests for backend services, component tests for frontend
- **Deployment guides** — Vercel, Railway, Fly.io, Coolify
- **Internationalization** — multi-language support

## Reporting Bugs

Open an issue using the **Bug Report** template. Include:
- Steps to reproduce
- Expected vs actual behavior
- Browser/OS if it's a frontend issue
- Relevant logs or screenshots

## Suggesting Features

Open an issue using the **Feature Request** template. Describe:
- The problem you're solving
- Your proposed solution
- Any alternatives you've considered

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold a welcoming, respectful environment.

## Questions?

- Open a [discussion](https://github.com/bemnetmussa/axon/discussions) or issue
- Reach out on Twitter: [@BemnetMussa](https://x.com/BemnetMussa)
