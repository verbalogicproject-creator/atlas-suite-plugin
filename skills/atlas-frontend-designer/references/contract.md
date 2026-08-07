# Atlas Frontend Designer contract

- Stage: optional Project Atlas presentation refinement
- Inputs: compiler receipt, `project-atlas.json`, `content.json`,
  `project-atlas.css`, `project-atlas.html`
- Editable surfaces: `content.json` presentation fields and
  `project-atlas.css`
- Protected surfaces: `project-atlas.json`, compiler receipt, source ledger,
  source digests, proof limits, canonical IDs, protected HTML IDs, data block
  IDs, and contract comments
- Runtime: optional local preview server and markdown-renderer adapter
- Output: proposed content/CSS diff, visual rationale, validation receipt
- Proof limit: presentation-safe frontend refinement only; not source truth,
  model quality, deployment readiness, connector activation, publication, or
  effect authority

## Required artifact split

`project-atlas.json` is the verifiable source-of-truth artifact.

`content.json` is the editable display and markdown-content artifact.

`project-atlas.css` is the visual refinement artifact.

`project-atlas.html` is the stable shell binding those artifacts through
protected IDs and design handles.

## Server boundary

The designer server is an authoring and preview tool. The portable output must
remain static and offline-readable. A missing server or renderer degrades to
the deterministic shell, not to failed source truth.
