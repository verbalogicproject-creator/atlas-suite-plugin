# Provenance and compatibility

## Baseline

Source: installed `in-the-loop` plugin 0.4.1 KG-RAG Specialist cache.

The baseline package contained 63 non-pycache files. Its canonical tree digest
and key artifact digests are in the baseline manifest. Original skill and agent
metadata live under `references/baseline-package`; original references and
scripts retain their usable layout. The active Atlas Suite skill is new and
does not modify the cache.

## Upgraded knowledge release

`deterministic-rag-kb/v1` records source-ledgered claims, platform profiles,
model observations, connector guidance, contextual-facet boundaries,
limitations, candidate recipes, and adversarial cases. The validator resolves
all claim sources and rechecks the cookbook and registry digests/count.

The KB’s Harness Boot receipt has `qualification_scope: blueprint`. It does not
claim runtime retrieval, exact-revision acquisition, semantic quality, model
generation, installation, or external effects.

## Framework compatibility

Atlas Suite v1.0.1 targets deterministic-kg-rag-framework `0.2.0` and its
versioned `dkg-*` contracts. The bridge uses the framework itself; it does not
translate contracts. Before importing framework code, the bridge requires the
exact framework version, Python `>=3.11`, `dkg-framework-interface/1.0`,
`dkg-cli/1.0`, and the declared v0.2 capability set. Legacy
`project-atlas-*` reading is owned by the framework shim and is not duplicated
in plugin prompts.

## Frontend design skill source

`atlas-frontend-designer` is derived from the local Taste frontend discipline,
but narrowed for Project Atlas knowledge UI. The derived skill keeps the
anti-slop design audit, accessibility, responsive layout, motion restraint, and
production preflight principles. It replaces landing-page defaults with Atlas
specific constraints: protected source-of-truth JSON, editable `content.json`,
CSS-only visual refinement, markdown-renderer adapter safety, and
protected-surface validation.

No device-local markdown renderer path is part of the product contract. A
local renderer may be used during dogfood only through a logical adapter
identity and digest.
