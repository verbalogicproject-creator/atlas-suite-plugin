from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from qualification_core import InTheLoopUnavailable, _itl_contract_paths
SCRIPT = ROOT / "scripts" / "qualification_scenarios.py"
SPEC = importlib.util.spec_from_file_location("qualification_scenarios", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
scenarios = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scenarios)


def test_compatible_fixture_passes_and_is_repeatable() -> None:
    first = scenarios.qualify_case("compatible")
    second = scenarios.qualify_case("compatible")
    assert first["observed"] == "pass"
    assert first["expectation_met"] is True
    assert first["result_sha256"] == second["result_sha256"]
    assert [check["layer"] for check in first["checks"]] == list(scenarios.LAYERS)


def test_every_frozen_drift_is_detected_at_its_declared_layer() -> None:
    cases = scenarios._load(scenarios.FIXTURE / "cases.json")["cases"]
    for case in cases:
        result = scenarios.qualify_case(case["id"])
        assert result["expectation_met"] is True, result
        assert result["detected_layer"] == case["expected_layer"]
    suite = scenarios.qualify_suite()
    assert suite["status"] == "passed"
    assert suite["metrics"] == {"cases": 10, "false_positives": 0, "false_negatives": 0}
    assert suite["result_sha256"] == scenarios.qualify_suite()["result_sha256"]


def test_positive_fastapi_direct_call_is_environment_bound() -> None:
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    result = scenarios.qualify_case("compatible", execute_runtime=True)
    assert result["observed"] == "pass"
    assert result["runtime_binding"]["probe"] == "direct-endpoint-call"
    assert "HTTP transport" in result["proof_limit"]


def test_dkg_exact_cross_root_same_capability_seam() -> None:
    if not scenarios.DKG_PACK.is_file() or shutil.which("git") is None:
        pytest.skip("DKG sibling and git are required for the cross-root seam")
    result = scenarios.qualify_dkg_same_capability()
    assert result["status"] == "passed", result
    assert result["same_capability_count"] == 1
    assert result["root_count"] == 2
    assert "no schema, HTTP, auth, or runtime compatibility" in result["proof_limit"]


def test_non_kg_rag_workflow_has_static_control_boundaries() -> None:
    result = scenarios.validate_workflow()
    assert result["status"] == "passed", result
    assert result["node_count"] == 3
    assert result["result_sha256"] == scenarios.validate_workflow()["result_sha256"]


def test_non_kg_rag_workflow_passes_authoritative_itl_linter_when_available() -> None:
    try:
        linter = _itl_contract_paths(ROOT)["linter"]
    except InTheLoopUnavailable:
        pytest.skip("exact In-the-Loop 0.4.1 qualification contract is unavailable")
    completed = subprocess.run(
        [sys.executable, str(linter), str(scenarios.WORKFLOW)],
        check=False,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_discovery_candidates_are_falsifiable_and_unpromoted() -> None:
    result = scenarios.validate_discovery_ledger()
    assert result["status"] == "passed", result
    assert result["candidate_count"] == 3
    ledger = scenarios._load(scenarios.DISCOVERY)
    rejected = [candidate for candidate in ledger["candidates"] if candidate["standing"] == "rejected"]
    assert rejected and all(candidate.get("rejection_reason") for candidate in rejected)
    assert all(candidate["maturity"] == "candidate" for candidate in ledger["candidates"])
