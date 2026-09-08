#!/usr/bin/env python3
"""Closed, deterministic, read-only Atlas qualification/profile core."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any


class QualificationError(ValueError):
    """A qualification artifact violated its closed contract."""


class InTheLoopUnavailable(QualificationError):
    """The optional exact In-the-Loop 0.4.1 qualification contract is absent."""


STANDINGS = {"observed", "documented", "derived", "proposed", "unknown", "stale", "rejected"}
MATURITIES = {"candidate", "component-qualified", "composition-qualified", "scenario-qualified", "portable", "release-qualified", "deprecated"}
EFFECTS = {"read_repository", "write_source", "network", "provider", "protected_effect"}
INPUT_KINDS = {"context", "intent", "policy", "authority"}
INPUT_SOURCES = {"repository", "task", "policy", "active-session-user-approval"}
GATE_KINDS = {"authority", "evidence", "verification"}
RECEIPT_STATUSES = {"passed", "failed", "stale"}
ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{1,127}")
SHA_RE = re.compile(r"[0-9a-f]{64}")
DKG_REQUIRED_CAPABILITIES = {
    "api-schema-projection", "atlas-five-core", "backend-read-v1", "domain-mining",
    "domain-qualification", "project-atlas-four-file", "query-capabilities-16",
}
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_bytes(value)
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise QualificationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    if path.is_symlink() or not path.is_file():
        raise QualificationError(f"missing or unsafe artifact: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QualificationError(f"invalid JSON artifact: {path}") from exc


def _closed(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        unknown = sorted(set(value) - keys) if isinstance(value, dict) else []
        missing = sorted(keys - set(value)) if isinstance(value, dict) else sorted(keys)
        raise QualificationError(f"{label} keys are not closed; missing={missing}, unknown={unknown}")
    return value


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or ID_RE.fullmatch(value) is None:
        raise QualificationError(f"invalid {label}")
    return value


def _strings(value: Any, label: str, *, nonempty: bool = True) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value) or any(not isinstance(item, str) or not item for item in value):
        raise QualificationError(f"{label} must be a {'non-empty ' if nonempty else ''}string list")
    if len(value) != len(set(value)):
        raise QualificationError(f"duplicate {label}")
    return value


def _enum(value: Any, allowed: set[str], label: str) -> str:
    if value not in allowed:
        raise QualificationError(f"unknown {label}: {value}")
    return value


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise QualificationError(f"invalid {label}")
    return value


def _repository_anchor(value: Any, base: Path) -> Path:
    if not isinstance(value, str) or not value:
        raise QualificationError("source anchor must be a non-empty string")
    logical = value.split("#", 1)[0]
    pure = PurePosixPath(logical)
    if not logical or pure.is_absolute() or "\\" in logical or any(part in {"", ".", ".."} for part in pure.parts):
        raise QualificationError(f"source anchor escapes repository root: {value}")
    candidate = base
    for part in pure.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise QualificationError(f"source anchor is missing or unsafe: {value}")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError as exc:
        raise QualificationError(f"source anchor escapes repository root: {value}") from exc
    if not resolved.is_file():
        raise QualificationError(f"source anchor is missing or unsafe: {value}")
    return resolved


def validate_registry(value: Any, root: Path | None = None) -> dict[str, Any]:
    registry = _closed(value, {"schema", "registry_id", "version", "claims", "promotion_policy", "proof_limit"}, "registry")
    if registry["schema"] != "atlas-capability-registry/1.0":
        raise QualificationError("unsupported registry schema")
    _identifier(registry["registry_id"], "registry id")
    if not isinstance(registry["version"], str) or not registry["version"]:
        raise QualificationError("registry version is required")
    if not isinstance(registry["proof_limit"], str) or not registry["proof_limit"]:
        raise QualificationError("registry proof limit is required")
    policy = _closed(registry["promotion_policy"], {"fresh_receipt_required", "passing_status_required", "independent_verification_required", "authority_from_context_forbidden"}, "promotion policy")
    if set(policy.values()) != {True}:
        raise QualificationError("all closed promotion safeguards must be enabled")
    if not isinstance(registry["claims"], list) or not registry["claims"]:
        raise QualificationError("registry claims are required")
    ids: list[str] = []
    for claim in registry["claims"]:
        claim = _closed(claim, {"id", "kind", "title", "standing", "maturity", "owner", "version", "source_anchors", "effects", "adapters", "incompatible_with", "probe", "negative_cases", "receipt_refs", "proof_limits"}, "claim")
        ids.append(_identifier(claim["id"], "claim id"))
        _enum(claim["kind"], {"primitive", "composition"}, "claim kind")
        _enum(claim["standing"], STANDINGS, "standing")
        _enum(claim["maturity"], MATURITIES, "maturity")
        for key in ("title", "owner", "version", "probe"):
            if not isinstance(claim[key], str) or not claim[key]:
                raise QualificationError(f"claim {key} is required")
        anchors = _strings(claim["source_anchors"], "source anchors")
        for anchor in anchors:
            _repository_anchor(anchor, _root(root))
        effects = _strings(claim["effects"], "effects", nonempty=False)
        for effect in effects:
            _enum(effect, EFFECTS, "effect")
        _strings(claim["adapters"], "adapters", nonempty=False)
        incompatible = _strings(claim["incompatible_with"], "incompatible claims", nonempty=False)
        for item in incompatible:
            _identifier(item, "incompatible claim id")
        _strings(claim["negative_cases"], "negative cases")
        _strings(claim["receipt_refs"], "receipt refs", nonempty=False)
        _strings(claim["proof_limits"], "proof limits")
    if len(ids) != len(set(ids)):
        raise QualificationError("duplicate claim id")
    known = set(ids)
    for claim in registry["claims"]:
        unknown = set(claim["incompatible_with"]) - known
        if unknown:
            raise QualificationError(f"unknown incompatible claim refs: {sorted(unknown)}")
    return registry


def validate_profile(value: Any, registry: dict[str, Any]) -> dict[str, Any]:
    validate_registry(registry)
    profile = _closed(value, {"schema", "id", "intent", "standing", "maturity", "components", "inputs", "execution_order", "outputs", "effects", "gates", "invariants", "tuning", "qualification", "proof_limits", "smallest_manual_test"}, "profile")
    if profile["schema"] != "atlas-profile/1.0":
        raise QualificationError("unsupported profile schema")
    _identifier(profile["id"], "profile id")
    _enum(profile["standing"], STANDINGS, "standing")
    _enum(profile["maturity"], MATURITIES, "maturity")
    for key in ("intent", "smallest_manual_test"):
        if not isinstance(profile[key], str) or not profile[key]:
            raise QualificationError(f"profile {key} is required")
    claims = {item["id"]: item for item in registry["claims"]}
    components = profile["components"]
    if not isinstance(components, list) or not components:
        raise QualificationError("profile components are required")
    component_ids: list[str] = []
    for component in components:
        component = _closed(component, {"id", "owner", "adapter", "required"}, "profile component")
        identifier = _identifier(component["id"], "component id")
        component_ids.append(identifier)
        if identifier not in claims:
            raise QualificationError(f"unknown component: {identifier}")
        if component["owner"] != claims[identifier]["owner"]:
            raise QualificationError(f"ambiguous owner for component: {identifier}")
        if component["adapter"] not in claims[identifier]["adapters"]:
            raise QualificationError(f"unknown adapter for component: {identifier}")
        if not isinstance(component["required"], bool):
            raise QualificationError("component required must be boolean")
    if len(component_ids) != len(set(component_ids)):
        raise QualificationError("duplicate profile component")
    selected = set(component_ids)
    for identifier in selected:
        incompatible = selected & set(claims[identifier]["incompatible_with"])
        if incompatible:
            raise QualificationError(f"incompatible components: {identifier}, {sorted(incompatible)[0]}")
    inputs = profile["inputs"]
    if not isinstance(inputs, list) or not inputs:
        raise QualificationError("profile inputs are required")
    input_kinds: dict[str, str] = {}
    for item in inputs:
        item = _closed(item, {"id", "kind", "required", "source", "description"}, "profile input")
        identifier = _identifier(item["id"], "input id")
        if identifier in input_kinds:
            raise QualificationError("duplicate profile input")
        input_kinds[identifier] = _enum(item["kind"], INPUT_KINDS, "input kind")
        _enum(item["source"], INPUT_SOURCES, "input source")
        if item["kind"] == "authority" and item["source"] != "active-session-user-approval":
            raise QualificationError("context or recovered state cannot populate authority")
        if item["kind"] != "authority" and item["source"] == "active-session-user-approval":
            raise QualificationError("approval source is reserved for authority inputs")
        if not isinstance(item["required"], bool) or not isinstance(item["description"], str) or not item["description"]:
            raise QualificationError("invalid profile input")
    steps = profile["execution_order"]
    if not isinstance(steps, list) or not steps:
        raise QualificationError("execution order is required")
    step_ids: list[str] = []
    produced: set[str] = set(input_kinds)
    for step in steps:
        step = _closed(step, {"id", "module", "requires", "produces"}, "execution step")
        step_ids.append(_identifier(step["id"], "step id"))
        if step["module"] not in selected:
            raise QualificationError(f"unknown step module: {step['module']}")
        required = _strings(step["requires"], "step requires", nonempty=False)
        if not set(required) <= produced:
            raise QualificationError(f"step has unresolved inputs: {step['id']}")
        produced.update(_strings(step["produces"], "step produces"))
    if len(step_ids) != len(set(step_ids)):
        raise QualificationError("duplicate execution step")
    outputs = profile["outputs"]
    if not isinstance(outputs, list) or not outputs:
        raise QualificationError("profile outputs are required")
    output_ids: list[str] = []
    for output in outputs:
        output = _closed(output, {"id", "description"}, "profile output")
        output_ids.append(_identifier(output["id"], "output id"))
        if output["id"] not in produced or not isinstance(output["description"], str) or not output["description"]:
            raise QualificationError(f"unresolved or invalid output: {output['id']}")
    if len(output_ids) != len(set(output_ids)):
        raise QualificationError("duplicate profile output")
    effects = profile["effects"]
    if not isinstance(effects, list) or not effects:
        raise QualificationError("profile effects are required")
    effect_ids: list[str] = []
    gate_ids: set[str] = set()
    gates = profile["gates"]
    if not isinstance(gates, list) or not gates:
        raise QualificationError("profile gates are required")
    for gate in gates:
        gate = _closed(gate, {"id", "kind", "input", "required", "description"}, "profile gate")
        identifier = _identifier(gate["id"], "gate id")
        if identifier in gate_ids:
            raise QualificationError("duplicate profile gate")
        gate_ids.add(identifier)
        kind = _enum(gate["kind"], GATE_KINDS, "gate kind")
        if gate["input"] not in input_kinds or not isinstance(gate["required"], bool) or not isinstance(gate["description"], str) or not gate["description"]:
            raise QualificationError("invalid profile gate")
        if kind == "authority" and input_kinds[gate["input"]] != "authority":
            raise QualificationError("context cannot populate an authority gate")
        if kind != "authority" and input_kinds[gate["input"]] == "authority":
            raise QualificationError("authority input cannot silently satisfy a non-authority gate")
    for effect in effects:
        effect = _closed(effect, {"id", "required", "approval_gate", "description"}, "profile effect")
        effect_ids.append(_enum(effect["id"], EFFECTS, "effect"))
        if not isinstance(effect["required"], bool) or not isinstance(effect["description"], str) or not effect["description"]:
            raise QualificationError("invalid profile effect")
        if effect["id"] != "read_repository" and effect["required"] and effect["approval_gate"] not in gate_ids:
            raise QualificationError(f"required protected effect lacks approval gate: {effect['id']}")
        if effect["approval_gate"] is not None and effect["approval_gate"] not in gate_ids:
            raise QualificationError("unknown effect approval gate")
    if len(effect_ids) != len(set(effect_ids)):
        raise QualificationError("duplicate profile effect")
    _strings(profile["invariants"], "invariants")
    if not isinstance(profile["tuning"], list):
        raise QualificationError("tuning must be a list")
    tuning_ids: list[str] = []
    for item in profile["tuning"]:
        item = _closed(item, {"id", "allowed", "default"}, "tuning field")
        tuning_ids.append(_identifier(item["id"], "tuning id"))
        allowed = _strings(item["allowed"], "tuning values")
        if item["default"] not in allowed:
            raise QualificationError("tuning default is not allowed")
    if len(tuning_ids) != len(set(tuning_ids)):
        raise QualificationError("duplicate tuning field")
    qualification = _closed(profile["qualification"], {"proof_plan", "result_ref", "receipt_refs", "verification_refs"}, "profile qualification")
    if not isinstance(qualification["proof_plan"], str) or not qualification["proof_plan"].startswith("qualification/proof-plans/"):
        raise QualificationError("profile proof plan must be a qualification logical path")
    _strings(qualification["receipt_refs"], "profile receipt refs", nonempty=False)
    _strings(qualification["verification_refs"], "profile verification refs", nonempty=False)
    if not isinstance(qualification["result_ref"], str) or not qualification["result_ref"].startswith("qualification/results/"):
        raise QualificationError("profile result ref must be a qualification logical path")
    if len(qualification["receipt_refs"]) != 1 or not qualification["receipt_refs"][0].startswith("qualification/receipts/"):
        raise QualificationError("profile must declare exactly one candidate receipt ref")
    if len(qualification["verification_refs"]) != 1 or not qualification["verification_refs"][0].startswith("qualification/verifications/"):
        raise QualificationError("profile must declare exactly one verification ref")
    _strings(profile["proof_limits"], "profile proof limits")
    return profile


def validate_proof_plan(value: Any, registry: dict[str, Any]) -> dict[str, Any]:
    validate_registry(registry)
    plan = _closed(value, {"schema", "id", "profile_id", "claim_ids", "hypothesis", "dimensions", "fixtures", "falsifying_cases", "frozen_thresholds", "independent_verification", "proof_limits"}, "proof plan")
    if plan["schema"] != "atlas-proof-plan/1.0":
        raise QualificationError("unsupported proof plan schema")
    _identifier(plan["id"], "proof plan id")
    _identifier(plan["profile_id"], "proof plan profile id")
    known = {claim["id"] for claim in registry["claims"]}
    claim_ids = _strings(plan["claim_ids"], "proof-plan claim ids")
    if not set(claim_ids) <= known:
        raise QualificationError("proof plan references an unknown claim")
    for key in ("hypothesis", "independent_verification"):
        if not isinstance(plan[key], str) or not plan[key]:
            raise QualificationError(f"proof plan {key} is required")
    _strings(plan["dimensions"], "proof dimensions")
    fixtures = _closed(plan["fixtures"], {"positive", "negative", "boundary"}, "proof fixtures")
    for name, values in fixtures.items():
        _strings(values, f"{name} fixtures")
    _strings(plan["falsifying_cases"], "falsifying cases")
    thresholds = plan["frozen_thresholds"]
    if not isinstance(thresholds, dict) or not thresholds or any(not isinstance(key, str) or not key or isinstance(value, bool) or not isinstance(value, (int, float)) for key, value in thresholds.items()):
        raise QualificationError("frozen thresholds must be a non-empty numeric object")
    _strings(plan["proof_limits"], "proof-plan proof limits")
    return plan


def validate_verification_record(value: Any) -> dict[str, Any]:
    record = _closed(value, {"schema", "verification_id", "profile_id", "producer", "producer_sha256", "verifier", "verifier_sha256", "result_ref", "result_sha256", "source_manifest_sha256", "adapter_bindings_sha256", "environment_sha256", "checks", "outcome", "failures", "proof_limit", "verification_sha256"}, "verification record")
    if record["schema"] != "atlas-qualification-verification/1.0":
        raise QualificationError("unsupported verification schema")
    _identifier(record["verification_id"], "verification id")
    _identifier(record["profile_id"], "verification profile id")
    for key in ("producer", "verifier", "result_ref", "proof_limit"):
        if not isinstance(record[key], str) or not record[key]:
            raise QualificationError(f"verification {key} is required")
    for key in ("producer_sha256", "verifier_sha256", "result_sha256", "source_manifest_sha256", "adapter_bindings_sha256", "environment_sha256", "verification_sha256"):
        _sha(record[key], key)
    if record["producer"] == record["verifier"] or record["producer_sha256"] == record["verifier_sha256"]:
        raise QualificationError("producer-only replay is not independent verification")
    _enum(record["outcome"], {"verified-pass", "verified-fail"}, "verification outcome")
    _strings(record["failures"], "verification failures", nonempty=False)
    if not isinstance(record["checks"], list) or not record["checks"]:
        raise QualificationError("verification checks are required")
    check_ids = []
    for check in record["checks"]:
        check = _closed(check, {"id", "status", "detail"}, "verification check")
        check_ids.append(_identifier(check["id"], "verification check id"))
        _enum(check["status"], {"passed", "failed"}, "verification check status")
        if not isinstance(check["detail"], str) or not check["detail"]:
            raise QualificationError("verification check detail is required")
    if len(check_ids) != len(set(check_ids)):
        raise QualificationError("duplicate verification check")
    unsigned = dict(record)
    observed = unsigned.pop("verification_sha256")
    if digest(unsigned) != observed:
        raise QualificationError("verification_sha256 mismatch")
    return record


def validate_receipt(value: Any, *, registry_sha256: str | None = None, profile_sha256: str | None = None) -> dict[str, Any]:
    receipt = _closed(value, {"schema", "receipt_id", "claim_ids", "profile_id", "registry_sha256", "profile_sha256", "proof_plan_sha256", "frozen_thresholds", "results", "status", "freshness", "failures", "independent_verification", "bindings", "proof_limit", "receipt_sha256"}, "receipt")
    if receipt["schema"] != "atlas-qualification-receipt/2.0":
        raise QualificationError("unsupported receipt schema")
    _identifier(receipt["receipt_id"], "receipt id")
    _identifier(receipt["profile_id"], "receipt profile id")
    _strings(receipt["claim_ids"], "receipt claim ids")
    for key in ("registry_sha256", "profile_sha256", "proof_plan_sha256", "receipt_sha256"):
        _sha(receipt[key], key)
    if registry_sha256 is not None and receipt["registry_sha256"] != registry_sha256:
        raise QualificationError("receipt registry digest is stale")
    if profile_sha256 is not None and receipt["profile_sha256"] != profile_sha256:
        raise QualificationError("receipt profile digest is stale")
    if not isinstance(receipt["frozen_thresholds"], dict) or not receipt["frozen_thresholds"]:
        raise QualificationError("receipt frozen thresholds are required")
    if not isinstance(receipt["results"], dict) or set(receipt["results"]) != set(receipt["frozen_thresholds"]):
        raise QualificationError("receipt results must exactly match frozen thresholds")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in [*receipt["frozen_thresholds"].values(), *receipt["results"].values()]):
        raise QualificationError("receipt thresholds and results must be numeric")
    _enum(receipt["status"], RECEIPT_STATUSES, "receipt status")
    _enum(receipt["freshness"], {"current", "stale"}, "receipt freshness")
    _strings(receipt["failures"], "receipt failures", nonempty=False)
    if not isinstance(receipt["independent_verification"], bool) or not isinstance(receipt["proof_limit"], str) or not receipt["proof_limit"]:
        raise QualificationError("invalid receipt verification metadata")
    bindings = _closed(receipt["bindings"], {"result", "source_manifest", "adapter_bindings", "environment", "verification"}, "receipt bindings")
    result = _closed(bindings["result"], {"ref", "sha256"}, "result binding")
    verification = _closed(bindings["verification"], {"ref", "sha256"}, "verification binding")
    for item, label in ((result, "result"), (verification, "verification")):
        if not isinstance(item["ref"], str) or not item["ref"].startswith("qualification/"):
            raise QualificationError(f"invalid {label} ref")
        _sha(item["sha256"], f"{label} sha256")
    manifest = _closed(bindings["source_manifest"], {"files", "sha256"}, "source manifest")
    if not isinstance(manifest["files"], list) or not manifest["files"]:
        raise QualificationError("source manifest files are required")
    paths = []
    for item in manifest["files"]:
        item = _closed(item, {"path", "sha256"}, "source manifest file")
        if not isinstance(item["path"], str) or not item["path"]:
            raise QualificationError("source manifest path is required")
        paths.append(item["path"])
        _sha(item["sha256"], "source file sha256")
    if paths != sorted(set(paths)) or digest(manifest["files"]) != _sha(manifest["sha256"], "source manifest sha256"):
        raise QualificationError("source manifest is not canonical or digest-bound")
    adapters = _closed(bindings["adapter_bindings"], {"items", "sha256"}, "adapter bindings")
    if not isinstance(adapters["items"], list) or not adapters["items"] or digest(adapters["items"]) != _sha(adapters["sha256"], "adapter bindings sha256"):
        raise QualificationError("adapter bindings are missing or digest-mismatched")
    environment = _closed(bindings["environment"], {"boundary", "sha256"}, "environment binding")
    if not isinstance(environment["boundary"], dict) or digest(environment["boundary"]) != _sha(environment["sha256"], "environment sha256"):
        raise QualificationError("environment binding digest mismatch")
    unsigned = dict(receipt)
    observed = unsigned.pop("receipt_sha256")
    if digest(unsigned) != observed:
        raise QualificationError("receipt_sha256 mismatch")
    return receipt


def receipt_can_promote(receipt: dict[str, Any], *, registry_sha256: str, profile_sha256: str, verification_record: dict[str, Any] | None = None, expected_bindings: dict[str, Any] | None = None) -> bool:
    validate_receipt(receipt, registry_sha256=registry_sha256, profile_sha256=profile_sha256)
    def met(key: str, threshold: float) -> bool:
        observed = receipt["results"][key]
        if key.endswith("_max"):
            return observed <= threshold
        if key.endswith("_min"):
            return observed >= threshold
        raise QualificationError(f"threshold direction must end in _min or _max: {key}")

    thresholds_met = all(met(key, value) for key, value in receipt["frozen_thresholds"].items())
    if verification_record is None:
        return False
    verification = validate_verification_record(verification_record)
    bindings = receipt["bindings"]
    verification_matches = (
        bindings["verification"]["sha256"] == verification["verification_sha256"]
        and verification["profile_id"] == receipt["profile_id"]
        and verification["result_ref"] == bindings["result"]["ref"]
        and verification["result_sha256"] == bindings["result"]["sha256"]
        and verification["source_manifest_sha256"] == bindings["source_manifest"]["sha256"]
        and verification["adapter_bindings_sha256"] == bindings["adapter_bindings"]["sha256"]
        and verification["environment_sha256"] == bindings["environment"]["sha256"]
        and verification["outcome"] == "verified-pass"
        and not verification["failures"]
    )
    bindings_current = expected_bindings is None or all(bindings[key] == expected_bindings[key] for key in ("result", "source_manifest", "adapter_bindings", "environment"))
    return receipt["status"] == "passed" and receipt["freshness"] == "current" and not receipt["failures"] and receipt["independent_verification"] and thresholds_met and verification_matches and bindings_current


def _root(root: Path | None) -> Path:
    return root.resolve() if root else Path(__file__).resolve().parents[1]


def _artifacts(root: Path | None) -> tuple[Path, dict[str, Any]]:
    base = _root(root)
    registry = validate_registry(load_json(base / "qualification" / "capability-registry.json"), base)
    return base, registry


def list_profiles(root: Path | None = None) -> dict[str, Any]:
    base, registry = _artifacts(root)
    profiles = []
    for path in sorted((base / "qualification" / "profiles").glob("*.atlas-profile.json")):
        profile = validate_profile(load_json(path), registry)
        profiles.append({key: profile[key] for key in ("id", "intent", "standing", "maturity")})
    return {"schema": "atlas-profile-list/1.0", "profiles": profiles, "operation": "read-only", "proof_limit": "Discovery only; listing does not execute a profile or grant authority."}


def describe_profile(profile_id: str, root: Path | None = None) -> dict[str, Any]:
    base, registry = _artifacts(root)
    path = base / "qualification" / "profiles" / f"{_identifier(profile_id, 'profile id')}.atlas-profile.json"
    profile = validate_profile(load_json(path), registry)
    claims = {item["id"]: item for item in registry["claims"]}
    components = [{**item, "version": claims[item["id"]]["version"], "standing": claims[item["id"]]["standing"], "maturity": claims[item["id"]]["maturity"]} for item in profile["components"]]
    available_receipt_refs = [ref for ref in profile["qualification"]["receipt_refs"] if (base / ref).is_file() and not (base / ref).is_symlink()]
    return {"schema": "atlas-profile-description/1.0", "operation": "read-only", "registry_sha256": digest(registry), "profile_sha256": digest(profile), "available_receipt_refs": available_receipt_refs, "profile": {**profile, "components": components}}


def _file_binding(path: Path, base: Path) -> dict[str, str]:
    if path.is_symlink() or not path.is_file():
        raise QualificationError(f"binding source is missing or unsafe: {path}")
    try:
        logical = path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError as exc:
        raise QualificationError(f"repository binding escapes root: {path}") from exc
    return {"path": logical, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _dependency_binding(path: Path, logical: str) -> dict[str, str]:
    if path.is_symlink() or not path.is_file():
        raise QualificationError(f"dependency binding is missing or unsafe: {logical}")
    return {"path": logical, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def dkg_root(base: Path) -> Path:
    configured = os.environ.get("DKG_FRAMEWORK_ROOT")
    return Path(configured).expanduser().resolve() if configured else (base.parent / "deterministic-kg-rag-framework").resolve()


def validate_dkg_identity(base: Path) -> dict[str, Any]:
    root = dkg_root(base)
    metadata_path = root / "pyproject.toml"
    interface_path = root / "config" / "framework-interface.json"
    cli_path = root / "src" / "dkg" / "cli.py"
    try:
        with metadata_path.open("rb") as handle:
            project = tomllib.load(handle)["project"]
        interface = load_json(interface_path)
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        raise QualificationError("paired DKG identity is missing or unparseable") from exc
    name, version, python_requires = project.get("name"), project.get("version"), project.get("requires-python")
    matched = VERSION_RE.fullmatch(version) if isinstance(version, str) else None
    expected_keys = {"schema", "distribution", "framework_version", "cli_contract", "python_requires", "capabilities", "proof_limit"}
    compatible = (
        name == "deterministic-kg-rag-framework" and matched is not None
        and (0, 3, 0) <= tuple(int(part) for part in matched.groups()) < (0, 4, 0)
        and python_requires == ">=3.11" and sys.version_info >= (3, 11)
        and isinstance(interface, dict) and set(interface) == expected_keys
        and interface["schema"] == "dkg-framework-interface/1.0"
        and interface["distribution"] == name and interface["framework_version"] == version
        and interface["cli_contract"] == "dkg-cli/1.0" and interface["python_requires"] == python_requires
        and isinstance(interface["capabilities"], list)
        and interface["capabilities"] == sorted(set(interface["capabilities"]))
        and all(isinstance(item, str) and item for item in interface["capabilities"])
        and not (DKG_REQUIRED_CAPABILITIES - set(interface["capabilities"]))
        and cli_path.is_file() and not cli_path.is_symlink()
    )
    if not compatible:
        raise QualificationError("paired DKG contract does not match the complete bridge contract")
    return {
        "schema": interface["schema"], "distribution": name, "framework_version": version,
        "cli_contract": interface["cli_contract"], "python_requires": python_requires,
        "capabilities": interface["capabilities"],
        "identity_files": [
            _dependency_binding(interface_path, f"dependency/deterministic-kg-rag-framework/{version}/config/framework-interface.json"),
            _dependency_binding(metadata_path, f"dependency/deterministic-kg-rag-framework/{version}/pyproject.toml"),
            _dependency_binding(cli_path, f"dependency/deterministic-kg-rag-framework/{version}/src/dkg/cli.py"),
        ],
    }


def _source_path(anchor: str, base: Path) -> Path:
    return _repository_anchor(anchor, base)


ITL_LOGICAL_PATHS = {
    "roster": "dependency/in-the-loop/0.4.1/bindings/codex/roster.json",
    "linter": "dependency/in-the-loop/0.4.1/scripts/lint_itl.py",
    "locker": "dependency/in-the-loop/0.4.1/scripts/workflow_lock.py",
    "core": "dependency/in-the-loop/0.4.1/spec/core-contract.md",
    "orchestration": "dependency/in-the-loop/0.4.1/spec/orchestration-format.md",
}


def _itl_contract_paths(base: Path) -> dict[str, Path]:
    """Resolve the authoritative exact ITL checkout or installed plugin bundle."""
    source = base.parents[2] / "in-the-loop-codex"
    candidates = (
        {
            "roster": source / "bindings" / "codex" / "roster.json",
            "linter": source / "scripts" / "lint_itl.py",
            "locker": source / "scripts" / "workflow_lock.py",
            "core": source / "spec" / "core-contract.md",
            "orchestration": source / "spec" / "orchestration-format.md",
        },
        {
            "roster": base.parents[2] / "in-the-loop-local" / "in-the-loop" / "0.4.1" / "skills" / "kg-rag-specialist" / "references" / "binding" / "roster.json",
            "linter": base.parents[2] / "in-the-loop-local" / "in-the-loop" / "0.4.1" / "skills" / "run-itl-workflow" / "scripts" / "lint_itl.py",
            "locker": base.parents[2] / "in-the-loop-local" / "in-the-loop" / "0.4.1" / "skills" / "run-itl-workflow" / "scripts" / "workflow_lock.py",
            "core": base.parents[2] / "in-the-loop-local" / "in-the-loop" / "0.4.1" / "skills" / "in-the-loop" / "references" / "spec" / "core-contract.md",
            "orchestration": base.parents[2] / "in-the-loop-local" / "in-the-loop" / "0.4.1" / "skills" / "in-the-loop" / "references" / "spec" / "orchestration-format.md",
        },
    )
    for paths in candidates:
        safe = [path.is_file() and not path.is_symlink() for path in paths.values()]
        if all(safe):
            return paths
        if any(path.exists() or path.is_symlink() for path in paths.values()):
            raise QualificationError("authoritative In-the-Loop 0.4.1 contract is incomplete or unsafe")
    raise InTheLoopUnavailable("itl-qualification-contract-unavailable")


def _itl_identity_bindings(paths: dict[str, Path]) -> list[dict[str, str]]:
    return [_dependency_binding(paths[key], ITL_LOGICAL_PATHS[key]) for key in sorted(paths)]


def build_current_bindings(profile_id: str, profile: dict[str, Any], registry: dict[str, Any], base: Path, result: dict[str, Any] | None = None) -> dict[str, Any]:
    result_ref = profile["qualification"]["result_ref"]
    observed_result = result if result is not None else load_json(base / result_ref)
    if not isinstance(observed_result, dict) or observed_result.get("result_sha256") != digest({key: value for key, value in observed_result.items() if key != "result_sha256"}):
        raise QualificationError("stored qualification result digest mismatch")
    common = [
        base / "scripts" / "qualification_core.py", base / "scripts" / "qualification_receipts.py",
        base / "scripts" / "qualification_verifier.py", base / "qualification" / "profiles" / f"{profile_id}.atlas-profile.json",
        base / profile["qualification"]["proof_plan"],
    ]
    itl: dict[str, Path] | None = None
    external_source_files: list[dict[str, str]] = []
    if profile_id == "fullstack-contract-spine":
        sources = common + [base / "scripts" / "qualification_scenarios.py"] + sorted((base / "qualification" / "fixtures" / "fullstack-contract-spine").rglob("*"))
    elif profile_id == "rag-evidence-firewall":
        sources = common + [base / "qualification" / "fixtures" / "fullstack-contract-spine" / "contract.json", base / "release-docs" / "architecture.md"]
    else:
        ai_root = base / "qualification" / "ai-control-plane"
        try:
            itl = _itl_contract_paths(base)
        except InTheLoopUnavailable:
            itl = None
        sources = common + [
            base / "scripts" / "qualification_ai_control_plane.py",
            *sorted(path for path in ai_root.rglob("*") if path.is_file()),
        ]
        if itl is not None:
            external_source_files = _itl_identity_bindings(itl)
    files = sorted(
        [_file_binding(path, base) for path in sources if path.is_file()] + external_source_files,
        key=lambda item: item["path"],
    )
    source_manifest = {"files": files, "sha256": digest(files)}
    claims = {item["id"]: item for item in registry["claims"]}
    dkg_identity: dict[str, Any] | None = None
    adapter_items = []
    for component in profile["components"]:
        claim = claims[component["id"]]
        identity_files = sorted((_file_binding(_source_path(anchor, base), base) for anchor in claim["source_anchors"]), key=lambda item: item["path"])
        contract: dict[str, Any] = {"schema": component["adapter"], "owner": claim["owner"], "version": claim["version"]}
        if component["adapter"].startswith("itl-") or component["adapter"] == "atlas-itl-grounding/1.0":
            if itl is None:
                try:
                    itl = _itl_contract_paths(base)
                except InTheLoopUnavailable:
                    itl = None
            if itl is not None:
                identity_files = sorted(identity_files + _itl_identity_bindings(itl), key=lambda item: item["path"])
            contract = {
                **contract,
                "qualification_contract": "dependency/in-the-loop/0.4.1",
                "qualification_contract_available": itl is not None,
                "authoritative_linter": ITL_LOGICAL_PATHS["linter"],
                "authoritative_locker": ITL_LOGICAL_PATHS["locker"],
                "production_roster": ITL_LOGICAL_PATHS["roster"],
                "workflow_contract": ITL_LOGICAL_PATHS["orchestration"],
            }
        if component["adapter"].startswith("dkg-") or component["adapter"] == "atlas-contract-spine/1.0":
            dkg_identity = dkg_identity or validate_dkg_identity(base)
            contract = dkg_identity
        adapter_items.append({"component_id": component["id"], "adapter": component["adapter"], "required": component["required"], "contract": contract, "source_files": identity_files})
    adapter_bindings = {"items": adapter_items, "sha256": digest(adapter_items)}
    dependencies: dict[str, str] = {}
    if profile_id == "fullstack-contract-spine":
        for distribution in ("fastapi", "httpx", "pydantic"):
            try:
                dependencies[distribution] = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError as exc:
                raise QualificationError(f"required qualification dependency unavailable: {distribution}") from exc
    boundary = {
        "schema": "atlas-qualification-environment/1.0",
        "python": {"implementation": platform.python_implementation(), "version": platform.python_version()},
        "platform": {"system": platform.system(), "machine": platform.machine()},
        "dependency_identities": {
            "suite": "atlas-suite-plugin/1.1.0",
            "dkg": f"deterministic-kg-rag-framework/{dkg_identity['framework_version']}" if dkg_identity is not None else None,
            "in_the_loop": "in-the-loop/0.4.1" if itl is not None else None,
        },
        "dependencies": dependencies,
    }
    environment = {"boundary": boundary, "sha256": digest(boundary)}
    return {"result": {"ref": result_ref, "sha256": observed_result["result_sha256"]}, "source_manifest": source_manifest, "adapter_bindings": adapter_bindings, "environment": environment}


def _adapter_checks(profile: dict[str, Any], root: Path | None = None) -> list[dict[str, Any]]:
    base = _root(root)
    try:
        validate_dkg_identity(base)
        dkg_ready = True
    except QualificationError:
        dkg_ready = False
    try:
        _itl_contract_paths(base)
        itl_ready = True
    except InTheLoopUnavailable:
        itl_ready = False
    checks = []
    for component in profile["components"]:
        adapter = component["adapter"]
        if adapter.startswith("dkg-") or adapter == "atlas-contract-spine/1.0":
            ready, reason = dkg_ready, "paired-dkg-contract-ready" if dkg_ready else "paired-dkg-contract-unavailable"
        elif adapter.startswith("itl-") or adapter == "atlas-itl-grounding/1.0":
            ready, reason = itl_ready, "exact-itl-0.4.1-contract-ready" if itl_ready else "itl-qualification-contract-unavailable"
        elif adapter == "atlas-profile/1.0":
            ready, reason = True, "local-profile-contract-ready"
        elif adapter == "atlas-context-packet/1.0":
            ready, reason = True, "declared-context-contract-ready"
        elif adapter in {"codex-native/1.0", "codex-task-result/1.0"}:
            ready, reason = True, "host-contract-declared-execution-not-authorized"
        elif adapter == "atlas-projection-set/1.0":
            ready, reason = True, "declared-projection-contract-ready"
        else:
            ready, reason = False, "unrecognized-adapter"
        checks.append({"component_id": component["id"], "adapter": adapter, "required": component["required"], "ready": ready, "reason": reason})
    return checks


def plan_profile(profile_id: str, root: Path | None = None) -> dict[str, Any]:
    description = describe_profile(profile_id, root)
    profile = description["profile"]
    adapter_checks = _adapter_checks(profile, root)
    ready = all(item["ready"] or not item["required"] for item in adapter_checks)
    return {"schema": "atlas-profile-plan/1.0", "operation": "read-only", "profile_id": profile_id, "status": "ready" if ready else "blocked", "adapter_checks": adapter_checks, "execution_order": profile["execution_order"], "effects": profile["effects"], "gates": profile["gates"], "outputs": profile["outputs"], "proof_limits": profile["proof_limits"], "execution_authorized": False}


def explain_profile(profile_id: str, root: Path | None = None) -> dict[str, Any]:
    description = describe_profile(profile_id, root)
    profile = description["profile"]
    return {
        "schema": "atlas-profile-explanation/1.0",
        "operation": "read-only",
        "profile_id": profile_id,
        "intent": profile["intent"],
        "composition": [
            {
                "id": item["id"],
                "owner": item["owner"],
                "adapter": item["adapter"],
                "required": item["required"],
            }
            for item in profile["components"]
        ],
        "invariants": profile["invariants"],
        "tuning": profile["tuning"],
        "smallest_manual_test": profile["smallest_manual_test"],
        "proof_limits": profile["proof_limits"],
        "execution_authorized": False,
    }


def profile_qualification(profile_id: str, root: Path | None = None) -> dict[str, Any]:
    base, registry = _artifacts(root)
    profile = validate_profile(load_json(base / "qualification" / "profiles" / f"{_identifier(profile_id, 'profile id')}.atlas-profile.json"), registry)
    plan = validate_proof_plan(load_json(base / profile["qualification"]["proof_plan"]), registry)
    if plan["profile_id"] != profile_id:
        raise QualificationError("profile proof plan id mismatch")
    receipt_ref = profile["qualification"]["receipt_refs"][0]
    verification_ref = profile["qualification"]["verification_refs"][0]
    result_ref = profile["qualification"]["result_ref"]
    receipt_path = base / receipt_ref
    receipts = []
    promotion_eligible = False
    status = "absent"
    if receipt_path.is_file() and not receipt_path.is_symlink():
        receipt = None
        errors = []
        try:
            receipt = validate_receipt(load_json(receipt_path), registry_sha256=digest(registry), profile_sha256=digest(profile))
            if receipt["profile_id"] != profile_id or receipt["claim_ids"] != plan["claim_ids"] or receipt["proof_plan_sha256"] != digest(plan):
                raise QualificationError("candidate receipt is not bound to the current profile proof plan")
            if receipt["bindings"]["result"]["ref"] != result_ref or receipt["bindings"]["verification"]["ref"] != verification_ref:
                raise QualificationError("candidate receipt does not use the profile-declared result and verification refs")
            verification = validate_verification_record(load_json(base / verification_ref))
            current_bindings = build_current_bindings(profile_id, profile, registry, base)
            for binding_name in ("result", "source_manifest", "adapter_bindings", "environment"):
                if receipt["bindings"][binding_name] != current_bindings[binding_name]:
                    raise QualificationError(f"{binding_name} binding drift")
            promotion_eligible = receipt_can_promote(
                receipt, registry_sha256=digest(registry), profile_sha256=digest(profile),
                verification_record=verification, expected_bindings=current_bindings,
            )
            status = "current"
        except QualificationError as exc:
            errors.append(str(exc))
            status = "stale"
            promotion_eligible = False
        receipts.append({"ref": receipt_ref, "receipt": receipt, "verification_ref": verification_ref, "observed_freshness": status, "validation_errors": errors, "promotion_eligible": promotion_eligible})
    return {
        "schema": "atlas-profile-qualification/1.0",
        "operation": "read-only",
        "profile_id": profile_id,
        "proof_plan": plan,
        "receipt_refs": [item["ref"] for item in receipts],
        "receipts": receipts,
        "status": status,
        "promotion_eligible": promotion_eligible,
        "proof_limit": "Promotion eligibility is a digest-bound policy result, not automatic registry promotion or execution authority.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atlas profile",
        description="Inspect transparent Atlas composition profiles without executing them.",
    )
    commands = parser.add_subparsers(dest="profile_command", required=True)
    commands.add_parser("list", help="list registered candidate profiles")
    for name in ("describe", "explain", "plan", "qualification"):
        item = commands.add_parser(name)
        item.add_argument("profile_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.profile_command == "list":
            result = list_profiles()
        elif args.profile_command == "describe":
            result = describe_profile(args.profile_id)
        elif args.profile_command == "explain":
            result = explain_profile(args.profile_id)
        elif args.profile_command == "plan":
            result = plan_profile(args.profile_id)
        else:
            result = profile_qualification(args.profile_id)
    except QualificationError as exc:
        print(f"atlas-suite: {exc}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
