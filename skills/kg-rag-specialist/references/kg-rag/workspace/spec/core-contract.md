---
spec_version: 0.4.1
---

# Core contract: task envelope and result contract

Every delegation in In the Loop — regardless of binding, tier, or role —
passes through the same two structures. A binding may render these as
whatever native format its platform prefers (frontmatter, a system prompt
section, a tool-call schema), but the fields themselves are part of the
spec, not the binding.

## Task envelope

Every delegated instruction must state:

```yaml
objective:
context_and_inputs:
scope:
constraints:
authority:
deliverable:
acceptance_evidence:
budget:
escalate_when:
```

`budget` MUST be a machine-checkable numeric ceiling — a cost limit, a
retry-cycle cap, a token budget — not a prose instruction like "escalate if
it feels expensive." A binding that cannot enforce a numeric ceiling
mechanically must still declare one; an unenforced number is still a
sharper contract than none.

## Result contract

Every delegated result must report:

```yaml
status: complete | partial | blocked
summary:
evidence:
artifacts_or_changed_files:
verification:
risks_or_unknowns:
recommended_next_route:
```

The result is a short, structured summary regardless of how much internal
work produced it — a delegate that burned significant effort internally
still returns a condensed report here, not a transcript.
