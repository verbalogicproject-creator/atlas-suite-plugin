# Atlas Suite post-v1 roadmap

Status: proposed companion to the paired framework roadmap

Authority boundary: this file does not authorize installation, cache mutation,
marketplace changes, publication, connectors, models, accounts, deployment, or
managed-service use.

The authoritative system sequence is the paired framework's
`docs/post-v1-roadmap.md`. Atlas Suite follows it without creating a second
runtime or contract resolver.

## Stage 1 — private direct-install dogfood

- Obtain approval for the exact plugin tree and direct-install target.
- Exercise all five single flags, four presets, representative combinations,
  unavailable adapters, stale state, malformed inputs, update, rollback, and
  removal through the paired DKG framework.
- Invoke every installed skill in fresh Codex threads and verify it preserves
  exact flag resolution, citations, proof limits, and authority boundaries.
- Recompute baseline and deterministic-RAG KB digests without repairing them.

Exit gate: install, use, update, rollback, and removal are observed locally;
CLI/plugin plans and receipts remain byte-identical; independent closure passes.

## Stage 2 — lightweight public Project Atlas skill

Create a separate minimal public skill paired only with the lightweight public
Project Atlas release. It supports deterministic repository orientation and
owner-manual generation with sanitized fixtures.

Exclude Five-Atlas orchestration, private corpora/task state, live connector
state, model/runtime paths, experimental profiles, and the private specialist
KB. Do not market the public skill as the full Atlas Suite.

Exit gate: a clean installation can orient a public fixture, render the static
manual, validate determinism, and uninstall without private dependencies.

## Stage 2.5 - Project Atlas frontend pipeline

Implement the approved two-stage frontend pipeline:

- deterministic compiler emits `project-atlas.json`, `content.json`,
  `project-atlas.css`, `project-atlas.html`, and a receipt;
- Atlas Frontend Designer, extracted and customized from Taste discipline,
  edits only `content.json` presentation fields and `project-atlas.css`;
- the optional designer server previews markdown-rendered content through a
  logical renderer adapter;
- protected-surface validation proves canonical data, source digests, proof
  limits, IDs, contract comments, and receipts are unchanged.

Exit gate: static offline Atlas output still validates without a server;
designer output passes protected-surface validation; no artifact records a
device-specific absolute path.

## Stage 3 — maintained private Atlas Suite

- Version compatibility between the plugin and DKG contracts explicitly.
- Maintain the controlling 18-recipe cookbook until a deliberate schema
  revision; keep candidate recipes separate.
- Require validation, regression fixtures, and a new blueprint-scoped Harness
  Boot receipt for every deterministic-RAG KB release.
- Add provider-neutral read-only adapters only after the framework capability
  is implemented and qualified; fail visibly when unavailable.
- Keep model, connector, and promotion actions outside skill authority.

Exit gate: upgrades are reproducible, backward compatibility is declared, and
skill behavior remains a thin procedure over the shared framework.

## Stage 4 — managed-service and mobile interfaces

After the paired framework proves a single-node private managed service, Atlas
Suite may add read-only service-health, manifest, evidence, and receipt
workflows. Mutations remain explicit revision-bound commands with current
approval; MCP context never becomes command authority.

An optional Android operator companion may use the same API after it is stable.
The owner has an early-access limited-distribution channel suitable for a small
trusted-device dogfood cohort. The plugin does not store account details,
control Android distribution, or justify building the mobile client by itself.

Exit gate: interface outputs match server receipts, offline/stale states are
obvious, no credential enters a prompt/KB, and every mutation is independently
authorized and observable.

## Publication boundary

V1 includes only a provider-neutral Claude Code marketplace descriptor. Any
later hosted marketplace submission, share link, package publication, or
hosted connection is a separate release with its own sanitized source ledger,
compatibility matrix, security review, installation/removal proof, and explicit
owner approval.
