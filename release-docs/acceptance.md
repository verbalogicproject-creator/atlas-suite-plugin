# Acceptance and release handoff

## Required local checks

- plugin manifest validation and fresh-process Codex discovery pass with
  exactly seven active skills; pinned reference packages do not add duplicate
  skill identities;
- every skill passes quick validation and contains no placeholders;
- plugin/direct plan stdout is byte-identical for all presets and representative flags;
- the bridge fails closed when the framework cannot be resolved;
- baseline cookbook and recipe registry match pinned digests and 18 recipes;
- deterministic-RAG KB validation passes and claim sources resolve;
- source contains no install action, credentials, cache, model, database,
  private body, or absolute device path;
- the provider-neutral Claude Code marketplace descriptor has no product gate,
  provider account requirement, model-provider requirement, or runtime network
  requirement;
- Project Atlas frontend docs preserve the source-of-truth split:
  `project-atlas.json` for verifiable canonical data, `content.json` for
  bounded presentation context, `design.css` for visual refinement, and
  compiler-owned `index.html` for the agent map;
- the public Atlas bundle has exactly four files and its build/rebind receipts
  remain under the state root;
- the bridge validates framework `>=0.3.0,<0.4.0`, the exact interface, and the
  required v0.3 capability set before import;
- direct/bridged domain-pack, API-schema, backend
  capabilities/describe/plan/run, and governed abstain/refuse outputs are
  byte-identical;
- menu choices 9 and 10 expose repository-domain mining and declaration-only
  API inspection without creating a second plugin engine;
- held-out task routing passes its predeclared Recall@K, MRR, citation,
  token-cost, and repeatability thresholds;
- plugin tests pass on the exact candidate;
- profile registry/schema/proof-plan contracts reject unknown or ambiguous
  fields, adapters, components, authority sources, and stale receipt digests;
- profile CLI output is canonical and read-only, and no execution route exists;
- full-stack and RAG candidate receipts replay byte-identically, while the AI
  candidate binds one real production-roster host run; all three pass frozen
  thresholds with separately signed standalone verification records;
  result/source/adapter/environment/verifier drift is ineligible;
- both repository artifact manifests verify after all documentation and source
  bytes stabilize.

## Qualification classification

Implemented: plugin structure, seven namespaced skills, paired DKG bridge,
v0.3 capability gating, task-facing backend access, Atlas frontend design
boundary, baseline preservation, KB v1, validation scripts, and local
documentation.

Observed locally: direct Codex installation, cachebusted update/reinstall,
fresh-process discovery of exactly seven unique skills, one fresh read-only
Codex thread using all seven skills, installed bridge plans, four-file build
and check, bounded context, domain/API projection, and backend plan/run.

Deferred: removal, rollback to an older installed pointer,
one-fresh-thread-per-skill repetition, frontend design generation, live
acquisition/promotion, model adapters, v2 ranking replay, hosted marketplace
publication, sharing, and deployment. The paired framework's exact-text
generation rule is an intentional v1 fail-closed boundary; the plugin does not
weaken or reinterpret it.

Qualification addition: the capability registry, three transparent candidate
profiles, proof plans, React/FastAPI drift fixture, non-KG-RAG In-the-Loop
workflow contract, discovery ledger, and read-only CLI are implemented. All
three receipts are current promotion-eligible candidate evidence, but
registry promotion is not automatic. The AI control-plane result is limited to
one frozen production-roster orientation and deny-then-approved repair, so it
does not establish repeatability, deployment readiness, or general correctness.

## Local release meaning

A candidate becomes locally release-ready source only after the final-byte
checks and exact artifact manifests pass. `ARTIFACTS.sha256` binds the qualified
v1.1 source bytes and must be regenerated after any edit. Release-ready status does not mean
hosted, published, deployed, shared, or released. A separately approved local
development installation is recorded in the Codex dogfood receipt.
Commit, push, PR, installation, cache update, marketplace entry, share link,
publication, or deployment require separate authority. Any change to the
plugin manifest, active skill instructions, bridge, baseline identities, KB,
or paired contract compatibility invalidates the handoff and requires relevant
checks again.

Future sequencing is documented in [`post-v1-roadmap.md`](post-v1-roadmap.md).
It does not change the current unpublished and undeployed release boundary.
