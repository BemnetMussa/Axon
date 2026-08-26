# Contributing to Axon

Axon is open-core. The curation engine and this monorepo are proprietary.

## How to help today

- Try the [live demo](https://axon-phi-ruby.vercel.app) and share feedback
- Report bugs or ideas on X: [@BemnetMussa](https://x.com/BemnetMussa)

Public contributions to the proprietary engine are not open yet. If a public client repository is published later, contribution guidelines will live there.

## Collaborators

If you have private-repo access:

1. Clone the repository
2. Follow the [Quick Start](README.md#quick-start)
3. Branch from `main`: `git checkout -b feature/your-feature`

## Development setup

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

```bash
cd backend
docker compose up db -d
```

## Making changes

### Code style

**Backend (Python):**
- Follow PEP 8
- Use type hints for function signatures
- Keep services modular — ingestion in `fetcher.py`, AI in `analyzer.py`, extraction in `extractor.py`

**Frontend (Svelte/TypeScript):**
- Prefer Svelte 5 runes
- Keep components small and focused
- Run `npx svelte-check` before opening a PR

### Tests

```bash
# Backend
cd backend && pip install -r requirements-dev.txt && python -m pytest

# Frontend
cd fronted && npm test
```

## Pull requests

- Keep PRs focused on one change
- Describe what and why
- Note any env or migration steps

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## Questions

- [@BemnetMussa](https://x.com/BemnetMussa)
- [OPEN_CORE.md](OPEN_CORE.md) for licensing
