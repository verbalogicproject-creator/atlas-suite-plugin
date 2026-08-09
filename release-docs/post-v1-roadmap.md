# Atlas Suite roadmap: after v1.0.1

Status: v1.0.1 boundary implemented as a local candidate; later sequencing is proposed

Authority boundary: this file does not authorize installation, cache mutation,
marketplace changes, publication, connectors, models, accounts, deployment, or
managed-service use.

The authoritative system sequence is the paired framework's
`docs/post-v1-roadmap.md`. Atlas Suite follows it without creating a second
runtime or contract resolver.

## Approved v1.0.1 boundary

Atlas Suite `v1.0.1` is the candidate agent-facing companion to framework
`v0.2.0`. It provides:

- a thin bridge validated through `dkg-framework-interface/1.0` and
  `dkg-cli/1.0`, without a copied engine;
- the interactive menu and scriptable deterministic commands;
- the five Atlas skills, KG-RAG specialist, and Atlas Frontend Designer;
- access to domain mining, qualification, API-schema, and Project Atlas
  operations implemented by the framework; and
- deterministic build, bounded presentation refinement, rebind, and validation
  of the four-file Project Atlas.

It does not ship durable memory, a voice/session runtime, hosted services,
provider credentials, agent orchestration, deployment controls, or a Command
Center UI.

## Post-v1.0.1 discovery program

After the paired releases close, run one joint framework/plugin deep dive
before assigning later plugin versions. The plugin roadmap must follow the
framework's `v0.2.0`-to-stable contract decisions rather than inventing a
parallel source of truth.

### Track A - bounded continuity context

- Expose optional boot, task, evidence, dependency-walk, and handoff projections
  from a validated Project Atlas.
- Bind repository identity, Atlas revision, selected evidence, capability
  versions, plan, omissions, degradation, risk, and proof limits.
- Provide visible hash-only drift checks and activation receipts.
- Preserve fail-closed behavior for unknown repositories and incompatible
  framework interfaces.

### Track B - capability and command contracts

- Map every skill and command to a provider-neutral descriptor with version,
  digest, trust state, compatibility range, input/output contract, and proof
  limit.
- Carry command safety classes from the framework: read-only, pending proposal,
  exact-confirmation, human-only, and forbidden.
- Keep installation, model calls, durable mutation, publication, and deployment
  outside skill authority.

### Track C - project and portfolio memory projections

- Consume portable, budgetable context packs and typed relationship projections
  once the framework stabilizes them.
- Support explicit handoff and session-start files without owning a personal
  memory database.
- Keep provider-specific hooks and exports as optional adapters over the same
  canonical artifacts.

### Track D - optional Command Center integration

- Treat Command Center as a separate application that consumes Atlas artifacts
  and receipts through a bounded adapter.
- Keep its Capability Library, Handoff Builder, graph canvas, Aria voice/session
  runtime, persistent workspace memory, pairing, hosted MCP/REST service,
  deployment, and telemetry outside Atlas Suite.
- Consider read-only MCP or REST integration only after the headless file/CLI
  contracts qualify; UI availability must never be required for validation.

### Stability gate

The maintained plugin line is stable only when clean install, discovery, use,
upgrade, rollback, and removal are reproducible; the framework compatibility
matrix is explicit; all generated artifacts and receipts are inspectable; stale
and offline states are visible; provider adapters return equivalent
deterministic plans; and no optional integration can mutate canonical knowledge
or restore authority.

The 2026-08-09 light scan treated Ubuntu `project_memory` commit `023d634` and
the dirty `command-center-v3` tree at commit `0b20d72` as future design inputs,
not qualified dependencies. Exact source freezes and adoption decisions are
deferred until after framework `v0.2.0` and plugin `v1.0.1` close.

## Earlier sequence retained for provenance

The stages below predate the paired `v0.2.0` and `v1.0.1` targets. They retain
useful qualification and long-range interface gates, but completed or
superseded work does not re-enter the current release scope.

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

## Stage 2.5 - Project Atlas frontend pipeline (implemented candidate)

Implement the approved two-stage frontend pipeline:

- deterministic compiler emits exactly `index.html`, `project-atlas.json`,
  `content.json`, and `design.css`; receipts stay under the state root;
- Atlas Frontend Designer, extracted and customized from Taste discipline,
  proposes only `content.json` presentation fields and `design.css`;
- deterministic rebind regenerates `index.html` and validates protected
  surfaces;
- the optional designer server previews markdown-rendered content through a
  logical renderer adapter;
- protected-surface validation proves canonical data, source digests, proof
  limits, IDs, contract comments, and receipts are unchanged.

Exit gate: static offline Atlas output still validates without a server;
designer output passes protected-surface validation; no artifact records a
device-specific absolute path.

Remaining qualification: independent browser inspection and broader held-out
task-route fixtures across large polyglot repositories.

## Stage 2.6 - Miner and specialized Atlas expansion

- Keep inventory, document, Python-import, relationship, and structural-score
  operators behind the framework's versioned Miner contract.
- Add API-schema extraction as the next deterministic operator, then promote
  API Schema Atlas only after endpoint/type/auth/drift fixtures pass.
- Treat neural vectors and agent-scored named dimensions as isolated derived
  profiles. Promote no profile without held-out relevance, citation,
  repeatability, and context-cost evidence.
- Feed successful extraction and visual patterns into inactive recipe
  candidates; promote only digest-bound candidates that pass regression gates.

Exit gate: each operator is independently replayable, source-bound, and
provider-neutral; specialized Atlases remain knowledge projections rather than
aliases for indexes or scoring machinery.

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
