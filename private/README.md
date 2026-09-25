# Private overlay (gitignored)

This folder holds the **proprietary** curation + AI analysis engine on maintainer machines.

Drop these files here (they are ignored by git):

- `services/fetcher.py`
- `services/analyzer.py`

The open loaders in `backend/app/services/fetcher.py` and `analyzer.py` import them when present.
Without them, community stubs keep the API shell bootable.

Do not commit secrets, prompts, or this overlay.
