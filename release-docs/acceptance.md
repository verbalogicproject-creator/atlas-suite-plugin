# Acceptance and release handoff

## Required local checks

- plugin manifest validation passes with seven discoverable skills;
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
- both repository artifact manifests verify after all documentation and source
  bytes stabilize.

## Qualification classification

Implemented: plugin structure, seven namespaced skills, paired DKG bridge,
v0.3 capability gating, task-facing backend access, Atlas frontend design
boundary, baseline preservation, KB v1, validation scripts, and local
documentation.

Deferred: direct installation/removal dogfood, installed-skill invocation in a
fresh Codex thread, live acquisition/promotion, models, v2 ranking replay,
hosted marketplace publication, and publication. The paired framework's exact-text
generation rule is an intentional v1 fail-closed boundary; the plugin does not
weaken or reinterpret it.

## Local release meaning

A candidate becomes locally release-ready source only after the final-byte
checks and exact artifact manifests pass. `ARTIFACTS.sha256` binds the qualified
v1.1 source bytes and must be regenerated after any edit. Release-ready status does not mean
installed or released.
Commit, push, PR, installation, cache update, marketplace entry, share link,
publication, or deployment require separate authority. Any change to the
plugin manifest, active skill instructions, bridge, baseline identities, KB,
or paired contract compatibility invalidates the handoff and requires relevant
checks again.

Future sequencing is documented in [`post-v1-roadmap.md`](post-v1-roadmap.md).
It does not change the current uninstalled, unpublished release boundary.
