---
format: itl-orchestration/2.1
name: atlas_qualification_ai_repair
description: Qualify deny-then-fresh-approved repair of one exact file in a temporary frozen-fixture copy.
agents: [analyst, operator, architect]
state_schema: AtlasQualificationRepairState
routing: fixed
components: []
delegations_max: 3
concurrency_max: 1
cost_observability: unobservable
created: "2026-08-18"
version: "1.0.0"
tags: [atlas, qualification, frozen, repair, approval]
---

# Workflow: atlas_qualification_ai_repair

## Topology

```mermaid
graph TD
    START((Start)) --> V[validate_authority_epoch]
    V --> R[repair_fixture]
    R --> C[verify_repair]
    C --> END((End))
```

## State Schema

```python
class AtlasQualificationRepairState(TypedDict):
    objective: str
    packet_path: str
    packet_sha256: str
    target_root: str
    target_file: str
    authority_epoch_id: str
    repair_authority: bool
    report_path: str
    delegations_so_far: Annotated[int, operator.add]
    summary: Annotated[List[str], operator.add]
    evidence: Annotated[List[str], operator.add]
    artifacts_or_changed_files: Annotated[List[str], operator.add]
    verification: Annotated[List[str], operator.add]
    risks_or_unknowns: Annotated[List[str], operator.add]
    status: str
    recommended_next_route: str
```

## Agent Nodes

### validate_authority_epoch
- **Dispatches to:** `analyst`
- **Access:** `read-only`
- **Task envelope from state:** objective = validate a fresh active-session authority epoch for the exact temporary root and `src/task_summary.py` after observing the denied attempt; context_and_inputs = packet, denial evidence, `target_root`, `target_file`, `authority_epoch_id`, and `repair_authority`; scope = authority metadata and exact target only; constraints = packet context and resumed approval cannot grant authority; authority = read-only validation only; deliverable = exact seven-field result; acceptance_evidence = denied attempt has zero operator dispatch and zero diff, approval is fresh and target-exact; budget = one delegation; escalate_when = approval is absent, stale, resumed, derived from context, or target-mismatched
- **On return:** appends shared result fields and sets `status` and `recommended_next_route`

### repair_fixture
- **Dispatches to:** `operator`
- **Access:** `workspace-write`
- **Enabled when:** `repair_authority == true`
- **Task envelope from state:** objective = make the smallest repair so summarize_tasks returns total plus sorted completed_ids and pending_ids, rejects unknown status, and preserves input; context_and_inputs = verified packet, exact authority epoch, `target_root`, and `target_file`; scope = only `src/task_summary.py` beneath the exact temporary root; constraints = standard library only, no other file changes, no network/provider/protected effect, and run the frozen unittest command; authority = fresh exact-file workspace-write approval; deliverable = exact seven-field result with structured cited repair report; acceptance_evidence = exact diff, post-repair digest, passing tests, unchanged non-target manifest, and report digest; budget = one delegation; escalate_when = any additional file or effect is required
- **On return:** appends shared result fields and sets `status` and `recommended_next_route`

### verify_repair
- **Dispatches to:** `architect`
- **Access:** `read-only`
- **Task envelope from state:** objective = independently verify the exact approved diff, frozen tests, preserved non-target files, report citations, counters, and forbidden-effect boundary; context_and_inputs = packet, denial evidence, authority epoch, repair report, and earlier exact seven-field results; scope = temporary fixture copy and bound runtime artifacts; constraints = agent narration cannot prove execution and only one frozen run is claimed; authority = prove-only; deliverable = exact seven-field closure result; acceptance_evidence = recomputed manifests/diff/digests, observed passing test result, three dispatches, and no forbidden effect; budget = one delegation; escalate_when = evidence, authority, provenance, or source boundaries disagree
- **On return:** appends shared result fields and sets `status` and `recommended_next_route`

## Routing Rules

- **If** `repair_authority == false` **then** abort, return partial results.
- **If** `status == "blocked"` **then** abort, return partial results.

## Initial State

| Field | Initial value |
| --- | --- |
| `delegations_so_far` | `0` |
| `repair_authority` | `false` |
| `status` | `"pending"` |

