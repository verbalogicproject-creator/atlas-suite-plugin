# Operations and dogfood

## Validate without installing

From the plugin root:

```sh
python3 scripts/generate_release_docs.py
python3 scripts/generate_release_docs.py --check
python3 skills/kg-rag-specialist/scripts/validate_deterministic_kb.py
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error::ResourceWarning python3 -m unittest discover -s tests -v
```

Qualification-specific checks and canonical candidate-artifact regeneration:

```sh
./scripts/atlas profile list
./scripts/atlas profile plan fullstack-contract-spine
PYTHONDONTWRITEBYTECODE=1 python3 scripts/qualification_receipts.py
DKG_FRAMEWORK_ROOT=/path/to/deterministic-kg-rag-framework \
ATLAS_AI_RUNTIME_ARTIFACT=qualification/ai-control-plane/runs/ai-control-plane-frozen-1/runtime.json \
PYTHONDONTWRITEBYTECODE=1 python3 scripts/qualification_receipts.py --write
PYTHONDONTWRITEBYTECODE=1 python3 scripts/qualification_ai_control_plane.py \
  verify qualification/ai-control-plane/runs/ai-control-plane-frozen-1/runtime.json
```

The first command family is always read-only. `--write` changes only the
declared candidate result, separately signed standalone-replay verification, and receipt
files under `qualification/`; use it after intentional source or fixture
changes. It does not promote claims or produce a release receipt. The local
verifier runs as a distinct read-only process, repeats the frozen qualification,
and rejects semantically tampered producer results; it is not an external trust domain.
The stored AI runtime artifact is a single-run, source- and host-bound
historical observation. Its original absolute temporary paths are retained as
observation facts, but new source, adapter, DKG, and In-the-Loop bindings use
repository-local or `dependency/...` logical identities. Regeneration requires fresh active-session approval for the exact
temporary repair target and must set `ATLAS_AI_RUNTIME_ARTIFACT` explicitly;
ordinary replay without that variable fails closed to runtime absence. If
the exact optional In-the-Loop 0.4.1 qualification contract is wholly absent,
replay emits the typed `itl-qualification-contract-unavailable` failed AI
candidate; profile qualification marks prior AI evidence stale and
non-promotable. Partial, symlinked, malformed, tampered, and stale-lock
conditions are not converted to availability and still fail closed.

Also run the plugin manifest validator and the skill-creator quick validator
from their installed development-tool locations against each of the seven
repository-relative skill directories. Record the exact validator identities
and outputs in the closure evidence; do not encode a device-specific path in
this repository.

The copied baseline validators run from
`skills/kg-rag-specialist/references/kg-rag/workspace` or through the exact
commands in the specialist skill. They qualify blueprint artifacts only.

## CLI/plugin parity

Run direct and bridged `atlas plan` commands with the same flags/preset and
compare stdout bytes. The plugin test suite exercises this invariant. For
stateful dogfood, point both routes at the same isolated source and distinct
state roots; compare plans, manifests, snapshots, receipts, and Harness Boot.

Exercise the v0.3 companion capabilities through the same bridge:

```sh
./scripts/atlas menu --choice 9 --source . --pack ../deterministic-kg-rag-framework/config/domain-packs/repository-architecture-v1.json --domain-output domain-projection
./scripts/atlas menu --choice 10 --source . --api-output api-schema.json
./scripts/atlas backend capabilities
./scripts/atlas backend describe --state-root .atlas-state
```

Choice 9 builds a local domain graph and non-activated receipt. Choice 10
emits a signed declaration projection. Neither command calls a model, follows
network references, or registers a candidate.

For a source-body-free backend read, compile a signed plan and run it against
the same state binding:

```sh
./scripts/atlas backend plan record.list --state-root .atlas-state
./scripts/atlas backend run --state-root .atlas-state --plan record-list.plan.json
```

The caller is responsible for capturing canonical plan stdout as the plan
file. `backend run` reports answerable or explicit empty/abstain results with
source anchors and refuses declared or intent-implied protected effects before
reading. `query` remains the higher-level governed intent route.

## Project Atlas frontend dogfood

Treat the frontend pipeline as two protected stages:

1. Run `./scripts/atlas atlas build --source . --state-root .atlas-state
   --output project-atlas-site` and verify exactly `index.html`,
   `project-atlas.json`, `content.json`, and `design.css`. The receipt remains
   under `.atlas-state`.
2. Query with `./scripts/atlas atlas context "<task>" --output
   project-atlas-site --budget-tokens 1800`, then inspect selected source files
   in order.
3. Run `atlas-frontend-designer` only against copies of `content.json` and
   `design.css`; pass proposals through `atlas rebind` into a new bundle.
4. Validate with `./scripts/atlas atlas check --output <bundle>`.

The designer server may use a local markdown-renderer adapter, but operations
records must name the adapter by logical identity and digest. Do not record
device-specific absolute paths in repository artifacts. Before accepting a
designer result, validate that canonical JSON, source digests, proof limits,
protected HTML IDs, and contract comments are unchanged.

Task-route qualification uses frozen relevance judgments, Recall@K, MRR,
citation correctness, context-token cost, freshness, abstention, and exact
repeatability.

## Dogfood matrix

- Each single flag: project, context, knowledge, topology, evidence-rules.
- Each preset: repo-orientation, implementation, kg-rag, release-review.
- Representative explicit combinations and reversed user flag ordering.
- Duplicate/unknown flags, missing framework, missing required capability,
  optional degraded capability, malformed manifest, stale snapshot.
- Active update and pointer rollback.
- Semantic/reranker requested while unavailable.
- Injection, protected effect, unknown evidence, tombstone, contradiction, and
  invalid structured generation.
- Four-file membership, same-input repeatability, task-route qualification,
  direct impact, annotation dry-run, and protected presentation rebind.
- Domain-pack validation/mining, API-schema projection parity, backend
  capabilities/describe/plan/run parity, and missing required v0.3 capability
  refusal before framework import.
- Plugin removal after a separately approved direct install.
- Closed profile validation, unknown-adapter refusal, deterministic profile
  descriptions, ten-case full-stack drift replay, paired-DKG evidence-firewall
  replay, and the production-locked single-run AI host-runtime receipt.
- Result, fixture/source, adapter, DKG/In-the-Loop identity, environment,
  producer, verifier, and verification-record drift must report stale or
  ineligible before any owner promotion decision.

## Installation boundary

The release baseline contains no hosted marketplace publication. A local Codex
development install uses a host-local marketplace pointing at the exact
verified repository path, followed by the plugin-creator cachebuster and
reinstall flow. The installed bridge also needs the paired framework root
available as `DKG_FRAMEWORK_ROOT`; on Codex this may be injected through the
documented `shell_environment_policy.set` configuration. Installation,
reinstall, removal, cache changes, and environment configuration are protected
effects and need exact approval. Never edit the installed in-the-loop cache.

## Marketplace descriptor

The committed `marketplace/claude-code/marketplace.json` is provider-neutral
distribution metadata. It points to the Git source, omits `policy.products`,
and declares no provider account, model provider, or runtime network
requirement. Hosts that require local marketplace paths may translate the git
source after cloning; that translation is host-specific and is not an
installation receipt.
