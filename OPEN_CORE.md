# Open-core

Axon is **open-core**: the reading experience and API shell are open so builders
can learn, contribute, and self-host a UI against the public contracts. The
curation engine and AI analysis that make Axon “Healthy Signals” stay proprietary.

## Why this split

Most AI catch-up products are closed newsletters (big audiences, little you can
fork) or thin indie aggregators. Axon opens the **product surface** people touch
and contribute to — UI, docs, API shell — while keeping the **signal quality**
moat closed.

## Open (MIT)

- Client UI (`fronted/`) — feed, reader, PWA shell
- API shell — routes, models, content extraction helpers
- Community stubs — `fetcher_community.py`, `analyzer_community.py`
- Docs, contributing guide, security policy

## Proprietary

- Hosted product (accounts, sync, production feed)
- Curation engine (ingestion, source selection, filters, dedup, ranking)
- AI analysis (prompts, insights, digests, article chat)
- Admin / schedulers / secrets
- Local-only overlay: `private/services/` (gitignored)

## Local maintainer setup

On machines that run the full product:

```text
private/services/fetcher.py   # full engine
private/services/analyzer.py
```

A backup outside git lives at `~/Documents/Projects/Axon-proprietary/`.

## Try Axon

- **Live demo:** [axon-phi-ruby.vercel.app](https://axon-phi-ruby.vercel.app)
- **Feedback / support:** [@BemnetMussa](https://x.com/BemnetMussa)

## License

- Open package: [LICENSE](LICENSE) (MIT)
- Boundary: [NOTICE](NOTICE)
