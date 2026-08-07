---
name: knowledge-atlas
description: Build or query governed entities, claims, relations, contradictions, provenance, evidence packets, and answer plans. Use for deterministic KG-RAG, source-grounded research, knowledge lifecycle, or the knowledge flag and kg-rag/release-review presets.
---

# Knowledge Atlas

Treat canonical claims and provenance as governing; SQLite and vectors are
rebuildable projections.

1. Inspect the source ledger, standing, lifecycle, ontology/shapes, aliases,
   contradictions, deletion rules, and current Knowledge receipt.
2. Preview the exact `knowledge` flag or requested preset through
   `../../scripts/dkg_bridge.py atlas plan`.
3. Build only requested Atlases. Quarantine model-proposed aliases until
   deterministic or human validation.
4. Query through `dkg query`; retain the plan, body-free trace, cited evidence
   packet, contradictions, uncertainty, and abstention/refusal disposition.
5. Generate only from a deterministic answer plan. Reject undeclared claims,
   unresolved citations, and new facts; allow at most one constrained repair.

Read `references/contract.md`. Semantic and reranker channels are explicit
opt-in declarations until qualified. Evidence supplies context, not authority.
