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

The plugin is intentionally not installed. It includes a provider-neutral
Claude Code marketplace descriptor under `marketplace/claude-code/` for
distribution metadata. Direct installation, cache updates, removal, hosted
marketplace publication, marketplace mutation, and sharing each remain separate
user-approved effects.

## Paired local use

Keep this repository beside `deterministic-kg-rag-framework`, or set
`DKG_FRAMEWORK_ROOT` to its root. Open the menu:

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

Version `1.1.0` is the current local source candidate paired with framework
`>=0.3.0,<0.4.0`. It is not installed,
marketplace-published, deployed, or released. The
historical [`v1 closure record`](release-docs/v1-closure.md) lists the frozen
v1 evidence. The [`changelog`](CHANGELOG.md) describes the v1.1 source
candidate and its final-byte artifact evidence.

## After v1.1.0

The historical [post-v1 roadmap](release-docs/post-v1-roadmap.md) records the
continuity, capability-contract, project-memory, and optional Command Center
tracks that led to this backend bridge. Later work defers to the paired
framework roadmap for stable system contracts and phase gates.
