# Atlas Suite Plugin

Provider-neutral agent interface for deterministic repository Atlases, KG-RAG
workflows, bounded context, and Project Atlas frontend generation.

Atlas Suite is a thin Apache-2.0 Codex plugin. It contains no database engine
and does not fork the DKG contracts.
`scripts/dkg_bridge.py` resolves the paired `deterministic-kg-rag-framework`
and invokes its exact CLI/resolver.

Skills:

- `atlas-suite-plugin:project-atlas`
- `atlas-suite-plugin:context-atlas`
- `atlas-suite-plugin:knowledge-atlas`
- `atlas-suite-plugin:topology-atlas`
- `atlas-suite-plugin:evidence-rules-atlas`
- `atlas-suite-plugin:kg-rag-specialist`
- `atlas-suite-plugin:atlas-frontend-designer`

A separately approved local Codex development installation now exists through
the host-local `atlas-suite-local` marketplace. The repository still includes
only a provider-neutral Claude Code descriptor under `marketplace/claude-code/`
for distribution metadata. Removal, hosted publication, sharing, deployment,
and other external effects remain separately approved actions.

## Paired local use

Keep this repository beside `deterministic-kg-rag-framework`, or set
`DKG_FRAMEWORK_ROOT` to its root. Qualification, verifier, scenario, and bridge
commands all honor that same variable. Open the menu:

```sh
./scripts/atlas
```

The same entry point remains scriptable. Build a complete hub with
`./scripts/atlas atlas build --source . --state-root .atlas-state --output
project-atlas-site`.

Mine repository structure or inspect API declarations without a model:

```sh
./scripts/atlas domain mine --source . --pack ../deterministic-kg-rag-framework/config/domain-packs/repository-architecture-v1.json --output domain-projection
./scripts/atlas domain api-schema --source . --output api-schema.json
```

The v1.1 bridge accepts framework versions `>=0.3.0,<0.4.0` only after the
framework declares its closed interface plus the read-backend and canonical
16-query capability surfaces. Backend arguments pass through byte-for-byte:

```sh
./scripts/atlas backend capabilities
./scripts/atlas backend describe --state-root .atlas-state
./scripts/atlas backend plan record.list --state-root .atlas-state
./scripts/atlas backend run --state-root .atlas-state --plan record-list.plan.json
```

Task-facing routes remain provider-neutral and map to framework contracts:

- orient: `atlas context` or the `repo-orientation` preset;
- audit: `domain mine`, `domain query`, and evidence-backed backend reads;
- inspect architecture: `atlas context` plus graph/record capabilities;
- trace implementation: `record.get`, `graph.walk`, and `provenance.trace`;
- analyze impact: `atlas impact` or `impact.analyze`;
- extract components: `domain mine` and `record.list`;
- build task context: `atlas context` or `context.compile`;
- generate Project Atlas: `atlas build`, retaining exactly four public files.

`backend run` reports `answerable` or explicit `empty`/`abstain` outcomes from
governed records and refuses declared or intent-implied protected effects
before reading. The established `query` route retains the same governed safety
boundary; neither route grants mutation or activation authority.

See `release-docs/operations.md` for validation and controlled dogfood.

## Transparent capability profiles

Inspect named combinations without executing them:

```sh
./scripts/atlas profile list
./scripts/atlas profile describe fullstack-contract-spine
./scripts/atlas profile explain rag-evidence-firewall
./scripts/atlas profile plan ai-tool-control-plane
./scripts/atlas profile qualification fullstack-contract-spine
```

These commands are deterministic and read-only; there is no profile `run`
route. Three candidate profiles expose the full-stack contract spine, RAG
evidence firewall, and Atlas/In-the-Loop/Codex control plane. All three have
current passing local candidate receipts when the exact optional
In-the-Loop 0.4.1 qualification contract is available. Without it, the
full-stack and RAG profiles remain usable, while the AI profile reports
`itl-qualification-contract-unavailable` as failed, stale, and non-promotable.
The stored control-plane evidence covers one production-roster orientation and
one deny-then-approved frozen repair; it does not claim repeatability or
promote registry maturity.
See [`capability profiles and qualification`](release-docs/capability-profiles.md).

## Project Atlas frontend pipeline

The suite treats Project Atlas HTML as a two-stage product:

- a deterministic compiler emits exactly `index.html`, `project-atlas.json`,
  `content.json`, and `design.css`; its receipt stays under the state root;
- an optional `atlas-frontend-designer` server refines only presentation
  proposals through a tailored visual skill and deterministic rebind.

`project-atlas.json` remains the verifiable source of truth. `content.json`
holds bounded display copy and agent/design intent. `design.css` owns visual
refinement and is compiled inline for reliable Android/offline direct opening.
`index.html` exposes stable IDs and design comments so UI
iteration can improve the frontend without touching authority-bearing data.
See `release-docs/project-atlas-frontend-pipeline.md`.

## Release status

Version `1.1.0` is the current source baseline paired with framework
`>=0.3.0,<0.4.0`. A cachebusted `1.1.0+codex.*` build is installed and has
passed bounded local Codex dogfood; it is not hosted-marketplace-published,
deployed, shared, or released. The
historical [`v1 closure record`](release-docs/v1-closure.md) lists the frozen
v1 evidence. The [`changelog`](CHANGELOG.md) describes the v1.1 source
candidate and its final-byte artifact evidence. See the
[Codex dogfood record](release-docs/codex-install-dogfood-2026-08-18.md) for
the installed proof and remaining gaps.

## After v1.1.0

The historical [post-v1 roadmap](release-docs/post-v1-roadmap.md) records the
continuity, capability-contract, project-memory, and optional Command Center
tracks that led to this backend bridge. Later work defers to the paired
framework roadmap for stable system contracts and phase gates.
