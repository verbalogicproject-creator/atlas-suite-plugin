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
the five-Atlas ledger. On-demand context ranking can select any indexed file,
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
