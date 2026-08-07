# Context Atlas contract

- Flag: `context`
- Facet: `decision_state` (`current`, `superseded`, `blocked`, `proposed`, `unknown`)
- Sources: plans, decisions, status, handoffs, and repository instructions
- Drift rule: revalidate source hashes, active manifest, schemas, and Git state
- Proof limit: task context and continuity only; context never grants authority
