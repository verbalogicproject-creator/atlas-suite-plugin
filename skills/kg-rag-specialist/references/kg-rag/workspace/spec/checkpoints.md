---
spec_version: 0.4.1
---

# Checkpoints

Checkpoints are optional persistence records for a validated and locked 2.1
workflow. They preserve declared, non-private state and bounded progress; they
do not preserve authority.

A checkpoint MUST:

- be explicitly enabled by the caller and declared by a Routing Rule;
- use a relative contained path whose file and existing ancestors are not
  symbolic links;
- be written atomically as canonical UTF-8 JSON with a final LF;
- contain only a caller-selected subset of fields declared by the root State
  Schema;
- bind itself to the exact workflow-lock digest and a digest of the projected
  state; and
- contain a sorted unique `evidence_refs` list of `itl-evidence/1.0` record
  SHA-256 values, when evidence is retained;
- bind `permitted_successors` derived from the locked graph and the ordered,
  predecessor-valid completed-node prefix; and
- record execution epochs and global and component-local counters without
  exceeding the locked ceilings.

Forward successors ignore disabled nodes and cycle edges. A locked cycle-back
target may reappear in `permitted_successors` after it completed in an earlier
epoch only when its normalized guard evaluates true against the projected
checkpoint state and both global and applicable component-local cycle counters
remain below their limits. Subsequent forward nodes become eligible as their
predecessors complete the newer epoch. Epochs MUST be backed by a locked cycle
target and consistent with delegation and cycle counters. Checkpoint data
records eligibility, not authority to dispatch the cycle.

A checkpoint MUST exclude approval or execution authority, credentials,
secrets, task prompts, and private transcripts. Resume MUST revalidate the
lock, every source digest, the binding roster, the selected profile, the state
projection, and all progress counters. Repair, commit, push, publication,
deployment, communication, purchase, deletion, and other protected effects
require fresh authority after resume. A checkpoint never restores approval.

Exclusion applies recursively to every projected value, including nested
object keys, list elements, and scalar strings. Private or authority-bearing
terms, credential-shaped values, recursive containers, excessive nesting, and
non-JSON values MUST fail closed during both write and resume. A safe outer
State Schema field name does not make an unsafe nested value persistable.

Each evidence reference identifies a separately validated record bound to the
same exact lock. Write and resume require the referenced canonical evidence
bytes; missing, duplicate, tampered, stale-lock, or digest-mismatched records
fail closed. Completed progress whose required predecessors are incomplete and
a stored successor set that differs from the graph-derived set also fail.
A reference is an integrity pointer, not proof of an external effect and not a
restoration of authority.
