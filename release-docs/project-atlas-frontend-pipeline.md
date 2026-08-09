# Project Atlas frontend pipeline

Status: implemented candidate contract; human baseline accepted, automated browser qualification open

Project Atlas Suite separates authority, editable content, and visual
refinement into distinct artifacts so Atlas output can become an interactive
frontend without weakening deterministic verification.

## Artifact boundary

`project-atlas.json` is the verifiable source of truth. It contains the
canonical schema, source ledger, digests, claims, evidence, proof limits,
stable IDs, section graph, and validation metadata. It is compiler-owned and
must be byte-repeatable for the same source revision and compiler inputs.

`content.json` is the bounded content surface. It contains display copy,
labels, section summaries, route IDs, and explicit agent/design intent. A
future renderer adapter may add digest-pinned Markdown references through a
versioned contract. Human or frontend-designer proposals cannot add canonical
claims, change source digests, remove proof limits, or redefine IDs.

`design.css` is the visual layer. It contains theme variables,
typography, responsive layout, visual hierarchy, and interaction polish. It
may be refined without touching canonical data or the HTML shell. Deterministic
rebind embeds those validated bytes into the generated HTML for reliable
`content://`, `file://`, and offline direct opening.

`index.html` is a stable compiler-owned hub. It binds the source-of-truth JSON,
content JSON, and the embedded CSS digest through fixed IDs and template slots. It renders the
essential route and proof content statically so direct-file and no-JavaScript
views remain useful.

## Two-stage pipeline

Stage 1 is the deterministic compiler. It performs source scanning,
normalization, evidence binding, schema validation, digest calculation, and
static shell generation. It has no LLM pass and no network dependency.

Stage 1 emits:

- `project-atlas.json`
- `content.json`
- `design.css`
- `index.html`

The build receipt names compiler inputs, output digests, and proof limit under
the external state root. It is intentionally not a fifth public file.

Stage 2 is `atlas-frontend-designer`. It is an optional server-backed design
runtime with a Project-Atlas-specific visual skill. It can refine
`content.json` presentation fields and `design.css`, preview the interactive
Atlas, and propose UI variants. The deterministic `atlas rebind` command
regenerates `index.html`; the designer cannot mutate it directly or change
`project-atlas.json`, canonical IDs, source digests, proof limits, or authority
markers.

## HTML design handles

The deterministic shell should expose explicit comments for the design stage.
These comments are an interface, not authority:

```html
<!-- ATLAS-CONTRACT: dkg-project-atlas-html/1.0; protected ids and data digests must not change -->
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
- `design.css` has no remote imports and no device-specific absolute
  paths.
- `index.html` preserves protected IDs, script/data block IDs,
  comments, and digest markers.
- single-file offline fallback still opens without a server.

Passing validation means the interactive frontend is presentation-safe. It
does not prove source truth, model quality, deployment readiness, or effect
authority.
