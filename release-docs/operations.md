# Operations and dogfood

## Validate without installing

From the plugin root:

```sh
python3 scripts/generate_release_docs.py
python3 scripts/generate_release_docs.py --check
python3 skills/kg-rag-specialist/scripts/validate_deterministic_kb.py
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error::ResourceWarning python3 -m unittest discover -s tests -v
```

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

## Project Atlas frontend dogfood

Treat the frontend pipeline as two protected stages:

1. Run the deterministic compiler and verify the emitted
   `project-atlas.json`, `content.json`, `project-atlas.css`,
   `project-atlas.html`, and receipt digests.
2. Run `atlas-frontend-designer` only against a copy of `content.json` and
   `project-atlas.css`.

The designer server may use a local markdown-renderer adapter, but operations
records must name the adapter by logical identity and digest. Do not record
device-specific absolute paths in repository artifacts. Before accepting a
designer result, validate that canonical JSON, source digests, proof limits,
protected HTML IDs, and contract comments are unchanged.

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
- Plugin removal after a separately approved direct install.

## Installation boundary

V1 contains no hosted marketplace publication and no cachebuster action. Direct
installation must target the exact verified repository path and remain beside
existing skills. Installation, reinstall, removal, and any cache update are
protected effects and need separate approval. Never edit the installed
in-the-loop cache.

## Marketplace descriptor

The committed `marketplace/claude-code/marketplace.json` is provider-neutral
distribution metadata. It points to the Git source, omits `policy.products`,
and declares no provider account, model provider, or runtime network
requirement. Hosts that require local marketplace paths may translate the git
source after cloning; that translation is host-specific and is not an
installation receipt.
