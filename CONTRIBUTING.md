# Contributing to Axon

Thanks for helping. Everything is open, including the curation engine and the
AI prompts.

## Ways to help

| Area | Where |
|------|-------|
| UI / PWA / accessibility | `fronted/` |
| Ranking, filters, sources, dedupe | `backend/engine/fetcher.py` |
| AI prompts and analysis | `backend/engine/analyzer.py` |
| API / models / extractor | `backend/app/` |
| Docs, README, examples | Keep claims honest |
| Bug reports, ranking misses, feedback | Issues or [@BemnetMussa](https://x.com/BemnetMussa) |

For ranking or source changes, include a few real stories the change would
have kept or dropped — that's how we judge whether it helps.

## Before you start

1. Try the [live demo](https://axon-phi-ruby.vercel.app)
2. Open an issue for larger changes so we can align scope

## Development setup

### Frontend

```bash
cd fronted
npm install
cp .env.example .env   # point at local API or demo
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Set `GROQ_API_KEY` in `backend/.env` for AI insights; ingest runs without it.

### Tests

```bash
cd backend && pip install -r requirements-dev.txt && python -m pytest
cd fronted && npm test
```

## Pull requests

- One focused change per PR
- Describe what and why
- Run checks you can (`svelte-check`, `pytest`)
- Do not include `.env` files or credentials
- Contributions are licensed under [AGPL-3.0](LICENSE)

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Questions

[@BemnetMussa](https://x.com/BemnetMussa)
