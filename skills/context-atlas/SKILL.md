---
name: context-atlas
description: Maintain durable, cited task state, decisions, drift, bounded context packets, and handoffs. Use for implementation context, resumed work, impact preparation, or the context flag and implementation/release-review presets.
---

# Context Atlas

Revalidate persistent context against live source before relying on it.

1. Inspect repository instructions, current Git state, the active plan,
   manifests, schemas, tests, and relevant Atlas receipts.
2. Classify claims as observed, documented, inferred, proposed, unknown, or
   stale and attach a logical source and proof limit.
3. Preview `python3 ../../scripts/dkg_bridge.py atlas plan --flags context`.
4. Build only with current write authority using `atlas run --flags context`.
5. Keep context packets bounded and cite the active snapshot. Report drift and
   important omissions instead of copying entire repositories.

Read `references/contract.md`. Recovery restores safe progress, never approval.
No resumed conversation, checkpoint, plan, or receipt authorizes a protected
effect. Never silently run Topology or Evidence-Rules; use the exact
`implementation` preset only when all three were requested.
