# Capability profiles and qualification

Atlas Suite can now describe combinations as transparent, named operational
tools. A profile does not install, execute, authorize, or hide components. It
expands into the exact component owners and adapters, ordered data flow,
inputs, effects, gates, outputs, tuning choices, and proof limits.

This is the practical meaning of the Suite as an **evidence-governed repository
intelligence platform** and a **deterministic multi-projection compiler**:
Atlas compiles source-grounded views and bounded context; the paired DKG owns
deterministic graph/RAG execution; In-the-Loop supplies workflow authority and
verification contracts; Codex is an acting host only when a separately
authorized task actually runs.

## Cold start

Keep the Suite beside `deterministic-kg-rag-framework`, or set
`DKG_FRAMEWORK_ROOT`. Every bridge and qualification process honors the same
root. In-the-Loop 0.4.1 is an optional external qualification dependency, not
vendored Suite runtime. From the Suite root, start with:

```sh
./scripts/atlas profile list
./scripts/atlas profile describe fullstack-contract-spine
./scripts/atlas profile explain fullstack-contract-spine
./scripts/atlas profile plan fullstack-contract-spine
./scripts/atlas profile qualification fullstack-contract-spine
```

All five routes are read-only and emit canonical JSON. `describe` is the
machine contract; `explain` is the compact composition and tuning view; `plan`
checks whether required adapters are available and still sets
`execution_authorized` to `false`; `qualification` reports evidence and
promotion eligibility. There is intentionally no `atlas profile run` command.

The first three candidate profiles are:

| Profile | What the combination behaves like | Strongest current evidence |
|---|---|---|
| `fullstack-contract-spine` | A cross-root React/FastAPI contract and drift detector | Passing frozen ten-case direct-call fixture, zero false positives and zero false negatives |
| `rag-evidence-firewall` | A deterministic evidence, abstention, refusal, and grounding boundary | Passing paired-DKG Harness Boot replay with repeatability, injection/protected-effect refusal, unknown abstention, and generation grounding |
| `ai-tool-control-plane` | Atlas evidence/context plane + In-the-Loop control plane + Codex acting host | Passing single-run production-roster orientation and deny-then-approved one-file repair, with locked counters, exact authority epoch, frozen tests, and standalone runtime verification |

Passing candidate receipts do not silently promote registry maturity. Receipt
v2 binds the stored result, frozen source/fixture manifest, exact adapter
contracts and stable logical dependency identities, semantic runtime and
dependency environment, and a separately signed standalone-replay verification
record. Checkout locations and absolute Suite/DKG roots are not receipt
identities. The verifier process reruns the
full-stack suite twice, independently rebuilds and queries the isolated RAG
fixture, or validates the AI packet, locks, citations, authority epoch, exact
diff, manifests, and normalized test evidence. Promotion is a separate owner decision and
requires all those bindings to remain current, frozen thresholds to pass, no
failures, and the distinct verifier record to remain valid. The verifier is a
separate local process and implementation artifact, not a separate external
trust domain.

## Qualification and manual testing

Run the complete local replay without writing artifacts:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/qualification_receipts.py
```

Regenerate canonical candidate results and receipts after an intentional
source change:

```sh
DKG_FRAMEWORK_ROOT=/path/to/deterministic-kg-rag-framework \
ATLAS_AI_RUNTIME_ARTIFACT=qualification/ai-control-plane/runs/ai-control-plane-frozen-1/runtime.json \
PYTHONDONTWRITEBYTECODE=1 python3 scripts/qualification_receipts.py --write
```

Run focused verification:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_qualification_core \
  tests.test_profile_cli \
  tests.test_qualification_receipts
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
  tests/test_qualification_ai_control_plane.py \
  tests/test_qualification_scenarios.py
```

When the exact In-the-Loop 0.4.1 linter, locker, roster, and contracts are
absent, only that typed dependency condition becomes a canonical failed AI
result with reason `itl-qualification-contract-unavailable`; the AI receipt is
non-promotable and stored passing evidence is reported stale. Partial,
symlinked, tampered, or stale-lock dependencies remain hard failures.

The results live under `qualification/results/`; standalone-replay verification records
live under `qualification/verifications/`; digest-bound candidate receipts
live under `qualification/receipts/candidates/`. Any result, source, adapter,
DKG/In-the-Loop identity, environment, producer, or verifier drift makes the
old receipt stale or ineligible. Release receipts are deliberately not
produced by this program.

## How to tune a profile

Treat a profile as a versioned recipe, not a bag of prompts:

1. Choose the user intent and declared repository roots.
2. Select only registry components with exact compatible adapters.
3. Set each declared tuning axis, such as context budget, highest contract
   layer, drift policy, or unknown-evidence policy.
4. Inspect every read, write, network, provider, and protected effect.
5. Keep evidence gates separate from authority gates.
6. Freeze positive, negative, boundary, stale, and falsifying cases before
   replaying them.
7. Requalify after any registry, profile, proof-plan, fixture, adapter, or
   environment change. Old digest-bound receipts then become inapplicable.

Never infer runtime compatibility from a shared capability name. Never map
context, a receipt, or recovered session state into authority. A profile can be
architecturally valid but still fail to produce user value; scenario thresholds
must decide that separately.

## Combination patterns and hidden capabilities

The same primitives produce different tools when scope, order, tuning, gates,
and presentation change:

- Atlas context + topology + evidence rules becomes a repository orientation
  packet or impact-analysis map depending on the task and projection order.
- Atlas projections + exact declarations + schema/runtime fixtures becomes a
  cross-root contract spine rather than a generic repository map.
- DKG retrieval + citation validation + refusal/abstention policy becomes an
  evidence firewall rather than merely a search command.
- Atlas grounding + In-the-Loop envelopes + Codex action + independent checks
  forms a dual-plane agent architecture. One non-KG-RAG host scenario now has
  passing candidate evidence; this remains a single-run proof, not a claim of
  repeatability or universal workflow correctness.

The discovery ledger in `qualification/discovery-candidates.json` records
poorly exposed behavior, emergent compositions, missing glue, proposed
capabilities, similarities, and rejected overclaims. A candidate remains a
hypothesis until its next probe and falsifying cases pass. This is how hidden
potential becomes testable without turning possibility into marketing fact.

## Current limits

- Profile discovery and planning are read-only; profiles do not execute.
- The full-stack runtime probe calls the frozen FastAPI endpoint function
  directly. It does not prove HTTP transport, middleware, deployed auth, or
  production reliability.
- The RAG replay is local and deterministic. It does not call a model or
  provider, acquire remote data, promote knowledge, or prove general answer
  correctness.
- The AI control-plane profile has a current passing candidate receipt for one
  frozen production-roster run. Registry maturity remains unchanged until a
  separate owner promotion decision; the evidence does not prove agent
  repeatability, deployment readiness, or correctness outside the fixture.
- No install, reinstall, cache update, publication, deployment, or release is
  performed by the qualification program.
