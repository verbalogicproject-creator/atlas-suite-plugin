---
spec_version: 0.4.1
---

# Knowledge-graph retrieval-augmented generation cookbook

This contract defines a provider-neutral, blueprint-only cookbook for describing
knowledge-graph retrieval-augmented generation systems. It is subordinate to
the repository authority, evidence, orchestration, and NGF contracts.

## Scope and vocabulary

A **knowledge graph** is a set of identified nodes and typed directed edges. A
**record** is an addressable source unit. A **claim** is a proposition derived
from one or more records. A **provenance path** connects a claim or result to
its records and transformations. A **retrieval plan** selects bounded graph and
text evidence for a query. A **blueprint** is a declarative plan and is not an
executed system. A **receipt** is a canonical record emitted by offline
qualification of a blueprint.

The cookbook covers formalization, manifests, recipes, methodology, Harness
Boot, and evaluation. It excludes a live retrieval service, index provisioning,
credentials, private corpus bodies, generated answers, permanent processes,
and protected external effects.

## Canonical asset separation

The source ledger, recipe registry, framework manifest,
blueprint, and qualification manifest MUST be separate closed data artifacts.
The source ledger MUST classify grounding sources and is the source-provenance,
consent/licensing, retention, and deletion manifest for this blueprint-only
version. It MUST NOT embed private source bodies or claim to be a runtime
claim-derivation ledger. The recipe registry MUST define reusable capability
requirements. The framework manifest MUST select one neutral profile and its
available capabilities. A blueprint MUST select recipes and declare all inputs,
limits, policies, and expected evidence. The qualification manifest MUST pin
the artifacts and criteria used to interpret a canonical receipt.

Unknown fields, identifiers, profiles, recipes, states, or verdicts MUST fail
closed. All referenced paths MUST be safe repository-relative paths. Canonical
JSON MUST be UTF-8, use sorted keys and compact separators, and end in one line
feed. Digests MUST be lowercase SHA-256 values over exact bytes.

## Graph, retrieval, and provenance invariants

Any later runtime artifact containing a graph or retrieved result MUST satisfy
the following invariants; v1 declares and validates the policy but does not
claim that such an artifact exists. Node and edge identifiers MUST be unique within a graph snapshot. Every edge
endpoint MUST resolve to a declared node. Every retrieved unit MUST resolve to
a record, and every answer-supporting claim MUST have at least one provenance
path to a record. Transformations MUST identify their inputs and outputs.
Cycles MAY occur in the domain graph but MUST NOT occur in a provenance
derivation path.

A retrieval plan MUST declare seed selection, traversal direction, maximum
depth, maximum candidates, ranking policy, context budget, and empty-result
behavior. Ordering ties MUST resolve by stable identifier. Truncation MUST be
recorded. A result with incomplete mandatory provenance MUST fail rather than
silently degrade.

## Profiles and recipes

The two qualifying neutral profiles are `local-deterministic` and
`production-adapter`. `local-deterministic` describes offline deterministic
blueprint qualification. `production-adapter` describes declared adapter
compatibility but does not by itself prove that any adapter or external
dependency is ready. The reserved `call-e` profile is separately blocked.

The canonical recipe registry MUST contain exactly eighteen ordered recipe
identifiers. Each recipe MUST declare inputs, outputs, capability requirements,
failure behavior, provenance obligations, evaluation dimensions, and profile
compatibility. Selection MUST fail when the framework manifest lacks a required
capability.

The ordered identifiers are `source-intake`, `ontology-design`, `chunking`,
`entity-relation-extraction`, `entity-resolution`, `graph-construction`,
`lexical-vector-indexing`, `query-classification`, `graph-traversal`,
`community-global-retrieval`, `hybrid-fusion`, `reranking`,
`evidence-packet-assembly`, `cited-answering`, `contradiction-handling`,
`abstention`, `update-deletion-reindexing`, and `adversarial-evaluation`.

`Call-E` is a reserved qualification call. It MUST remain `blocked` until its
authoritative brief is represented by a resolvable controlling entry in the
source ledger. Inference from adjacent calls or explanatory material MUST NOT
unblock it.

## Harness Boot

Harness Boot MUST evaluate four planes in order: governance/session, corpus,
retrieval, and evaluation. Each plane MUST produce a deterministic verdict and
reason codes. A failed or blocked plane MUST prevent later planes from claiming
readiness. Repeating Boot over byte-identical inputs MUST produce byte-identical
receipts.

Governance/session checks intent, authority boundaries, privacy, licenses,
consent, budgets, retention, secret exclusion, and the reserved-call rule.
Corpus checks source integrity, ontology and shapes, extraction policy,
freshness, deletion, and reindexing. Retrieval checks adapter declarations,
recipe compatibility, query routes, traversal, fusion, fallback, citations,
and abstention. Evaluation checks fixtures, mandatory metrics, project-specific
thresholds, baseline state, adversarial cases, and evidence policy.

## Evaluation and verdicts

Evaluation criteria MUST declare metric identifiers, populations, aggregation,
threshold direction, threshold value, rationale, sample sufficiency, and
uncertainty or tolerance policy before results are scored. Required dimensions
are retrieval recall and precision, ranking, entity resolution, triple and path
validity, citation precision and coverage, factual consistency, contradiction
response, abstention, freshness and deletion, latency, cost observability,
injection refusal, and protected-effect refusal. Thresholds MUST be
project-specific; this contract does not invent a universal quality boundary.
A criterion without sufficient observations MUST be `not_observed`, not passed.

The closed verdict vocabulary is `passed`, `failed`, `blocked`, and
`not_observed`. A receipt MUST not reinterpret historical evidence collected
against a different revision, manifest digest, corpus snapshot, or threshold
set as current evidence.

## Authority and proof boundary

Blueprint validation and Harness Boot MAY read declared local artifacts and
write only an explicitly authorized local receipt target. They MUST NOT perform
network access, create an index, invoke an external dependency, access
credentials, send content, deploy, publish, or convert recovered context into
authority.

A valid blueprint and a passed receipt prove only that the declared local
artifacts satisfy the cookbook's structural and deterministic offline checks.
They do not prove live retrieval quality, generated-answer quality, operational
readiness, safety in deployment, availability, or completion of any protected
effect.
