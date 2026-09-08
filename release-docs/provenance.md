# Provenance and compatibility

## Baseline

Source: installed `in-the-loop` plugin 0.4.1 KG-RAG Specialist cache.

The baseline package contained 63 non-pycache files. Its canonical tree digest
and key artifact digests are in the baseline manifest. Original skill and agent
metadata live under the plugin-level `vendor/kg-rag-specialist-baseline`
directory so Codex does not recursively register the pinned baseline as a
second active skill; original references and
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

Atlas Suite v1.1.0 targets deterministic-kg-rag-framework
`>=0.3.0,<0.4.0` and its versioned `dkg-*` contracts. The bridge uses the
framework itself; it does not translate contracts. Before importing framework
code, the bridge requires a compatible framework version, Python `>=3.11`,
`dkg-framework-interface/1.0`, `dkg-cli/1.0`, and the declared v0.3 capability
set. Legacy
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

## Qualification provenance

The canonical qualification root is this plugin's `qualification/` directory.
It owns registry/profile/proof contracts and frozen Suite fixtures; it does not
copy the DKG engine or claim ownership of In-the-Loop. Candidate receipts bind
the current registry, profile, and proof-plan digests. The full-stack fixture
records its FastAPI/Pydantic/Python direct-call environment; the RAG receipt
binds an upstream DKG Harness Boot receipt. No absolute device path, network
source, provider call, or installed-plugin state is part of those claims.

Receipt v2 additionally binds canonical result, source/fixture manifest,
complete adapter identities, root/runtime/dependency environment, producer,
and a distinct local verifier implementation. The verifier runs in a separate
process, reruns frozen full-stack cases, independently rebuilds/queries RAG,
and resolves citation hashes. The signed verification record is stronger than
producer repeatability alone, but it remains inside the same local source and
host trust domain; an external audit is not claimed.
