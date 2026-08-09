# Atlas Suite Plugin

Atlas Suite is a thin Apache-2.0 Codex plugin for the five deterministic DKG
Atlases, an upgraded KG-RAG Specialist, and an agent-first Project Atlas frontend
pipeline. It contains no database engine and does not fork the DKG contracts.
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

Version `1.0.1` is the current local source candidate paired with framework
`0.2.0`. It is not installed,
marketplace-published, deployed, or released. The
[`v1 closure record`](release-docs/v1-closure.md) lists observed evidence,
paired final-byte gates, artifact-manifest procedure, and protected-effect
boundary. See the [`changelog`](CHANGELOG.md) for candidate contents.

## After v1.0.1

The [plugin roadmap](release-docs/post-v1-roadmap.md) defines the post-`v1.0.1`
continuity, capability-contract, project-memory, and optional Command Center
tracks. It defers to the paired framework roadmap for stable system contracts
and phase gates.
