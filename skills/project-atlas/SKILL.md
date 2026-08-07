---
name: project-atlas
description: Build, refresh, inspect, or query a deterministic Project snapshot and owner-orientation summary with architecture/operations inventory, status, and proof boundaries. Use for repository orientation, handoffs, completion evidence, or the project flag and repo-orientation/release-review presets.
---

# Project Atlas

Use the paired DKG framework as the only writer and resolver. Project Atlas is
a projection over source; source, tests, receipts, and current human decisions
retain stronger authority.

1. Read repository instructions, Git state, manifests, architecture, commands,
   tests, evidence, and current-status documentation.
2. Preview the exact plan with
   `python3 ../../scripts/dkg_bridge.py atlas plan --flags project`.
3. Run only when the user authorized a build:
   `python3 ../../scripts/dkg_bridge.py atlas run --flags project --source <root>`.
4. Query with the shared `dkg query` route and retain citations/proof limits.
5. Report missing capabilities, degraded receipts, stale evidence, and omitted
   context. Never silently add another Atlas.

Use `--preset repo-orientation` only when the user requested Project plus
Topology. Read `references/contract.md` before interpreting the snapshot.
Network access, models, plugin installation, publication, deployment, commits,
and active source promotion require separate authority.
