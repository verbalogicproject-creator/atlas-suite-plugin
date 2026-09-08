# Architecture and authority

Status: implemented thin plugin candidate

```text
Codex request
    │
    ├─ one namespaced Atlas skill ─┐
    ├─ explicit multi-Atlas preset ├─ scripts/dkg_bridge.py
    └─ KG-RAG Specialist ──────────┘          │
                                      paired dkg CLI/resolver
                                               │
                             canonical snapshots/plans/receipts
```

Skills supply procedure and proof boundaries. The bridge adds the paired
framework `src` directory to the current process, then calls `dkg.cli.main`
with unchanged arguments. Therefore plugin and CLI plan/receipt semantics
cannot drift through a second implementation. If the paired framework is not
found, the plugin fails visibly and performs no fallback.

Before import, the bridge validates framework `>=0.3.0,<0.4.0`,
`dkg-framework-interface/1.0`, `dkg-cli/1.0`, and the required Atlas, domain,
qualification, API-schema, four-file, read-backend, and canonical 16-query
capabilities. Domain mining, ranking, candidate validation, backend execution,
and API projection remain framework modules; the plugin adds only agent-facing
skills, unchanged-argument access, menu access, and parity tests.

The agent surface is organized by task rather than repository ownership:
orientation uses `atlas context` or `repo-orientation`; audit uses domain and
evidence routes; architecture inspection uses record and graph reads;
implementation tracing uses `record.get`, `graph.walk`, and
`provenance.trace`; impact uses `atlas impact` or `impact.analyze`; extraction
uses domain mining and `record.list`; bounded task context uses `atlas context`
or `context.compile`; and frontend generation uses `atlas build`. Backend
results expose signed source anchors, explicit empty/abstain outcomes, and
pre-read safety refusal. The governed query route retains the same boundary.

Project Atlas frontend generation is a two-stage pipeline. The deterministic
compiler owns the exact four-file public bundle: `index.html`,
`project-atlas.json`, `content.json`, and `design.css`; receipts and the compact
context map remain under the external state root. Validated `design.css` bytes
are embedded and digest-bound in `index.html` so Android `content://` and
offline direct-file opening retain the complete visual design. The optional
`atlas-frontend-designer` proposes only editable content and CSS presentation.
Deterministic rebind regenerates `index.html` and rejects changes to canonical
JSON, IDs, source digests, proof limits, schema markers, or authority data.

`index.html` is an agent-first orientation map. It exposes bounded task routes,
file reading order, selection reasons, estimated context cost, omissions, and
the five-Atlas ledger. Its canonical JSON also carries the declaration-only
API-schema projection exposed in the HTML API Contracts section. On-demand
context ranking can select any indexed file,
including files omitted from the concise default routes.
The detailed contract is in `release-docs/project-atlas-frontend-pipeline.md`.

Each Atlas skill defaults to its single exact flag. Presets may be used only
when the user requested the complete visible combination. No skill silently
runs a dependency Atlas. The five skills share the canonical DKG contracts but
keep their domain/facet and proof boundaries explicit.

The KG-RAG Specialist preserves the installed in-the-loop 0.4.1 baseline for
comparison. Its original skill/agent files, references, validators, workflows,
schemas, fixtures, recipe registry, and controlling 18-recipe cookbook are
copied under the new namespace. `references/baseline-manifest.json` pins the
source identity. A separate deterministic-RAG KB v1 extends guidance without
altering the cookbook.

Context, model output, retrieval, MCP, skills, and receipts never grant effect
authority. The plugin cannot enable a connector, start a model, install itself,
commit, publish, deploy, or modify a marketplace without a separate active
request naming that exact effect.

The qualification layer under `qualification/` adds a two-axis capability
registry, closed JSON profiles, proof plans, frozen fixtures, and candidate
receipts. `scripts/qualification_core.py` owns only deterministic discovery and
validation. Profile routing happens before DKG resolution so `profile list`,
`describe`, and `explain` work without importing the engine; adapter-aware
`plan` reports missing paired contracts without executing them. The DKG remains
the graph/RAG engine, and In-the-Loop remains the workflow authority.

Qualification receipt v2 binds each result to canonical source/fixture files,
the complete paired-DKG bridge identity when applicable, the authoritative
In-the-Loop linter/contract identity, runtime and root environment, and a
separately signed standalone local replay-verification artifact. The verifier
runs as a different process: it repeats the full-stack suite or rebuilds and
queries isolated RAG state while resolving citation source hashes. Read-only qualification
recomputes those bindings. Drift is reported as stale/ineligible; it never
silently reuses a passing receipt.
