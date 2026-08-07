---
name: kg-rag-specialist
description: Produce and validate source-grounded deterministic KG-RAG blueprints, ledgers, ontologies, recipes, evaluation plans, evidence boundaries, and blueprint-scoped Harness Boot receipts. Use for KG-RAG architecture or qualification, not live retrieval answers.
---

# KG-RAG Specialist

Produce design and qualification artifacts, not live answers. Preserve the
installed 0.4.1 baseline under `references/kg-rag`; its controlling 18-recipe
cookbook remains unchanged. Read `references/baseline-manifest.json` before
relying on baseline identity.

Start with:

1. `references/kg-rag/workspace/spec/ngf-format.md`
2. `references/kg-rag/workspace/spec/kg-rag-cookbook.md`
3. `references/kg-rag/workspace/docs/kg-rag/00-index.ngf.md`
4. `references/kg-rag/workspace/kg-rag/source-ledger.json`
5. `references/kg-rag/workspace/kg-rag/recipe-registry.json`
6. `references/deterministic-rag-kb/v1/index.md`

Build a closed source ledger, ontology/shapes, route registry, capability
manifest, lifecycle/invalidation policy, frozen thresholds, adversarial cases,
and evidence/answer-plan boundary. Defaults are lexical, graph-local, and
deterministic graph aggregates with RRF `k=60`; semantic and reranking remain
explicit opt-ins. Keep candidate recipes outside the controlling 18 until a
future schema revision.

Validate the preserved baseline with its bundled scripts. Validate the new KB
with `scripts/validate_deterministic_kb.py`. When the paired framework is
available, run `../../scripts/dkg_bridge.py qualify fixture <fixture>` and
`../../scripts/dkg_bridge.py boot` for runtime-scoped local evidence. Do not
confuse that with the specialist's blueprint-scoped Harness Boot receipt.

Never call a model, create an index, start a server, use a live connector,
embed credentials/private bodies, or claim runtime readiness without separate
exact authority and observed evidence. Commit, installation, marketplace
change, publication, deployment, and live API use remain outside this skill.
