#!/usr/bin/env python3
"""Replay the three frozen profile plans and emit candidate evidence receipts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from qualification_core import build_current_bindings, canonical_bytes, digest, load_json, validate_profile, validate_proof_plan, validate_receipt, validate_registry, validate_verification_record
from qualification_scenarios import qualify_suite, validate_workflow
from qualification_ai_control_plane import absent_result, verify_runtime


ROOT = Path(__file__).resolve().parents[1]
DKG_ROOT = ROOT.parent / "deterministic-kg-rag-framework"
VERIFIER = ROOT / "scripts" / "qualification_verifier.py"


def _signed(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.pop("result_sha256", None)
    result["result_sha256"] = digest(result)
    return result


def _rag_replay() -> dict[str, Any]:
    if not (DKG_ROOT / "src" / "dkg").is_dir():
        return {"schema": "atlas-rag-firewall-result/1.0", "status": "failed", "failures": ["paired-dkg-unavailable"], "checks": [], "proof_limit": "No paired DKG runtime was available."}
    environment = {**os.environ, "PYTHONPATH": str(DKG_ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        source = temp / "source"
        (source / "docs").mkdir(parents=True)
        (source / "contract.json").write_bytes((ROOT / "qualification" / "fixtures" / "fullstack-contract-spine" / "contract.json").read_bytes())
        (source / "docs" / "architecture.md").write_bytes((ROOT / "release-docs" / "architecture.md").read_bytes())
        state = temp / "state"
        subprocess.run([sys.executable, "-m", "dkg", "atlas", "run", "--flags", "project,knowledge", "--source", str(source), "--state-root", str(state)], env=environment, check=True, capture_output=True)
        completed = subprocess.run([sys.executable, "-m", "dkg", "boot", "--state-root", str(state)], env=environment, check=True, capture_output=True)
        query_arguments = [sys.executable, "-m", "dkg", "query", "What architecture is documented?", "--state-root", str(state)]
        query_first = subprocess.run(query_arguments, env=environment, check=True, capture_output=True).stdout
        query_second = subprocess.run(query_arguments, env=environment, check=True, capture_output=True).stdout
    boot = json.loads(completed.stdout)
    wanted = {"deterministic-query", "injection-refusal", "protected-effect-refusal", "unknown-abstention", "generation-grounding"}
    checks = [item for item in boot["checks"] if item["id"] in wanted]
    query_result = json.loads(query_first)
    evidence = query_result["packet"]["evidence"]
    citations_valid = bool(evidence) and all(
        isinstance(item.get("citation_id"), str)
        and isinstance(item.get("source"), dict)
        and isinstance(item["source"].get("logical_path"), str)
        and isinstance(item["source"].get("sha256"), str)
        for item in evidence
    )
    checks.append({"id": "citation-validity", "status": "passed" if citations_valid else "failed", "detail": len(evidence)})
    checks.append({"id": "query-byte-repeatability", "status": "passed" if query_first == query_second else "failed", "detail": digest(query_first)})
    return _signed({
        "schema": "atlas-rag-firewall-result/1.0",
        "status": "passed" if boot["status"] == "passed" and len(checks) == len(wanted) + 2 and all(item["status"] == "passed" for item in checks) else "failed",
        "failures": boot["failures"],
        "checks": checks,
        "upstream_receipt_sha256": boot["receipt_sha256"],
        "proof_limit": "Local deterministic DKG Harness Boot over one frozen corpus; no provider, remote retrieval, active-knowledge promotion, or general answer-quality claim.",
    })


def replay_results() -> dict[str, dict[str, Any]]:
    fullstack_first = qualify_suite(execute_runtime=True)
    fullstack_second = qualify_suite(execute_runtime=True)
    rag_first = _rag_replay()
    rag_second = _rag_replay()
    runtime_path = os.environ.get("ATLAS_AI_RUNTIME_ARTIFACT")
    ai_result = verify_runtime(load_json(Path(runtime_path))) if runtime_path else absent_result()
    return {
        "fullstack-contract-spine": _signed({**fullstack_first, "repeatable": fullstack_first == fullstack_second}),
        "rag-evidence-firewall": _signed({**rag_first, "repeatable": rag_first == rag_second}),
        "ai-tool-control-plane": ai_result,
    }


def _standalone_verification(profile_id: str, observation: dict[str, Any]) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(VERIFIER), profile_id], input=canonical_bytes(observation),
        capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise RuntimeError(f"standalone verifier failed: {completed.stderr.decode(errors='replace').strip()}")
    return validate_verification_record(json.loads(completed.stdout))


def _receipt(profile_id: str, observation: dict[str, Any], bindings: dict[str, Any], verification: dict[str, Any]) -> dict[str, Any]:
    registry = validate_registry(load_json(ROOT / "qualification" / "capability-registry.json"))
    profile = validate_profile(load_json(ROOT / "qualification" / "profiles" / f"{profile_id}.atlas-profile.json"), registry)
    plan = validate_proof_plan(load_json(ROOT / "qualification" / "proof-plans" / f"{profile_id}.proof-plan.json"), registry)
    if plan["profile_id"] != profile["id"] or plan["claim_ids"] != [item["id"] for item in profile["components"]]:
        raise ValueError("proof plan is not bound to the exact profile component order")
    if profile_id == "fullstack-contract-spine":
        metrics = observation["metrics"]
        results = {
            "compatible_cases_preserved_min": 1 if observation["results"][0]["expectation_met"] else 0,
            "false_negative_count_max": metrics["false_negatives"],
            "false_positive_count_max": metrics["false_positives"],
            "injected_drift_detected_min": sum(item["case_id"] != "compatible" and item["expectation_met"] for item in observation["results"]),
        }
        passed = observation["status"] == "passed" and observation["repeatable"]
        failures = [] if passed else ["fullstack-fixture-replay-failed"]
    elif profile_id == "rag-evidence-firewall":
        checks = {item["id"]: item["status"] == "passed" for item in observation["checks"]}
        results = {
            "citation_validity_min": 1 if checks.get("citation-validity") else 0,
            "injection_refusal_min": 1 if checks.get("injection-refusal") else 0,
            "repeatability_min": 1 if observation["repeatable"] else 0,
            "unsupported_answer_count_max": 0 if checks.get("generation-grounding") else 1,
        }
        passed = observation["status"] == "passed" and observation["repeatable"]
        failures = list(observation["failures"]) if not passed else []
    else:
        results = observation["metrics"]
        failures = list(observation["failures"])
        passed = observation["status"] == "passed" and not failures
    verification_ref = profile["qualification"]["verification_refs"][0]
    receipt_bindings = {**bindings, "verification": {"ref": verification_ref, "sha256": verification["verification_sha256"]}}
    unsigned = {
        "schema": "atlas-qualification-receipt/2.0",
        "receipt_id": f"receipt.{profile_id}.candidate-1",
        "claim_ids": plan["claim_ids"],
        "profile_id": profile_id,
        "registry_sha256": digest(registry),
        "profile_sha256": digest(profile),
        "proof_plan_sha256": digest(plan),
        "frozen_thresholds": plan["frozen_thresholds"],
        "results": results,
        "status": "passed" if passed else "failed",
        "freshness": "current",
        "failures": failures,
        "independent_verification": True,
        "bindings": receipt_bindings,
        "proof_limit": observation["proof_limit"],
    }
    receipt = {**unsigned, "receipt_sha256": digest(unsigned)}
    return validate_receipt(receipt, registry_sha256=digest(registry), profile_sha256=digest(profile))


def generate(write: bool = False) -> dict[str, Any]:
    observations = replay_results()
    registry = validate_registry(load_json(ROOT / "qualification" / "capability-registry.json"))
    bindings = {}
    verifications = {}
    for profile_id, observation in observations.items():
        profile = validate_profile(load_json(ROOT / "qualification" / "profiles" / f"{profile_id}.atlas-profile.json"), registry)
        bindings[profile_id] = build_current_bindings(profile_id, profile, registry, ROOT, observation)
        verifications[profile_id] = _standalone_verification(profile_id, observation)
    receipts = {profile_id: _receipt(profile_id, observation, bindings[profile_id], verifications[profile_id]) for profile_id, observation in observations.items()}
    if write:
        results_root = ROOT / "qualification" / "results"
        receipts_root = ROOT / "qualification" / "receipts" / "candidates"
        verifications_root = ROOT / "qualification" / "verifications"
        results_root.mkdir(parents=True, exist_ok=True)
        receipts_root.mkdir(parents=True, exist_ok=True)
        verifications_root.mkdir(parents=True, exist_ok=True)
        for profile_id in sorted(observations):
            (results_root / f"{profile_id}.result.json").write_bytes(canonical_bytes(observations[profile_id]))
            (verifications_root / f"{profile_id}.verification.json").write_bytes(canonical_bytes(verifications[profile_id]))
            (receipts_root / f"{profile_id}.receipt.json").write_bytes(canonical_bytes(receipts[profile_id]))
    return {"schema": "atlas-qualification-replay/2.0", "observations": observations, "verifications": verifications, "receipts": receipts}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write canonical candidate results and receipts under qualification/")
    args = parser.parse_args()
    result = generate(write=args.write)
    print(canonical_bytes(result).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
