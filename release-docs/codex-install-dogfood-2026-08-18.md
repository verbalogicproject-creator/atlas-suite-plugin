# Codex local-install dogfood — 2026-08-18

Status: passed with bounded degradations and explicit remaining gaps  
Scope: local marketplace registration, install, update/reinstall, installed
discovery, installed CLI routes, and one fresh read-only Codex skill run  
Proof limit: this is local development evidence. It does not prove hosted
marketplace behavior, removal/rollback, every skill in a separate fresh thread,
frontend design output, model adapters, publication, sharing, deployment, or
behavior on another host.

## Qualified identities

- Source baseline: Atlas Suite `1.1.0` at the observed local source revision.
- Installed build: cachebusted `1.1.0+codex.*` from the host-local
  `atlas-suite-local` marketplace.
- Paired engine: deterministic KG-RAG framework `0.3.0` satisfying the closed
  `>=0.3.0,<0.4.0` compatibility contract.
- Source and installed cache matched after reinstall, excluding ignored local
  dogfood/cache state.

## Pre-install evidence

- plugin manifest validator passed;
- all seven top-level skills passed the installed quick validator;
- generated release documents were fresh;
- deterministic specialist KB validation passed with the original 63-file
  baseline digest and zero failures;
- 14 Atlas Suite tests passed;
- the paired DKG suite passed all 90 local test cases.

## Installation and discovery

The local marketplace was registered from the staging parent so its local
source points at the exact Suite directory. Codex recorded the plugin installed
and enabled. Fresh-process prompt inspection initially revealed eight entries:
the seven intended skills plus a duplicate `kg-rag-specialist` from the pinned
baseline package nested below the active `skills/` tree.

One bounded repair moved the byte-identical baseline skill and agent metadata
to plugin-level `vendor/kg-rag-specialist-baseline`. The baseline canonical
digest remained unchanged. A recursive discovery regression test was added,
the cachebuster/reinstall flow was applied, and fresh Codex discovery then
reported exactly these seven identities once each:

- `project-atlas`
- `context-atlas`
- `knowledge-atlas`
- `topology-atlas`
- `evidence-rules-atlas`
- `kg-rag-specialist`
- `atlas-frontend-designer`

## Installed CLI dogfood

The installed bridge used the paired DKG through explicit
`DKG_FRAMEWORK_ROOT` and passed:

- source-versus-installed plan-byte parity for all five single flags;
- all four presets;
- representative combinations and both user flag orderings;
- four-file Project Atlas build and protected-surface check;
- bounded context selection;
- non-activated repository-domain mining;
- declaration-only API-schema projection;
- backend capability/descriptor inspection;
- signed `record.list` plan and source-body-free answerable read with no
  effects executed.

The four public site files were exactly `index.html`, `project-atlas.json`,
`content.json`, and `design.css`; the receipt remained under isolated state.

Reversed flag requests preserve their original `selection.flags` order and
therefore have different request/plan digests, while their deterministic
execution order is the same. Direct and bridged bytes remain identical for
each exact request.

## Fresh Codex skill dogfood

One ephemeral read-only Codex thread explicitly loaded all seven installed
skills. It read every required skill/contract, ran only the five plan previews
and static specialist validator, and inspected the frontend mutation boundary.

- Project and Topology plans were ready.
- Context was degraded because optional Git capability was not visible in that
  installed read-only context.
- Knowledge and Evidence-Rules were degraded because no optional source ledger
  was supplied to the plan-only request.
- The KG-RAG validator passed with the original 63-file digest and controlling
  18-recipe registry.
- The frontend boundary allowed proposals only for `content.json` presentation
  fields and `design.css`; canonical JSON and protected HTML surfaces remained
  immutable.
- All seven skill names, paths, and skill digests were unique.
- No source write, build, rebind, live query, web request, delegation,
  connector, publication, deployment, or other protected effect was performed
  by that read-only skill run.

## Host configuration

The local source layout resolves a sibling DKG automatically, but a cached
plugin cannot infer that repository sibling. The host therefore injects only
`DKG_FRAMEWORK_ROOT` through Codex `shell_environment_policy.set`. Codex Doctor
confirmed that the configuration loaded. This is a host installation setting,
not a portable plugin artifact.

## Remaining gates

- Start a normal new app thread after this final reinstall and invoke a Suite
  skill without a manual environment prefix.
- Repeat each skill in its own fresh thread if the strict historical Stage-1
  matrix is required.
- Qualify frontend design/rebind visually and functionally.
- Test explicit rollback and separately approved removal only if desired;
  removal is not part of this keep-installed dogfood outcome.
- Preserve publication, sharing, deployment, live acquisition, model adapters,
  and provider use as separate approval boundaries.
