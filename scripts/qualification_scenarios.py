#!/usr/bin/env python3
"""Frozen Phase 4-6 scenario qualification without network or repository writes."""

from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "qualification" / "fixtures" / "fullstack-contract-spine"
WORKFLOW = ROOT / "qualification" / "workflows" / "repository-orientation.itl.md"
DISCOVERY = ROOT / "qualification" / "discovery-candidates.json"
DKG_ROOT = ROOT.parent / "deterministic-kg-rag-framework"
DKG_PACK = DKG_ROOT / "config" / "domain-packs" / "repository-architecture-v2.json"
LAYERS = (
    "declaration-identity",
    "source-freshness",
    "api-schema",
    "contract-fixture",
    "runtime-integration",
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def _signed(value: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result["result_sha256"] = hashlib.sha256(_canonical(result)).hexdigest()
    return result


def _set_path(value: dict[str, Any], dotted: str, replacement: Any) -> None:
    current: dict[str, Any] = value
    parts = dotted.split(".")
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            raise ValueError(f"mutation parent is not an object: {dotted}")
        current = child
    current[parts[-1]] = replacement


def _symbol_present(root: Path, reference: str) -> bool:
    if "#" not in reference:
        return False
    logical_path, symbol = reference.rsplit("#", 1)
    path = root / logical_path
    if not path.is_file() or not symbol:
        return False
    source = path.read_text(encoding="utf-8")
    patterns = (
        rf"\b(?:async\s+)?def\s+{re.escape(symbol)}\s*\(",
        rf"\bfunction\s+{re.escape(symbol)}\s*\(",
        rf"\b(?:const|let|var)\s+{re.escape(symbol)}\b",
    )
    return any(re.search(pattern, source) for pattern in patterns)


def _baseline_state() -> dict[str, Any]:
    contract = _load(FIXTURE / "contract.json")
    frontend_declaration = _load(FIXTURE / "frontend" / "capabilities.json")["dkg_capabilities"][0]
    backend_declaration = _load(FIXTURE / "backend" / "capabilities.json")["dkg_capabilities"][0]
    ledger = _load(FIXTURE / "source-ledger.json")["files"]
    contract["frontend"]["capability_id"] = frontend_declaration["id"]
    contract["backend"]["capability_id"] = backend_declaration["id"]
    contract["ledger"] = ledger
    contract["ledger_backend_app_sha256"] = ledger["backend/app.py"]
    return contract


def _case(case_id: str) -> dict[str, Any]:
    cases = _load(FIXTURE / "cases.json")["cases"]
    try:
        return next(case for case in cases if case["id"] == case_id)
    except StopIteration as exc:
        raise ValueError(f"unknown case: {case_id}") from exc


def _failure(layer: str, code: str, detail: str) -> dict[str, str]:
    return {"layer": layer, "code": code, "detail": detail}


def _runtime_payload() -> tuple[list[dict[str, Any]], dict[str, str]]:
    try:
        import fastapi
        import httpx
        import pydantic
    except ImportError as exc:
        raise RuntimeError(f"optional runtime dependency unavailable: {exc.name}") from exc
    module_path = FIXTURE / "backend" / "app.py"
    spec = importlib.util.spec_from_file_location("atlas_frozen_fastapi_fixture", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen FastAPI fixture")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    models = asyncio.run(module.list_tasks("fixture-token"))
    payload = [item.model_dump(mode="json") for item in models]
    binding = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "fastapi": fastapi.__version__,
        "httpx": httpx.__version__,
        "pydantic": pydantic.__version__,
        "probe": "direct-endpoint-call",
    }
    return payload, binding


def qualify_case(case_id: str, *, execute_runtime: bool = False) -> dict[str, Any]:
    case = _case(case_id)
    state = _baseline_state()
    for mutation in case["mutations"]:
        _set_path(state, mutation["field"], mutation["value"])
    checks: list[dict[str, Any]] = []
    failure: dict[str, str] | None = None

    frontend = state["frontend"]
    backend = state["backend"]
    if (
        frontend.get("capability_id") != state["capability_id"]
        or backend.get("capability_id") != state["capability_id"]
        or not _symbol_present(FIXTURE / "frontend", frontend["implementation"])
        or not _symbol_present(FIXTURE / "backend", backend["implementation"])
    ):
        failure = _failure("declaration-identity", "capability-anchor-unresolved", "Both explicit tasks.list declarations and exact path#symbol anchors are required; name similarity is ignored.")
    checks.append({"layer": "declaration-identity", "status": "failed" if failure else "passed"})

    if failure is None:
        stale = []
        for logical_path, expected in sorted(state["ledger"].items()):
            if logical_path == "backend/app.py":
                expected = state["ledger_backend_app_sha256"]
            observed = hashlib.sha256((FIXTURE / logical_path).read_bytes()).hexdigest()
            if observed != expected:
                stale.append(logical_path)
        if stale:
            failure = _failure("source-freshness", "source-ledger-stale", ", ".join(stale))
        checks.append({"layer": "source-freshness", "status": "failed" if stale else "passed"})

    schema = _load(FIXTURE / "backend" / "openapi.json")
    schema_path = schema["paths"].get(backend["route"])
    operation = schema_path.get(backend["method"].lower()) if isinstance(schema_path, dict) else None
    if failure is None:
        schema_ok = isinstance(operation, dict) and str(backend["success_status"]) in operation.get("responses", {}) and str(backend["error_status"]) in operation.get("responses", {})
        if not schema_ok:
            failure = _failure("api-schema", "backend-contract-not-in-schema", "Backend route, method, success, or error declaration differs from frozen OpenAPI.")
        checks.append({"layer": "api-schema", "status": "passed" if schema_ok else "failed"})

    task_schema = schema["components"]["schemas"]["Task"]
    schema_properties = {name: item["type"] for name, item in task_schema["properties"].items()}
    schema_auth = next(iter(schema["components"]["securitySchemes"].values()))["scheme"]
    if failure is None:
        contract_ok = (
            frontend["route"] == backend["route"]
            and frontend["method"] == backend["method"]
            and frontend["auth"] == backend["auth"] == schema_auth
            and frontend["success_status"] == backend["success_status"]
            and frontend["error_status"] == backend["error_status"]
            and frontend["response"]["type"] == "array"
            and frontend["response"]["required"] == task_schema["required"]
            and frontend["response"]["properties"] == schema_properties
        )
        if not contract_ok:
            failure = _failure("contract-fixture", "frontend-backend-contract-drift", "Normalized route, method, auth, error, or response declarations differ.")
        checks.append({"layer": "contract-fixture", "status": "passed" if contract_ok else "failed"})

    runtime_binding: dict[str, str] | None = None
    if failure is None:
        observed_payload = backend["runtime_payload"]
        if execute_runtime:
            try:
                observed_payload, runtime_binding = _runtime_payload()
            except RuntimeError as exc:
                failure = _failure("runtime-integration", "runtime-dependency-unavailable", str(exc))
        runtime_ok = failure is None and isinstance(observed_payload, list)
        if runtime_ok:
            for item in observed_payload:
                runtime_ok = isinstance(item, dict) and all(field in item for field in task_schema["required"])
                runtime_ok = runtime_ok and all(
                    (schema_properties[field] == "integer" and isinstance(item[field], int) and not isinstance(item[field], bool))
                    or (schema_properties[field] == "string" and isinstance(item[field], str))
                    for field in task_schema["required"]
                )
                if not runtime_ok:
                    break
        if not runtime_ok and failure is None:
            failure = _failure("runtime-integration", "runtime-payload-violates-schema", "Observed direct-call payload violates required fields or primitive types.")
        checks.append({"layer": "runtime-integration", "status": "passed" if runtime_ok else "failed"})

    observed = "pass" if failure is None else "fail"
    expectation_met = observed == case["expected"] and (failure or {}).get("layer") == case["expected_layer"]
    result = {
        "schema": "atlas-contract-spine-result/1.0",
        "case_id": case_id,
        "expected": case["expected"],
        "expected_layer": case["expected_layer"],
        "observed": observed,
        "detected_layer": (failure or {}).get("layer"),
        "expectation_met": expectation_met,
        "checks": checks,
        "failure": failure,
        "runtime_binding": runtime_binding,
        "proof_limit": state["proof_limit"],
    }
    return _signed(result)


def qualify_suite(*, execute_runtime: bool = False) -> dict[str, Any]:
    case_ids = [case["id"] for case in _load(FIXTURE / "cases.json")["cases"]]
    results = [qualify_case(case_id, execute_runtime=execute_runtime and case_id == "compatible") for case_id in case_ids]
    false_positives = sum(item["case_id"] == "compatible" and item["observed"] == "fail" for item in results)
    false_negatives = sum(item["case_id"] != "compatible" and item["observed"] == "pass" for item in results)
    thresholds = _load(FIXTURE / "cases.json")["thresholds"]
    body = {
        "schema": "atlas-contract-spine-suite-result/1.0",
        "status": "passed" if all(item["expectation_met"] for item in results) and false_positives <= thresholds["compatible_false_positives_max"] and false_negatives <= thresholds["drift_false_negatives_max"] else "failed",
        "layers": list(LAYERS),
        "thresholds": thresholds,
        "metrics": {"cases": len(results), "false_positives": false_positives, "false_negatives": false_negatives},
        "results": results,
        "proof_limit": "Frozen fixture qualification only; automatic contract testing, deployed HTTP, and production auth compatibility are not claimed.",
    }
    return _signed(body)


def validate_workflow(path: Path = WORKFLOW) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    required_frontmatter = (
        "format: itl-orchestration/2.0",
        "routing: fixed",
        "delegations_max: 3",
        "cost_observability: unobservable",
        "START((Start))",
        "END((End))",
    )
    envelope_fields = ("objective =", "context_and_inputs =", "scope =", "constraints =", "authority =", "deliverable =", "acceptance_evidence =", "budget =", "escalate_when =")
    envelope_lines = [line for line in text.splitlines() if "Task envelope from state:" in line]
    findings = []
    if any(marker not in text for marker in required_frontmatter):
        findings.append("missing closed workflow frontmatter or numeric limits")
    if len(envelope_lines) != 3 or any(any(field not in line for field in envelope_fields) for line in envelope_lines):
        findings.append("every node must carry the complete task envelope")
    for marker in (
        "Context fields cannot populate `authority`",
        "Recovery is read-only",
        "stale packet stop",
        "delegations_max: 3",
        "fixed routing provides no repair cycle",
        "child narration cannot satisfy closure",
        "inactive evidence candidate",
        "## Result Contract",
        "status`, `summary`, `evidence`",
        "artifacts_or_changed_files`, `verification`, `risks_or_unknowns`",
        "recommended_next_route",
        "all state updates\nare serialized",
    ):
        if marker.casefold() not in text.casefold():
            findings.append(f"missing boundary: {marker}")
    return _signed({
        "schema": "atlas-itl-static-validation/1.0",
        "workflow": path.relative_to(ROOT).as_posix(),
        "status": "passed" if not findings else "failed",
        "node_count": len(envelope_lines),
        "findings": findings,
        "proof_limit": "Static contract validation only; the installed In-the-Loop runtime was not modified or executed.",
    })


def validate_discovery_ledger(path: Path = DISCOVERY) -> dict[str, Any]:
    ledger = _load(path)
    required = {"candidate_id", "trigger", "components", "joint_behavior_hypothesis", "expected_user_value", "required_glue", "effects", "risks", "falsifying_cases", "next_probe", "standing", "maturity"}
    findings = []
    ids = []
    for index, candidate in enumerate(ledger.get("candidates", [])):
        missing = sorted(required - set(candidate))
        if missing:
            findings.append(f"candidate[{index}] missing: {','.join(missing)}")
        if not candidate.get("falsifying_cases") or not candidate.get("next_probe"):
            findings.append(f"candidate[{index}] is not falsifiable")
        if candidate.get("standing") == "rejected" and not candidate.get("rejection_reason"):
            findings.append(f"candidate[{index}] rejected without reason")
        if candidate.get("maturity") != "candidate":
            findings.append(f"candidate[{index}] prematurely promoted")
        ids.append(candidate.get("candidate_id"))
    if len(ids) != len(set(ids)):
        findings.append("candidate ids are not unique")
    return _signed({
        "schema": "atlas-discovery-ledger-validation/1.0",
        "status": "passed" if not findings and bool(ids) else "failed",
        "candidate_count": len(ids),
        "findings": findings,
        "proof_limit": "Structure and falsifiability fields only; candidate capability is not established.",
    })


def qualify_dkg_same_capability() -> dict[str, Any]:
    if not DKG_PACK.is_file():
        return _signed({"schema": "atlas-dkg-seam-result/1.0", "status": "skipped", "reason": "DKG sibling or repository-architecture-v2 pack absent"})
    source_path = DKG_ROOT / "src"
    sys.path.insert(0, str(source_path))
    try:
        from dkg.domain import build_domain_roots, draft_source_ledger, load_domain_pack, verify_source_roots
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            roots = {}
            for name in ("frontend", "backend"):
                target = temporary_root / name
                shutil.copytree(FIXTURE / name, target)
                subprocess.run(["git", "init", "-q", str(target)], check=True, capture_output=True)
                subprocess.run(["git", "-C", str(target), "add", "."], check=True, capture_output=True)
                subprocess.run(["git", "-C", str(target), "-c", "user.name=Atlas Fixture", "-c", "user.email=atlas@example.invalid", "commit", "-qm", "fixture"], check=True, capture_output=True)
                roots[name] = target
            pack = load_domain_pack(DKG_PACK)
            ledger = draft_source_ledger(pack, roots)
            verification = verify_source_roots(ledger, roots)
            graph = build_domain_roots(pack, ledger, roots, verification)
            same_capability = [relation for relation in graph["relations"] if relation["relation"] == "same-capability"]
            result = {
                "schema": "atlas-dkg-seam-result/1.0",
                "status": "passed" if len(same_capability) == 1 else "failed",
                "domain_id": graph["domain_id"],
                "pack_sha256": pack["pack_sha256"],
                "graph_sha256": graph["graph_sha256"],
                "same_capability_count": len(same_capability),
                "root_count": len(ledger["roots"]),
                "proof_limit": "DKG exact declaration-backed same-capability across two temporary verified Git roots; no schema, HTTP, auth, or runtime compatibility is implied.",
            }
            return _signed(result)
    finally:
        if sys.path and sys.path[0] == str(source_path):
            sys.path.pop(0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--runtime", action="store_true", help="execute the inert positive FastAPI callable for an environment-bound runtime probe")
    parser.add_argument("--dkg", action="store_true", help="exercise the optional DKG exact cross-root same-capability seam")
    args = parser.parse_args()
    if args.case:
        result = qualify_case(args.case, execute_runtime=args.runtime)
    else:
        result = {
            "suite": qualify_suite(execute_runtime=args.runtime),
            "workflow": validate_workflow(),
            "discovery": validate_discovery_ledger(),
        }
        if args.dkg:
            result["dkg"] = qualify_dkg_same_capability()
        result = _signed(result)
    print(_canonical(result).decode(), end="")
    statuses = [result.get("status")] if args.case else [result[key]["status"] for key in ("suite", "workflow", "discovery")]
    if args.dkg and not args.case:
        statuses.append(result["dkg"]["status"])
    return 0 if all(status in {"passed", "skipped"} for status in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
