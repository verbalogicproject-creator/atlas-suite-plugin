# Evidence-Rules Atlas contract

- Flag: `evidence-rules`
- Facet: `standing` (`eligible`, `candidate`, `quarantined`, `rejected`, `unknown`)
- Shared evidence states: `validated`, `built`, `observed`, `hypothesized`, `open`
- Invalidation chain: source → transformation → chunk → facet → graph → index → rerank cache → answer plan → answer
- Receipt journal: append-only and hash-chained; hash chains are tamper-evident, not external notarization
- Proof limit: governance and integrity context; approval stays human-owned
