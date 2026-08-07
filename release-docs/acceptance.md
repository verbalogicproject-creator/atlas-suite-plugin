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
  editable display/markdown content, and `project-atlas.css` for visual
  refinement;
- plugin tests pass on the exact candidate;
- both repository artifact manifests verify after all documentation and source
  bytes stabilize.

## Qualification classification

Implemented: plugin structure, seven namespaced skills, paired DKG bridge,
Atlas frontend design boundary, baseline preservation, KB v1, validation
scripts, and local documentation.

Deferred: direct installation/removal dogfood, installed-skill invocation in a
fresh Codex thread, live acquisition/promotion, models, v2 ranking replay,
hosted marketplace publication, and publication. The paired framework's exact-text
generation rule is an intentional v1 fail-closed boundary; the plugin does not
weaken or reinterpret it.

## Local release meaning

A candidate becomes locally release-ready source only after the final-byte
checks and exact artifact manifests pass. That status still does not mean
installed or released.
Commit, push, PR, installation, cache update, marketplace entry, share link,
publication, or deployment require separate authority. Any change to the
plugin manifest, active skill instructions, bridge, baseline identities, KB,
or paired contract compatibility invalidates the handoff and requires relevant
checks again.

Future sequencing is documented in [`post-v1-roadmap.md`](post-v1-roadmap.md).
It does not change the current uninstalled, unpublished release boundary.
