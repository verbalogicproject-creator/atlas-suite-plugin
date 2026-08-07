# Project Atlas contract

- Flag: `project`
- Snapshot: `dkg-atlas-snapshot/1.0`
- Projection: isolated read-only-query SQLite; canonical JSON is authoritative
- Facet: `role` (`component`, `command`, `documentation`, `test`, `fixture`, `configuration`)
- Output: inventory records, human summary, child receipt, composite membership
- Proof limit: owner orientation and status projection; not completion or effect authority

V1 ships the canonical snapshot and Markdown summary, not an HTML renderer. Any
later HTML renderer must remain a presentation over the Project snapshot.
Legacy `project-atlas-*` readers remain read-only during migration.
