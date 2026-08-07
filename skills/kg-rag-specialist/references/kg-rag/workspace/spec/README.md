---
spec_version: 0.4.1
---

# In the Loop — core spec

This directory is the provider-agnostic core of **In the Loop**: the part of
the framework that is true regardless of which AI coding tool is running it.
Nothing in `spec/` may name a specific vendor, model, or tool primitive — see
`core-contract.md`, `authority-and-evidence.md`, and `routing-principles.md`
for the normative content, and the repo's spec-purity test for the mechanical
rule that keeps it that way.

A **binding** is a concrete, native implementation of this spec for one
platform. A second binding for a different AI coding tool should be able to
implement everything in this directory faithfully, using that platform's own
idiomatic mechanisms, without this directory needing to change.

<!-- binding-example:start -->
This repository ships bindings under `bindings/claude-code/` and
`bindings/codex/`, each built on its platform's native delegation, planning,
permission, and plugin primitives.
<!-- binding-example:end -->

## What lives here

- `core-contract.md` — the task-envelope and result-contract every
  delegated unit of work uses.
- `authority-and-evidence.md` — what a binding must never let model output
  substitute for: human approval on protected effects, and empirical
  verification over narration.
- `routing-principles.md` — how work gets routed to a cheaper or more
  capable tier, and how a routing heuristic earns permanence.
- `orchestration-format.md` — the ITL orchestration format (`.itl.md`): how
  a manager-orchestrated multi-agent system's graph, shared state, reusable
  workflow agents, and routing rules get written down as a declarative file
  a session reads and drives, including the formal grammar for routing-rule
  predicates.
- `workflow-lock.md` — deterministic validation and flattening of composed
  2.1 graphs before dispatch.
- `checkpoints.md` — opt-in, digest-bound persistence that never restores
  protected authority.
- `evidence.md` — typed, lock-bound observation claims and their fixed verdict
  vocabulary.
- `repo-factory-lifecycle.md` — the parent-controlled Five-Dot intake,
  revision-bound approvals, sealed authority, evidence, repair, and local
  release-readiness lifecycle for a repository factory.

## What does not live here

Anything that only makes sense on one platform — a specific tool name, a
specific model family, a specific configuration file format — belongs in a
binding's own directory, not here. If a binding needs to show a concrete
example of one of these principles in action, it does so in its own
`README.md`, with a fenced "binding example" callout, never inside this
directory's normative text.
