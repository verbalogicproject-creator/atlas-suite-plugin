# Atlas Suite Plugin

Atlas Suite is a thin Apache-2.0 Codex plugin for the five deterministic DKG
Atlases, an upgraded KG-RAG Specialist, and the planned Project Atlas frontend
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

The plugin is intentionally not installed and has no marketplace entry in v1.
Direct installation, cache updates, removal, marketplace changes, publication,
and sharing each remain separate user-approved effects.

## Paired local use

Keep this repository beside `deterministic-kg-rag-framework`, or set
`DKG_FRAMEWORK_ROOT` to its root. Preview a plan without writing:

```sh
python3 scripts/dkg_bridge.py atlas plan --preset kg-rag
```

See `release-docs/operations.md` for validation and controlled dogfood.

## Project Atlas frontend pipeline

The suite treats Project Atlas HTML as a two-stage product:

- a deterministic compiler emits `project-atlas.json`, `content.json`,
  `project-atlas.css`, `project-atlas.html`, and a receipt;
- an optional `atlas-frontend-designer` server refines only presentation
  surfaces through a tailored visual skill and markdown-renderer adapter.

`project-atlas.json` remains the verifiable source of truth. `content.json`
holds editable display copy and markdown content. `project-atlas.css` owns
visual refinement. The HTML shell exposes stable IDs and design comments so UI
iteration can improve the frontend without touching authority-bearing data.
See `release-docs/project-atlas-frontend-pipeline.md`.

## Release status

Version `1.0.0` is a committed source candidate. It is not installed,
marketplace-published, deployed, or released. The
[`v1 closure record`](release-docs/v1-closure.md) lists observed evidence,
paired final-byte gates, artifact-manifest procedure, and protected-effect
boundary. See the [`changelog`](CHANGELOG.md) for candidate contents.

## After v1

The [plugin post-v1 roadmap](release-docs/post-v1-roadmap.md) covers private install
dogfood, the separate lightweight public Project Atlas skill, maintained
private-suite evolution, and later read-only managed/mobile interfaces. It
defers to the paired framework roadmap for system architecture and phase gates.
