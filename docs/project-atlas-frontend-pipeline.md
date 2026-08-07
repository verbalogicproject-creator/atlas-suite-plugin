# Project Atlas frontend pipeline

Status: design contract for the next Project Atlas Suite implementation slice

Project Atlas Suite separates authority, editable content, and visual
refinement into distinct artifacts so Atlas output can become an interactive
frontend without weakening deterministic verification.

## Artifact boundary

`project-atlas.json` is the verifiable source of truth. It contains the
canonical schema, source ledger, digests, claims, evidence, proof limits,
stable IDs, section graph, and validation metadata. It is compiler-owned and
must be byte-repeatable for the same source revision and compiler inputs.

`content.json` is the editable content surface. It contains display copy,
markdown bodies or renderer-safe markdown references, labels, section
summaries, curated excerpts, and ordering hints. It may be edited by a human
or the frontend designer stage, but it cannot add claims, change source
digests, remove proof limits, or redefine canonical IDs.

`project-atlas.css` is the visual layer. It contains theme variables,
typography, responsive layout, visual hierarchy, and interaction polish. It
may be refined without touching canonical data or the HTML shell.

`project-atlas.html` is a stable shell. It binds the source-of-truth JSON,
content JSON, and CSS through fixed IDs and template slots. The shell may
include embedded fallback copies for single-file portability, but the contract
must still expose the three logical artifacts.

## Two-stage pipeline

Stage 1 is the deterministic compiler. It performs source scanning,
normalization, evidence binding, schema validation, digest calculation, and
static shell generation. It has no LLM pass and no network dependency.

Stage 1 emits:

- `project-atlas.json`
- `content.json`
- `project-atlas.css`
- `project-atlas.html`
- a receipt naming compiler version, inputs, output digests, and proof limit

Stage 2 is `atlas-frontend-designer`. It is an optional server-backed design
runtime with a Project-Atlas-specific visual skill. It can refine
`content.json` presentation fields and `project-atlas.css`, preview the
interactive Atlas, and propose UI variants. It cannot mutate
`project-atlas.json`, protected HTML IDs, embedded canonical JSON, source
digests, proof limits, or authority markers.

## HTML design handles

The deterministic shell should expose explicit comments for the design stage.
These comments are an interface, not authority:

```html
<!-- ATLAS-CONTRACT: project-atlas-html/3.0; protected ids and data digests must not change -->
<!-- ATLAS-SOT: project-atlas.json sha256=<digest>; edit forbidden outside compiler -->
<!-- ATLAS-CONTENT: content.json sha256=<digest>; editable presentation surface -->
<!-- ATLAS-DESIGN: slot=overview intent="improve hierarchy; preserve bindings and source labels" -->
<!-- ATLAS-DESIGN: slot=evidence intent="make proof limits scannable; do not rewrite facts" -->
```

The designer may use these comments to target sections, but validation must
fail if the comments are used to justify changing canonical content.

## Markdown renderer adapter

Markdown rendering is a pluggable frontend adapter. During local development,
the suite may use a device-local renderer such as the markdown renderer in an
operator workspace, but absolute device paths are not part of the product
contract and must not be emitted into Atlas artifacts.

The portable contract is:

- `content.json` records logical markdown locators and safe markdown bodies or
  digest-pinned references.
- the renderer receives only sanitized markdown plus metadata needed for
  display.
- renderer output is presentation-only and never becomes evidence unless a
  compiler receipt separately binds it.
- missing renderer support degrades to deterministic static HTML.

## Validation

Stage 2 output must pass a protected-surface validator:

- `project-atlas.json` is byte-identical or digest-identical to Stage 1.
- canonical IDs, source digests, proof limits, and schema markers are
  unchanged.
- `content.json` contains no new canonical claim, source digest, authority
  state, or external effect approval.
- `project-atlas.css` has no remote imports and no device-specific absolute
  paths.
- `project-atlas.html` preserves protected IDs, script/data block IDs,
  comments, and digest markers.
- single-file offline fallback still opens without a server.

Passing validation means the interactive frontend is presentation-safe. It
does not prove source truth, model quality, deployment readiness, or effect
authority.
