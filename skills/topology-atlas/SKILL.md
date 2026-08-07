---
name: topology-atlas
description: Build or inspect deterministic dependency, workflow, data-flow, connector, impact-path, and global aggregate projections. Use for architecture, blast-radius analysis, repository orientation, implementation planning, or the topology flag and any preset containing it.
---

# Topology Atlas

Map observed endpoints and relations; never infer a working dependency from a
filename alone.

1. Inspect manifests, imports, routers, migrations, commands, tests, fixtures,
   connectors, and read/write boundaries.
2. Preview `python3 ../../scripts/dkg_bridge.py atlas plan --flags topology`.
3. Build with the exact flag only after write authority is current.
4. Validate that every edge endpoint resolves, traversals are bounded, global
   aggregates are deterministic, and ties use stable IDs.
5. For impact analysis, report direction, depth, candidate ceiling, omitted
   paths, and the evidence/proof boundary.

Read `references/contract.md`. A topology edge describes observed or declared
structure; it does not prove runtime behavior or authorize replay.
