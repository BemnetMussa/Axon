---
name: Ranking miss
about: A story the filter should have kept, or should have cut
title: "Ranking miss: "
labels: ranking
---

**Story**
Title and link:

**What happened**
- [ ] It was cut, but should have been kept
- [ ] It was kept, but should have been cut
- [ ] It was kept, but ranked too high or too low

**Why**
What makes it signal (or noise)?

**Which rule is at fault?** (optional)
- [ ] Score: traction, freshness, or source trust
- [ ] New / Recent
- [ ] Not junk (domain or title filter)
- [ ] Not a repeat (dedupe)
- [ ] Under quota (5 per source, 20 per sweep)
- [ ] Not sure

Rules are in `backend/engine/fetcher.py`.
