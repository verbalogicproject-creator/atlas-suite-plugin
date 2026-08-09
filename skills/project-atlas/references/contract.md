# Project Atlas contract

- Child flag: `project`
- Combined build: all five children through the exact `release-review` preset
- Child snapshot: `dkg-atlas-snapshot/1.0`
- Public Atlas: `dkg-project-atlas/1.0`
- Content: `dkg-project-atlas-content/1.0`
- HTML: `dkg-project-atlas-html/1.0`
- Internal compact map: `dkg-ctx/1.0`, stored under the state root
- Projection: isolated SQLite for queries; canonical JSON remains authoritative
- Dimension authority: derived and non-governing; agent enrichment is inactive
  until held-out qualification passes

The public bundle contains exactly `index.html`, `project-atlas.json`,
`content.json`, and `design.css`. Build and rebind receipts remain under the
state root and never become a fifth public file. `index.html` is the concise
agent map; routes name source files, reading order, reasons, estimated context
cost, freshness, and omissions.

The bundle excludes credentials, private bodies, absolute device paths,
runtime caches, external scripts, and remote CSS. Context selection and impact
relations are deterministic projections, not completion proof or effect
authority. Legacy `project-atlas-*` readers remain read-only during migration.
