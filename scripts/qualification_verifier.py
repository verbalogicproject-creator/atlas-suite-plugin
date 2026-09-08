#!/usr/bin/env python3
"""Standalone read-only verifier that independently replays frozen qualification."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from qualification_core import build_current_bindings, canonical_bytes, digest, dkg_root, load_json, validate_profile, validate_registry, validate_verification_record
from qualification_scenarios import qualify_suite, validate_workflow
from qualification_ai_control_plane import absent_result, verify_runtime


ROOT = Path(__file__).resolve().parents[1]
PRODUCER = ROOT / "scripts" / "qualification_receipts.py"
VERIFIER = Path(__file__).resolve()
DKG_ROOT = dkg_root(ROOT)


def _raw_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check(identifier: str, passed: bool, detail: str) -> dict[str, str]:
    return {"id": identifier, "status": "passed" if passed else "failed", "detail": detail}


def _signed_result(value: dict[str, Any]) -> dict[str, Any]:
    unsigned = dict(value)
    unsigned.pop("result_sha256", None)
    return {**unsigned, "result_sha256": digest(unsigned)}


def _fullstack_checks(result: dict[str, Any], bindings: dict[str, Any]) -> list[dict[str, str]]:
    cases = load_json(ROOT / "qualification" / "fixtures" / "fullstack-contract-spine" / "cases.json")["cases"]
    expected = {item["id"]: (item["expected"], item["expected_layer"]) for item in cases}
    observed = {item.get("case_id"): item for item in result.get("results", [])}
    exact_cases = set(observed) == set(expected) and all(
        item.get("expected") == expected[identifier][0]
        and item.get("expected_layer") == expected[identifier][1]
        and item.get("expectation_met") is True
        for identifier, item in observed.items() if identifier in expected
    )
    compatible = observed.get("compatible", {})
    runtime = compatible.get("runtime_binding") or {}
    dependencies = bindings["environment"]["boundary"]["dependencies"]
    runtime_bound = all(runtime.get(name) == version for name, version in dependencies.items()) and runtime.get("probe") == "direct-endpoint-call"
    false_positives = sum(item.get("expected") == "pass" and item.get("observed") != "pass" for item in observed.values())
    false_negatives = sum(item.get("expected") == "fail" and item.get("observed") != "fail" for item in observed.values())
    metrics = result.get("metrics") == {"cases": len(expected), "false_positives": false_positives, "false_negatives": false_negatives}
    first = qualify_suite(execute_runtime=True)
    second = qualify_suite(execute_runtime=True)
    replayed = _signed_result({**first, "repeatable": canonical_bytes(first) == canonical_bytes(second)})
    return [
        _check("independent-double-replay", canonical_bytes(first) == canonical_bytes(second), "standalone verifier reran every frozen variant twice with byte-identical canonical suite output"),
        _check("candidate-replay-match", canonical_bytes(result) == canonical_bytes(replayed), "candidate result exactly matches the standalone verifier replay"),
        _check("frozen-case-ledger", exact_cases, "stored cases exactly match the frozen case IDs, expectations, and detection layers"),
        _check("metrics-recomputed", metrics, "false-positive and false-negative metrics were recomputed from stored cases"),
        _check("runtime-environment", runtime_bound, "compatible direct-call versions match the bound environment"),
        _check("result-outcome", result.get("status") == "passed" and result.get("repeatable") is True, "stored suite passed and recorded byte repeatability"),
    ]


def _rag_replay() -> dict[str, Any]:
    environment = {**os.environ, "PYTHONPATH": str(DKG_ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        source = temp / "source"
        (source / "docs").mkdir(parents=True)
        inputs = {
            "contract.json": ROOT / "qualification" / "fixtures" / "fullstack-contract-spine" / "contract.json",
            "docs/architecture.md": ROOT / "release-docs" / "architecture.md",
        }
        for logical, origin in inputs.items():
            target = source / logical
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(origin.read_bytes())
        state = temp / "state"
        subprocess.run([sys.executable, "-m", "dkg", "atlas", "run", "--flags", "project,knowledge", "--source", str(source), "--state-root", str(state)], env=environment, check=True, capture_output=True)
        boot_run = subprocess.run([sys.executable, "-m", "dkg", "boot", "--state-root", str(state)], env=environment, check=True, capture_output=True)
        arguments = [sys.executable, "-m", "dkg", "query", "What architecture is documented?", "--state-root", str(state)]
        query_first = subprocess.run(arguments, env=environment, check=True, capture_output=True).stdout
        query_second = subprocess.run(arguments, env=environment, check=True, capture_output=True).stdout
        boot = json.loads(boot_run.stdout)
        query = json.loads(query_first)
        evidence = query["packet"]["evidence"]
        citations_valid = bool(evidence)
        for item in evidence:
            citation_source = item.get("source", {})
            logical = citation_source.get("logical_path")
            expected = citation_source.get("sha256")
            candidate = source / logical if isinstance(logical, str) else source
            citations_valid = citations_valid and candidate.is_file() and not candidate.is_symlink() and hashlib.sha256(candidate.read_bytes()).hexdigest() == expected
    wanted = {"deterministic-query", "injection-refusal", "protected-effect-refusal", "unknown-abstention", "generation-grounding"}
    checks = [item for item in boot["checks"] if item["id"] in wanted]
    checks.append({"id": "citation-validity", "status": "passed" if citations_valid else "failed", "detail": len(evidence)})
    checks.append({"id": "query-byte-repeatability", "status": "passed" if query_first == query_second else "failed", "detail": digest(query_first)})
    return _signed_result({
        "schema": "atlas-rag-firewall-result/1.0",
        "status": "passed" if boot["status"] == "passed" and len(checks) == len(wanted) + 2 and all(item["status"] == "passed" for item in checks) else "failed",
        "failures": boot["failures"], "checks": checks, "upstream_receipt_sha256": boot["receipt_sha256"],
        "proof_limit": "Local deterministic DKG Harness Boot over one frozen corpus; no provider, remote retrieval, active-knowledge promotion, or general answer-quality claim.",
    })


def _rag_checks(result: dict[str, Any], bindings: dict[str, Any]) -> list[dict[str, str]]:
    required = {"deterministic-query", "injection-refusal", "protected-effect-refusal", "unknown-abstention", "generation-grounding", "citation-validity", "query-byte-repeatability"}
    checks = {item.get("id"): item.get("status") for item in result.get("checks", [])}
    dkg_contracts = [item["contract"] for item in bindings["adapter_bindings"]["items"] if item["adapter"].startswith("dkg-")]
    contract_ok = len(dkg_contracts) == 1 and dkg_contracts[0].get("schema") == "dkg-framework-interface/1.0" and dkg_contracts[0].get("cli_contract") == "dkg-cli/1.0"
    upstream = result.get("upstream_receipt_sha256")
    first = _rag_replay()
    second = _rag_replay()
    replayed = _signed_result({**first, "repeatable": canonical_bytes(first) == canonical_bytes(second)})
    return [
        _check("independent-double-replay", canonical_bytes(first) == canonical_bytes(second), "standalone verifier rebuilt isolated DKG state twice with byte-identical canonical replay output"),
        _check("candidate-replay-match", canonical_bytes(result) == canonical_bytes(replayed), "candidate result exactly matches the standalone isolated replay with resolved citation hashes"),
        _check("frozen-check-set", set(checks) == required and all(status == "passed" for status in checks.values()), "all seven frozen evidence-firewall checks are present and passed"),
        _check("dkg-contract", contract_ok, "paired DKG identity satisfies the complete bridge contract"),
        _check("upstream-receipt", isinstance(upstream, str) and len(upstream) == 64, "stored result binds the DKG Harness Boot receipt digest"),
        _check("result-outcome", result.get("status") == "passed" and result.get("repeatable") is True and result.get("failures") == [], "stored replay passed without failures and recorded repeatability"),
    ]


def _ai_checks(result: dict[str, Any], _bindings: dict[str, Any]) -> list[dict[str, str]]:
    replayed = absent_result() if result.get("runtime") is None else verify_runtime(result["runtime"])
    runtime_present = result.get("runtime") is not None
    return [
        _check("independent-static-replay", result.get("static_validation", {}).get("status") == "passed", "standalone verifier rebuilt packet, fixture, workflow, production-lock, and adversarial checks"),
        _check("candidate-replay-match", canonical_bytes(result) == canonical_bytes(replayed), "candidate exactly matches independent validation of its embedded runtime artifact or explicit absence"),
        _check("runtime-evidence-state", (runtime_present and result.get("status") == "passed") or (not runtime_present and result.get("status") == "failed"), "runtime presence and candidate outcome agree"),
    ]


def verify_result(profile_id: str, result: dict[str, Any], bindings: dict[str, Any]) -> dict[str, Any]:
    unsigned_result = {key: value for key, value in result.items() if key != "result_sha256"}
    common = [
        _check("result-digest", result.get("result_sha256") == digest(unsigned_result) == bindings["result"]["sha256"], "stored result and receipt binding have the same canonical digest"),
        _check("source-manifest", bindings["source_manifest"]["sha256"] == digest(bindings["source_manifest"]["files"]), "fixture and executable source files are digest-bound"),
        _check("adapter-bindings", bindings["adapter_bindings"]["sha256"] == digest(bindings["adapter_bindings"]["items"]), "component owners, adapters, contracts, and source identities are digest-bound"),
        _check("environment-binding", bindings["environment"]["sha256"] == digest(bindings["environment"]["boundary"]), "Python, platform, roots, and runtime dependencies are digest-bound"),
    ]
    if profile_id == "fullstack-contract-spine":
        checks = common + _fullstack_checks(result, bindings)
        candidate_passed = result.get("status") == "passed"
    elif profile_id == "rag-evidence-firewall":
        checks = common + _rag_checks(result, bindings)
        candidate_passed = result.get("status") == "passed"
    elif profile_id == "ai-tool-control-plane":
        checks = common + _ai_checks(result, bindings)
        candidate_passed = result.get("status") == "passed"
    else:
        raise ValueError(f"unsupported verification profile: {profile_id}")
    verifier_ok = all(item["status"] == "passed" for item in checks)
    failures = [item["id"] for item in checks if item["status"] != "passed"]
    if verifier_ok and not candidate_passed:
        failures.append("candidate-result-failed")
    unsigned = {
        "schema": "atlas-qualification-verification/1.0",
        "verification_id": f"verification.{profile_id}.candidate-1",
        "profile_id": profile_id,
        "producer": "scripts/qualification_receipts.py",
        "producer_sha256": _raw_sha(PRODUCER),
        "verifier": "scripts/qualification_verifier.py",
        "verifier_sha256": _raw_sha(VERIFIER),
        "result_ref": bindings["result"]["ref"],
        "result_sha256": bindings["result"]["sha256"],
        "source_manifest_sha256": bindings["source_manifest"]["sha256"],
        "adapter_bindings_sha256": bindings["adapter_bindings"]["sha256"],
        "environment_sha256": bindings["environment"]["sha256"],
        "checks": checks,
        "outcome": "verified-pass" if verifier_ok and candidate_passed else "verified-fail",
        "failures": failures,
        "proof_limit": (
            "Standalone local-process replay validates one observed parent-driven native agent/provider run, frozen evidence, and exact bindings; producer and verifier remain in the same repository and host trust domain. No repeatability, promotion, deployment, or publication claim."
            if profile_id == "ai-tool-control-plane" and result.get("runtime") is not None
            else "Standalone local-process replay and validation of frozen evidence and exact bindings; producer and verifier remain in the same repository and host trust domain. No profile execution, authority, promotion, network, provider, deployment, or publication effect."
        ),
    }
    return validate_verification_record({**unsigned, "verification_sha256": digest(unsigned)})


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: qualification_verifier.py PROFILE_ID", file=sys.stderr)
        return 2
    profile_id = arguments[0]
    try:
        def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            value: dict[str, Any] = {}
            for key, item in pairs:
                if key in value:
                    raise ValueError(f"duplicate JSON key: {key}")
                value[key] = item
            return value
        result = json.loads(sys.stdin.buffer.read(), object_pairs_hook=reject_duplicates)
        registry = validate_registry(load_json(ROOT / "qualification" / "capability-registry.json"))
        profile = validate_profile(load_json(ROOT / "qualification" / "profiles" / f"{profile_id}.atlas-profile.json"), registry)
        bindings = build_current_bindings(profile_id, profile, registry, ROOT, result)
        verification = verify_result(profile_id, result, bindings)
    except Exception as exc:
        print(f"atlas-verifier: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_bytes(verification))
    return 0 if verification["outcome"] == "verified-pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
