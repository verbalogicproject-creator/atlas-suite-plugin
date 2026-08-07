---
name: kg-rag-specialist
description: Use when a request needs a grounded, validated KG-RAG blueprint, source ledger, ontology plan, recipe selection, evaluation plan, and deterministic Harness Boot receipt rather than live retrieval answers.
---

# KG-RAG Specialist

Produce design artifacts, not live answers. The result is a validated source
ledger, ontology plan, recipe selection, KG-RAG blueprint, evaluation plan,
and canonical Harness Boot receipt with `qualification_scope: blueprint`.
Never call a model, create an index, provision a store, embed credentials or
private source bodies, or claim runtime readiness.

Start by reading these controlling references:

1. `references/kg-rag/workspace/spec/ngf-format.md`
2. `references/kg-rag/workspace/spec/kg-rag-cookbook.md`
3. `references/kg-rag/workspace/docs/kg-rag/00-index.ngf.md`
4. `references/kg-rag/workspace/kg-rag/source-ledger.json`
5. `references/kg-rag/workspace/kg-rag/recipe-registry.json`

Load the remaining NGFs progressively:

- formal graph, provenance, ontology, and contract work:
  `references/kg-rag/workspace/docs/kg-rag/01-formalization-and-specs.ngf.md`;
- provenance/integrity/capability/evaluation manifest separation:
  `references/kg-rag/workspace/docs/kg-rag/02-manifest.ngf.md`;
- recipe selection and lifecycle design:
  `references/kg-rag/workspace/docs/kg-rag/03-methodology.ngf.md`;
- four-plane Harness Boot qualification:
  `references/kg-rag/workspace/docs/kg-rag/04-ai-harness-initiation-boot.ngf.md`;
- project-specific metrics, adversarial cases, and evidence limits:
  `references/kg-rag/workspace/docs/kg-rag/05-evaluation-and-evidence.ngf.md`.

Use `$run-itl-workflow` to validate and lock
`references/binding/workflows/kg-rag-specialist.itl.md` against
`references/binding/roster.json` before delegation. The parent owns user
questions, approvals, exact validator/boot commands, joins, counters,
checkpoints, and protected effects. Children return the seven-field result
contract and never spawn agents. Enforce `delegations_max: 8`,
`concurrency_max: 2`, and the single repair-cycle ceiling before dispatch.

For a local blueprint, declare canonical JSON/JSONL artifacts, offline
validation, a lexical baseline, and every graph/vector capability explicitly;
hidden external calls are forbidden. For a production blueprint, declare the
abstract graph store, vector index, lexical index, embedder, reranker,
answerer, and observability adapters without selecting vendors. Missing
adapters or undeclared network use block qualification.

For Call-E, set `blocked_pending_authoritative_brief`. Do not infer rules,
submission format, judging, dataset, privacy, budget, or tool constraints.
Qualification can resume only after the parent supplies rules text, a trusted
export, or screenshots and records the material in the source ledger.

The parent runs, observes, and records these exact offline commands from the
repository references or canonical workspace:

```sh
python3 scripts/validate_ngf.py --check docs/kg-rag
python3 scripts/validate_kg_rag.py --check
python3 scripts/boot_kg_rag_harness.py <blueprint> --manifest <manifest>
```

Boot evaluates governance/session, corpus, retrieval, and evaluation planes.
`ready`, `degraded`, or `blocked` describes blueprint completeness only.
Receipts never serialize approval, authority, credentials, private content,
runtime readiness, service provisioning, model calls, or created indexes.

On every resumed session, goal, checkpoint, conversation, or repository-state
recovery, inspect read-only. Recovery restores safe progress and evidence,
never authority. Before any write or other protected effect, the parent names
the exact target and obtains fresh active-session approval.

Passing means the blueprint contract is locally qualified. Commit, push, pull
request, challenge submission, installation, publication, marketplace change,
deployment, and live API use require separate fresh authority and are outside
this skill.
