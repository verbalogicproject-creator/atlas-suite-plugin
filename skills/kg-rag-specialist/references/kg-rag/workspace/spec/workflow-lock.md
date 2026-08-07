---
spec_version: 0.4.1
---

# Deterministic workflow lock and checkpoint

`itl-workflow-lock/1.0` is a standard-library build and validation artifact,
not a runner. Before dispatch, the parent validates a 2.1 workflow, resolves
contained component sources, and writes canonical compact UTF-8 JSON with a
final LF. It contains no timestamps or absolute paths and records source,
registry and selected-profile digests plus flattened namespaced nodes, edges,
joins, state mappings, limits, and checkpoints. Rebuilding identical inputs
MUST produce byte-identical output.

The flattened graph MUST include each declared bounded cycle-back rule with
its normalized predicate. Validation requires the rule maximum to equal the
workflow's `cycle_max`, so the lock binds the single enforced ceiling rather
than discarding a narrower rule-local limit. When a profile or component
access override disables a node, the lock MUST compile deterministic bypasses
only across forward edges. A guarded cycle targeting a disabled node remains
recorded for review but is never eligible and MUST NOT be bypassed into an
unconditional or different cycle. Disabled nodes are never dispatch targets.

A component source MUST be a relative contained regular non-symlink file;
recursive references and incompatible versions fail before dispatch. Global
delegation and cycle ceilings apply to the flattened graph and local ceilings
remain additional limits. A lock records the root and component source
digests and versions; expanded node IDs, roles, access, enabled conditions,
edges, barriers, and instance namespaces; input and output mappings; global
and component-local delegation, concurrency, and cycle limits; checkpoint
declarations; and the resolved binding roster and profile digests. Unknown or
stale inputs fail closed. Lock validation happens before every initial or
resumed dispatch.

Checkpoints use `itl-checkpoint/1.0`. They are opt-in, atomic, contained and
non-symlink files bound to lock and state digests. They MUST exclude approval
authority, credentials, prompts, and private transcripts. Resume revalidates
the lock sources and registry and restores state only: it never restores any
repair, commit, push, publication, or other protected approval.

See [[checkpoints.md]] for the checkpoint record and resume contract.
See [[evidence.md]] for lock-bound evidence records referenced by checkpoints.
