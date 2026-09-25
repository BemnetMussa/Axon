# Contributing to Axon

Thanks for helping. Axon is **open-core**: the UI, docs, and API shell welcome
contributions. The curation + AI analysis engine stays proprietary
([OPEN_CORE.md](OPEN_CORE.md)).

## Ways to help

| Area | Welcome? | Notes |
|------|----------|--------|
| UI / PWA / accessibility | Yes | `fronted/` |
| Docs, README, examples | Yes | Keep claims honest |
| API shell / models / extractor | Yes | No proprietary prompts |
| Bug reports & product feedback | Yes | Issues or [@BemnetMussa](https://x.com/BemnetMussa) |
| Curation filters, ranking, AI prompts | No | Proprietary — not accepted as PRs |
| Secrets, keys, production configs | No | Never commit |

## Before you start

1. Try the [live demo](https://axon-phi-ruby.vercel.app)
2. Skim [OPEN_CORE.md](OPEN_CORE.md) and [NOTICE](NOTICE)
3. Open an issue for larger changes so we can align scope

## Development setup

### Frontend

```bash
cd fronted
npm install
cp .env.example .env   # point at local API or demo
npm run dev
```

### Backend (API shell)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Without `private/services/*.py`, ingest/analyze use **community stubs** (safe no-ops).
That is expected for public contributors. The hosted product still serves real signals.

### Tests

```bash
cd backend && pip install -r requirements-dev.txt && python -m pytest
cd fronted && npm test
```

## Pull requests

- One focused change per PR
- Describe what and why
- Run checks you can (`svelte-check`, `pytest`)
- Do not include `.env`, credentials, or anything under `private/`

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Questions

[@BemnetMussa](https://x.com/BemnetMussa)
