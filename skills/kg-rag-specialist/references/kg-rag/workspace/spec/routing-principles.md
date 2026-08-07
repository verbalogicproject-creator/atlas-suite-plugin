---
spec_version: 0.4.1
---

# Routing principles

- Route by task shape, not by task label. What decides the route is
  reversibility, scope clarity, volume, and ambiguity risk — not a keyword
  match on what the task is called.
- Do not spawn a specialized role by default. Delegate only when
  specialization or independent/parallel execution materially improves
  cost, latency, or quality over handling it directly.
- On a specialized role being unavailable, fall back to the next
  appropriate tier once; if that also fails, absorb the work at the
  highest available capability rather than looping.
- Permit one same-role retry only for malformed output or a transient
  failure, then escalate or stop with a clear, stated blocker. Do not retry
  silently past that point.
- Gate cheap-tier work, don't add redundant self-verification to
  already-self-verifying tiers. A cheap or fast tier needs explicit
  allowed/forbidden actions and hard stop points to be trustworthy; a tier
  that already verifies its own output should not carry boilerplate asking
  it to verify itself again.
- A routing heuristic earns permanence, it isn't assumed one. A new rule
  discovered during real use gets logged with why it was needed, and only
  hardens into a permanent rule after recurring across two or more real
  cases — not after a single anecdote.
