# Version 1 closure record

## Status and governing identities

Version `1.0.0` is locally release-ready source. It is committed and pushed as
a source candidate, but it is not installed, marketplace-published, deployed,
or released. This conclusion is bound to both verified `ARTIFACTS.sha256`
inventories, the paired final-byte gates below, and the independent closure
verdict for those exact bytes. Any byte change invalidates the conclusion.

The approved local workflow is bound to:

- closure plan: `5f4663d79d277c928ae44adb1b0f96e67f60d9ae3070ffef661bde97b32e3ed7`;
- sealed authority: `ec83463ce635a9c3653424a7af04831ad6a89d056e93107dc86719e50fa16708`;
- Repo Factory lock: `1b59c229526d982d22745d4234849adae1b2d3be8431e9ee21b9c49bd895d99b`;
- Production Auditor lock: `9ecfeb4aa272dad43039b7ab6c2eb9d3468d169161a20d648c5026c115f5afae`.

These identities describe scope and process; they grant no external authority.

## Scope, architecture, and interfaces

The plugin manifest exposes seven skills under `skills/`: Project, Context,
Knowledge, Topology, Evidence-Rules, KG-RAG Specialist, and Atlas Frontend
Designer. Their namespaced interfaces and proof boundaries are described in
the root [`README`](../README.md). `scripts/dkg_bridge.py` is the only
execution bridge; it resolves the paired `deterministic-kg-rag-framework` and
invokes its exact CLI/resolver rather than translating contracts or
implementing a second runtime. Missing framework resolution fails visibly
without fallback.

Atlas Frontend Designer is presentation-only. It may refine `content.json` and
`project-atlas.css` after deterministic compilation, but it cannot mutate
`project-atlas.json`, protected HTML IDs, source digests, proof limits,
contract comments, or receipts.

[`architecture.md`](architecture.md) maps request flow. Skills provide
procedure, routing, and bounded knowledge; canonical state and receipts belong
to the paired framework. A skill, retrieved context, or receipt cannot install
the plugin or authorize any other effect.

## Observed candidate evidence

- Plugin unit discovery passed seven tests.
- Direct and bridged `atlas plan` output was byte-identical for representative
  flags and every preset exercised by the suite.
- Seven manifest-declared skills were present; missing framework resolution
  failed closed.
- Baseline identity and deterministic-RAG KB validation passed, and the source
  contained no marketplace or runtime database/model/environment artifacts.
- The paired framework passed 35 warning-strict tests; its integrity,
  promotion-binding, and exact-text generation repairs are documented in its
  own `docs/v1-closure.md`.
- Repository tests encode all five single flags, all four presets,
  representative/reversed combinations, and nine stateful direct/bridge
  run-and-Boot comparisons.
- Complete baseline reconstruction verifies 63 files against canonical tree
  digest `685dcc96809621c97a3b3f0f4a4ba18692ad1b3de8657452b33acf05470dc72a`.
- The bridge refuses missing, unparseable, incorrectly named, or non-1.x
  framework metadata before importing its CLI.

Deterministic builds, backup/restore, rollback, and blocked acquisition
preflight were rerun through the paired framework on the final candidate. The
plugin remains uninstalled unless fresh exact installation authority is given.

## Deferred gates and non-claims

V1 does not claim persistent plugin installation or fresh-thread dogfood,
marketplace registration, sharing, live source acquisition/promotion, v2
ranking scores, semantic/reranker quality, model serving, Termux/proot
cross-environment operation, publication, deployment, or market validation.

## Final reproduction gate

Keep this repository beside the paired framework. From the plugin root on the
exact final bytes:

```sh
python3 scripts/generate_release_docs.py
python3 scripts/generate_release_docs.py --check
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error::ResourceWarning python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error::ResourceWarning python3 skills/kg-rag-specialist/scripts/validate_deterministic_kb.py
python3 scripts/dkg_bridge.py atlas plan --preset release-review
```

Run the plugin manifest validator and quick validation for all seven skill
directories using the installed development validators, without installing
this candidate. Recompute the preserved baseline identities. Compare direct
and bridged plan bytes for all five single flags, all four presets, representative
combinations, and reversed flag order. Re-run the paired framework's final
closure gates before making a paired conclusion.

The closure run used `validate_plugin.py` digest
`ebda00d55d7518b127f675f062fb5c6e7a1ffdc0a99df1a55ac594400d7d3228`
and `quick_validate.py` digest
`6cc9dc3199c935916cf6f73fcbbbb0e3bb1b58c8f5109fefa499978908164f51`.

## Artifact-manifest procedure

After every source and documentation edit stops, regenerate release docs with
`python3 scripts/generate_release_docs.py`, then generate `ARTIFACTS.sha256`
from repository-relative regular source files, excluding `.git`, ignored
generated docs, caches, virtual environments, build output, and the manifest
itself. Use bytewise path ordering and SHA-256. Review for unexpected or
sensitive files, then run `sha256sum --check ARTIFACTS.sha256`. Verify the
paired framework manifest in the same closure run. Commit, push, installation,
or publication remain separate protected effects. Any later byte change
invalidates the manifest and closure.

## Recovery and protected effects

The uninstalled source tree has no plugin runtime state to roll back. A missing
or incompatible paired framework must stop bridge execution. If a future
approved installation fails, preserve the candidate and installed target for
inspection and use the separately approved removal/reinstall procedure; never
edit another plugin's cache as recovery.

Installation, reinstall, removal, cache update, commit, push, PR creation,
marketplace entry, sharing, publication, deployment, account use, and every
framework protected effect require fresh approval naming the exact target and
scope. Resuming this record never restores approval.
