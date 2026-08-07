#!/usr/bin/env python3
"""Provider-neutral, deterministic KG-RAG contracts and Harness Boot."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from scripts import build_kg_rag_assets as assets
except ModuleNotFoundError:
    import build_kg_rag_assets as assets  # type: ignore[no-redef]


_CANDIDATE_ROOT = Path(__file__).resolve().parent.parent
ROOT = _CANDIDATE_ROOT / "references/kg-rag/workspace" if (_CANDIDATE_ROOT / "references/kg-rag/workspace/kg-rag").is_dir() else _CANDIDATE_ROOT
SCHEMAS = ROOT / "schemas/kg-rag"
CONTRACT_NAMES = (
    "ngf-document",
    "kg-rag-source-ledger",
    "kg-rag-framework-manifest",
    "kg-rag-recipe-registry",
    "kg-rag-blueprint",
    "kg-rag-qualification",
    "kg-rag-harness-boot-receipt",
)
SCHEMA_FILES = {f"{name}/1.0": SCHEMAS / f"{name}.schema.json" for name in CONTRACT_NAMES}
SHA256_RE = re.compile(r"[0-9a-f]{64}")
FORBIDDEN_RECEIPT_FRAGMENTS = ("secret", "credential", "password", "private_content", "approval", "authority")


class ContractError(ValueError):
    """A fail-closed contract violation."""


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json_bytes(data: bytes, label: str, *, canonical_required: bool = False) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ContractError(f"{label} contains non-finite number {value}")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} is not strict UTF-8 JSON: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object")
    if canonical_required and data != canonical(value):
        raise ContractError(f"{label} is not canonical JSON")
    return value


def safe_relative(value: str, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ContractError(f"{label} must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ContractError(f"{label} must be a contained relative path")
    return path


def contained(base: Path, relative: str, label: str, *, must_exist: bool = True) -> Path:
    rel = safe_relative(relative, label)
    candidate = base.joinpath(*rel.parts)
    current = base
    for part in rel.parts:
        current /= part
        if current.is_symlink():
            raise ContractError(f"{label} must not traverse a symlink")
    try:
        candidate.absolute().relative_to(base.absolute())
    except ValueError as error:
        raise ContractError(f"{label} escapes its root") from error
    if must_exist and (not candidate.is_file() or candidate.is_symlink()):
        raise ContractError(f"{label} must name an existing regular non-symlink file")
    return candidate


def safe_existing_file(path: Path, root: Path, label: str) -> Path:
    try:
        relative = path.absolute().relative_to(root.absolute()).as_posix()
    except ValueError as error:
        raise ContractError(f"{label} escapes repository root") from error
    return contained(root, relative, label)


def read_json(path: Path, *, canonical_required: bool = True, root: Path | None = None) -> dict[str, Any]:
    safe = safe_existing_file(path, root or ROOT, str(path))
    return strict_json_bytes(safe.read_bytes(), str(path), canonical_required=canonical_required)


def exact(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    missing, extra = fields - value.keys(), value.keys() - fields
    if missing:
        raise ContractError(f"{label} missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ContractError(f"{label} has undeclared fields: {', '.join(sorted(extra))}")
    return value


def string(value: Any, label: str, allowed: set[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{label} must be a non-empty string")
    if allowed is not None and value not in allowed:
        raise ContractError(f"{label} has unsupported value {value!r}")
    return value


def boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"{label} must be boolean")
    return value


def integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ContractError(f"{label} must be an integer >= {minimum}")
    return value


def number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{label} must be a finite number")
    return float(value)


def string_list(value: Any, label: str, *, ordered: list[str] | None = None) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ContractError(f"{label} must be a non-empty string array")
    if len(set(value)) != len(value):
        raise ContractError(f"{label} contains duplicates")
    if ordered is not None and value != ordered:
        raise ContractError(f"{label} must match the canonical ordered inventory")
    return value


def digest_ref(value: Any, label: str, repo_root: Path) -> None:
    ref = exact(value, {"path", "bytes", "sha256", "version"}, label)
    path = contained(repo_root, string(ref["path"], f"{label}.path"), f"{label}.path")
    integer(ref["bytes"], f"{label}.bytes")
    if not SHA256_RE.fullmatch(string(ref["sha256"], f"{label}.sha256")):
        raise ContractError(f"{label}.sha256 must be lowercase SHA-256")
    string(ref["version"], f"{label}.version", {assets.COOKBOOK_VERSION})
    data = path.read_bytes()
    if len(data) != ref["bytes"] or sha256(data) != ref["sha256"]:
        raise ContractError(f"{label} artifact integrity mismatch")


SOURCE_FIELDS = {
    "id", "title", "locator", "locator_type", "publisher", "version_or_date",
    "accessed", "authority_class", "license_status", "usage_status",
    "consent_status", "retention_policy", "deletion_policy", "freshness",
    "digest_status", "sha256", "provenance_is_integrity", "vendored_body",
}


def _validate_source_entries(
    sources: Any,
    *,
    repo_root: Path,
    minimum: int,
    minimum_message: str,
) -> set[str]:
    if not isinstance(sources, list) or len(sources) < minimum:
        raise ContractError(minimum_message)
    ids: list[str] = []
    for index, raw in enumerate(sources):
        item = exact(raw, SOURCE_FIELDS, f"sources[{index}]")
        ids.append(string(item["id"], "source id"))
        for key in SOURCE_FIELDS - {"sha256", "provenance_is_integrity", "vendored_body"}:
            string(item[key], f"source {item['id']} {key}")
        if item["license_status"] in {"unknown", "unlicensed", "denied"}:
            raise ContractError(f"source {item['id']} is not licensed for declared use")
        if item["usage_status"] in {"unknown", "unauthorized", "denied"} or item["consent_status"] != "authorized":
            raise ContractError(f"source {item['id']} is not authorized for declared use")
        if boolean(item["vendored_body"], "vendored_body"):
            raise ContractError("external source bodies must not be vendored")
        if boolean(item["provenance_is_integrity"], "provenance_is_integrity"):
            raise ContractError("provenance and artifact integrity must not be conflated")
        if item["locator_type"] == "repository-relative":
            source_path = contained(repo_root, item["locator"], "source locator")
            if item["digest_status"] != "stable" or not isinstance(item["sha256"], str) or not SHA256_RE.fullmatch(item["sha256"]):
                raise ContractError("stable local source requires a SHA-256 digest")
            if sha256(source_path.read_bytes()) != item["sha256"]:
                raise ContractError("local grounding source digest mismatch")
        elif item["locator_type"] == "https":
            if not item["locator"].startswith("https://") or item["sha256"] is not None:
                raise ContractError("external locator must be HTTPS and omit an unobserved body digest")
        else:
            raise ContractError("unsupported source locator type")
    if len(ids) != len(set(ids)):
        raise ContractError("source IDs must be unique")
    return set(ids)


def validate_ngf_source_ledger(value: dict[str, Any], *, repo_root: Path = ROOT) -> None:
    """Validate the provider-neutral NGF ledger without KG-RAG requirements."""
    exact(value, {"schema", "sources"}, "source ledger")
    string(value["schema"], "schema", {"ngf-source-ledger/1.0"})
    _validate_source_entries(
        value["sources"],
        repo_root=repo_root,
        minimum=1,
        minimum_message="source ledger must contain at least one source",
    )


def validate_source_ledger(value: dict[str, Any], *, repo_root: Path = ROOT) -> None:
    exact(value, {"schema", "cookbook_version", "sources"}, "source ledger")
    string(value["schema"], "schema", {"kg-rag-source-ledger/1.0"})
    string(value["cookbook_version"], "cookbook_version", {assets.COOKBOOK_VERSION})
    ids = _validate_source_entries(
        value["sources"],
        repo_root=repo_root,
        minimum=9,
        minimum_message="source ledger must contain at least the nine declared grounding sources",
    )
    required_ids = {item["id"] for item in assets.source_ledger()["sources"]}
    if not required_ids.issubset(ids):
        raise ContractError("source ledger is missing a required grounding source")


def validate_manifest(value: dict[str, Any], *, repo_root: Path = ROOT) -> None:
    exact(value, {"schema", "framework_id", "cookbook_version", "integrity_notice", "capabilities", "profiles", "artifacts"}, "framework manifest")
    string(value["schema"], "schema", {"kg-rag-framework-manifest/1.0"})
    string(value["framework_id"], "framework_id")
    string(value["cookbook_version"], "cookbook_version", {assets.COOKBOOK_VERSION})
    if "not provenance" not in string(value["integrity_notice"], "integrity_notice"):
        raise ContractError("integrity notice must distinguish digests from provenance")
    capabilities = string_list(value["capabilities"], "capabilities", ordered=assets.CAPABILITIES)
    if not isinstance(value["profiles"], list) or len(value["profiles"]) != 3:
        raise ContractError("manifest must declare exactly three profiles")
    expected_profiles = ["local-deterministic", "production-adapter", "call-e"]
    expected_profile_values = {
        "local-deterministic": ("blueprint", ["local-hybrid"]),
        "production-adapter": ("abstract", ["production-hybrid"]),
        "call-e": ("blocked", ["call-e"]),
    }
    observed_profiles: list[str] = []
    for raw in value["profiles"]:
        profile = exact(raw, {"name", "maturity", "network_policy", "allowed_routes", "capabilities", "required_adapters"}, "profile")
        observed_profiles.append(string(profile["name"], "profile.name", set(expected_profiles)))
        maturity = string(profile["maturity"], "profile.maturity", {"blueprint", "abstract", "blocked"})
        string(profile["network_policy"], "profile.network_policy", {"forbidden"})
        routes = string_list(profile["allowed_routes"], "profile.allowed_routes")
        expected_maturity, expected_routes = expected_profile_values[profile["name"]]
        if maturity != expected_maturity or routes != expected_routes:
            raise ContractError("profile maturity or route inventory is invalid")
        if string_list(profile["capabilities"], "profile.capabilities") != capabilities:
            raise ContractError("profile capability inventory must match manifest")
        string_list(profile["required_adapters"], "profile.required_adapters", ordered=assets.ADAPTER_KINDS)
    if observed_profiles != expected_profiles:
        raise ContractError("profile order or inventory is invalid")
    if not isinstance(value["artifacts"], list) or not value["artifacts"]:
        raise ContractError("artifact inventory must be non-empty")
    paths: list[str] = []
    for raw in value["artifacts"]:
        digest_ref(raw, "manifest artifact", repo_root)
        paths.append(raw["path"])
    if len(paths) != len(set(paths)):
        raise ContractError("artifact paths must be unique")


def validate_registry(value: dict[str, Any]) -> None:
    exact(value, {"schema", "cookbook_version", "recipes"}, "recipe registry")
    string(value["schema"], "schema", {"kg-rag-recipe-registry/1.0"})
    string(value["cookbook_version"], "cookbook_version", {assets.COOKBOOK_VERSION})
    if not isinstance(value["recipes"], list) or len(value["recipes"]) != len(assets.RECIPE_IDS):
        raise ContractError("recipe registry must contain exactly eighteen recipes")
    observed: list[str] = []
    for index, raw in enumerate(value["recipes"], 1):
        item = exact(raw, {"order", "id", "inputs", "outputs", "required_capabilities", "failure_behavior", "provenance_obligations", "evaluation_dimensions", "compatible_profiles"}, f"recipe[{index}]")
        if integer(item["order"], "recipe.order", 1) != index:
            raise ContractError("recipe order must be contiguous")
        observed.append(string(item["id"], "recipe.id"))
        string_list(item["inputs"], "recipe.inputs")
        string_list(item["outputs"], "recipe.outputs")
        if not set(string_list(item["required_capabilities"], "recipe.required_capabilities")).issubset(assets.CAPABILITIES):
            raise ContractError("recipe requires undeclared capability")
        string(item["failure_behavior"], "recipe.failure_behavior")
        string(item["provenance_obligations"], "recipe.provenance_obligations")
        if not set(string_list(item["evaluation_dimensions"], "recipe.evaluation_dimensions")).issubset(assets.METRIC_IDS):
            raise ContractError("recipe has unknown evaluation dimension")
        string_list(item["compatible_profiles"], "recipe.compatible_profiles", ordered=["local-deterministic", "production-adapter", "call-e"])
    if observed != assets.RECIPE_IDS:
        raise ContractError("recipe IDs or order do not match the cookbook contract")


def validate_evaluation(value: Any) -> None:
    evaluation = exact(value, {"baseline", "criteria", "adversarial_cases", "result_vocabulary", "thresholds_are_universal"}, "evaluation")
    string(evaluation["baseline"], "evaluation.baseline")
    if boolean(evaluation["thresholds_are_universal"], "thresholds_are_universal"):
        raise ContractError("quality thresholds must be project-specific, never universal")
    string_list(evaluation["result_vocabulary"], "result_vocabulary", ordered=["passed", "failed", "blocked", "not_observed"])
    if not isinstance(evaluation["criteria"], list):
        raise ContractError("evaluation.criteria must be an array")
    metrics: list[str] = []
    for raw in evaluation["criteria"]:
        criterion = exact(raw, {"metric_id", "population", "aggregation", "direction", "threshold", "rationale", "minimum_samples", "tolerance", "evidence_status"}, "evaluation criterion")
        metrics.append(string(criterion["metric_id"], "metric_id"))
        string(criterion["population"], "population")
        string(criterion["aggregation"], "aggregation")
        string(criterion["direction"], "direction", {"gte", "lte"})
        number(criterion["threshold"], "threshold")
        string(criterion["rationale"], "rationale")
        integer(criterion["minimum_samples"], "minimum_samples", 1)
        if number(criterion["tolerance"], "tolerance") < 0:
            raise ContractError("tolerance must be non-negative")
        string(criterion["evidence_status"], "evidence_status", {"passed", "failed", "blocked", "not_observed"})
    if metrics != assets.METRIC_IDS:
        raise ContractError("mandatory evaluation metric inventory is incomplete or reordered")
    if not isinstance(evaluation["adversarial_cases"], list):
        raise ContractError("adversarial_cases must be an array")
    cases: list[str] = []
    for raw in evaluation["adversarial_cases"]:
        case = exact(raw, {"id", "expected"}, "adversarial case")
        cases.append(string(case["id"], "adversarial case id"))
        string(case["expected"], "adversarial expected behavior")
    if cases != assets.ADVERSARIAL_IDS:
        raise ContractError("mandatory adversarial case inventory is incomplete or reordered")


def validate_blueprint(value: dict[str, Any], *, repo_root: Path = ROOT) -> None:
    exact(value, {"schema", "blueprint_id", "framework_id", "profile", "qualification_scope", "selected_recipes", "governance_session", "corpus", "retrieval", "adapters", "evaluation"}, "blueprint")
    string(value["schema"], "schema", {"kg-rag-blueprint/1.0"})
    string(value["blueprint_id"], "blueprint_id")
    string(value["framework_id"], "framework_id")
    string(value["profile"], "profile", {"local-deterministic", "production-adapter", "call-e"})
    string(value["qualification_scope"], "qualification_scope", {"blueprint"})
    string_list(value["selected_recipes"], "selected_recipes", ordered=assets.RECIPE_IDS)
    governance = exact(value["governance_session"], {"intent", "privacy_class", "licenses_verified", "consent_verified", "secrets_excluded", "private_content_excluded", "network_allowed", "recovery_restores_authority", "retention", "budgets"}, "governance_session")
    string(governance["intent"], "intent")
    string(governance["privacy_class"], "privacy_class")
    for key in ("licenses_verified", "consent_verified", "secrets_excluded", "private_content_excluded", "network_allowed", "recovery_restores_authority"):
        boolean(governance[key], key)
    retention = exact(governance["retention"], {"mode", "days"}, "retention")
    string(retention["mode"], "retention.mode", {"ephemeral", "bounded"})
    days = integer(retention["days"], "retention.days")
    if days > 3650 or (retention["mode"] == "ephemeral" and days != 0):
        raise ContractError("invalid retention policy")
    budgets = exact(governance["budgets"], {"latency_ms", "compute_units", "cost_observability"}, "budgets")
    integer(budgets["latency_ms"], "latency_ms", 1)
    integer(budgets["compute_units"], "compute_units", 1)
    string(budgets["cost_observability"], "cost_observability", {"observable", "unobservable"})
    if not governance["licenses_verified"] or not governance["consent_verified"] or not governance["secrets_excluded"] or not governance["private_content_excluded"]:
        raise ContractError("licenses, consent, secret exclusion, and private-content exclusion must be affirmed")
    if governance["network_allowed"] or governance["recovery_restores_authority"]:
        raise ContractError("v1 forbids network use and recovery-restored authority")
    corpus = exact(value["corpus"], {"source_ids", "ontology", "shapes", "extraction_policy", "entity_resolution_policy", "contradiction_policy", "provenance_policy", "freshness_policy", "deletion_policy", "reindex_policy"}, "corpus")
    string_list(corpus["source_ids"], "corpus.source_ids")
    digest_ref(corpus["ontology"], "corpus.ontology", repo_root)
    digest_ref(corpus["shapes"], "corpus.shapes", repo_root)
    corpus_policies = {
        "extraction_policy": "bounded-and-source-addressable",
        "entity_resolution_policy": "preserve-unresolved-and-conflicting-identities",
        "contradiction_policy": "preserve-both-sides-with-lineage",
        "provenance_policy": "preserve-record-to-claim-transformation-paths-and-reject-derivation-cycles",
        "freshness_policy": "revalidate-pinned-snapshot-before-use",
        "deletion_policy": "tombstone-delete-derived-artifacts-and-reindex",
        "reindex_policy": "deterministic-rebuild-after-update-or-deletion",
    }
    for key, expected in corpus_policies.items():
        string(corpus[key], f"corpus.{key}", {expected})
    retrieval = exact(value["retrieval"], {"route", "query_routes", "traversal", "fusion", "reranking", "context_budget", "fallback", "abstention", "evidence_packet_required", "citations_required"}, "retrieval")
    string(retrieval["route"], "retrieval.route")
    if not isinstance(retrieval["query_routes"], list) or not retrieval["query_routes"]:
        raise ContractError("query routes must be declared")
    for raw in retrieval["query_routes"]:
        route = exact(raw, {"query_class", "route"}, "query route")
        string(route["query_class"], "query_class"); string(route["route"], "query route")
    expected_query_routes = [{"query_class": "local", "route": retrieval["route"]}, {"query_class": "global", "route": retrieval["route"]}]
    if retrieval["query_routes"] != expected_query_routes:
        raise ContractError("query routes must cover local and global classes using the selected route")
    traversal = exact(retrieval["traversal"], {"direction", "maximum_depth", "maximum_candidates"}, "traversal")
    string(traversal["direction"], "direction", {"in", "out", "both"})
    integer(traversal["maximum_depth"], "maximum_depth", 1); integer(traversal["maximum_candidates"], "maximum_candidates", 1)
    fusion = exact(retrieval["fusion"], {"method", "tie_break"}, "fusion")
    string(fusion["method"], "fusion.method", {"reciprocal-rank-fusion"}); string(fusion["tie_break"], "fusion.tie_break", {"stable-identifier"})
    reranking = exact(retrieval["reranking"], {"enabled", "policy"}, "reranking")
    if not boolean(reranking["enabled"], "reranking.enabled"):
        raise ContractError("selected reranking recipe requires reranking")
    string(reranking["policy"], "reranking.policy", {"declared-adapter-only"})
    integer(retrieval["context_budget"], "context_budget", 1)
    string(retrieval["fallback"], "fallback", {"lexical-baseline-then-abstain"}); string(retrieval["abstention"], "abstention", {"required-when-evidence-insufficient"})
    if not boolean(retrieval["evidence_packet_required"], "evidence_packet_required") or not boolean(retrieval["citations_required"], "citations_required"):
        raise ContractError("evidence packets and citations are mandatory")
    adapters_value = exact(value["adapters"], set(assets.ADAPTER_KINDS), "adapters")
    implementation = "local-deterministic" if value["profile"] == "local-deterministic" else "abstract"
    for kind in assets.ADAPTER_KINDS:
        adapter = exact(adapters_value[kind], {"kind", "implementation", "network_enabled"}, f"adapter {kind}")
        if string(adapter["kind"], "adapter.kind") != kind:
            raise ContractError("adapter kind mismatch")
        string(adapter["implementation"], "adapter.implementation", {implementation})
        boolean(adapter["network_enabled"], "adapter.network_enabled")
    validate_evaluation(value["evaluation"])


def validate_qualification(value: dict[str, Any]) -> None:
    exact(value, {"schema", "qualification_scope", "suites", "required_planes", "required_metrics", "required_adversarial_cases", "baseline_state", "result_vocabulary"}, "qualification")
    string(value["schema"], "schema", {"kg-rag-qualification/1.0"})
    string(value["qualification_scope"], "qualification_scope", {"blueprint"})
    string_list(value["required_planes"], "required_planes", ordered=["governance_session", "corpus", "retrieval", "evaluation"])
    string_list(value["required_metrics"], "required_metrics", ordered=assets.METRIC_IDS)
    string_list(value["required_adversarial_cases"], "required_adversarial_cases", ordered=assets.ADVERSARIAL_IDS)
    string(value["baseline_state"], "baseline_state", {"not_observed"})
    string_list(value["result_vocabulary"], "result_vocabulary", ordered=["passed", "failed", "blocked", "not_observed"])
    if not isinstance(value["suites"], list) or len(value["suites"]) != 3:
        raise ContractError("qualification must contain local, production, and Call-E suites")
    expected = [("local", "ready"), ("production", "degraded"), ("call-e", "blocked")]
    for raw, (suite_id, status) in zip(value["suites"], expected):
        suite = exact(raw, {"id", "blueprint", "expected_status", "expected_blockers"}, "qualification suite")
        string(suite["id"], "suite.id", {suite_id})
        safe_relative(string(suite["blueprint"], "suite.blueprint"), "suite.blueprint")
        string(suite["expected_status"], "expected_status", {status})
        if not isinstance(suite["expected_blockers"], list) or any(not isinstance(item, str) for item in suite["expected_blockers"]):
            raise ContractError("expected_blockers must be a string array")


def validate_receipt(value: dict[str, Any]) -> None:
    exact(value, {"schema", "qualification_scope", "blueprint_id", "status", "planes", "digests", "capabilities", "warnings", "blockers", "runtime_readiness_qualified"}, "boot receipt")
    string(value["schema"], "schema", {"kg-rag-harness-boot-receipt/1.0"})
    string(value["qualification_scope"], "qualification_scope", {"blueprint"})
    string(value["blueprint_id"], "blueprint_id")
    string(value["status"], "status", {"ready", "degraded", "blocked"})
    planes = exact(value["planes"], {"governance_session", "corpus", "retrieval", "evaluation"}, "planes")
    blocked_seen = False
    for name in ("governance_session", "corpus", "retrieval", "evaluation"):
        plane = exact(planes[name], {"status", "reason_codes"}, f"plane {name}")
        status = string(plane["status"], "plane status", {"ready", "degraded", "blocked"})
        string_list(plane["reason_codes"], "reason_codes")
        if blocked_seen and status != "blocked":
            raise ContractError("a blocker must propagate through later planes")
        blocked_seen |= status == "blocked"
    digests = exact(value["digests"], {"blueprint", "framework_manifest", "source_ledger", "recipe_registry", "qualification", "ontology", "shapes"}, "digests")
    for label, digest_value in digests.items():
        if not SHA256_RE.fullmatch(string(digest_value, f"digest {label}")):
            raise ContractError("receipt digest must be lowercase SHA-256")
    string_list(value["capabilities"], "capabilities", ordered=assets.CAPABILITIES)
    for field in ("warnings", "blockers"):
        if not isinstance(value[field], list) or any(not isinstance(item, str) or not item for item in value[field]) or value[field] != sorted(set(value[field])):
            raise ContractError(f"{field} must be a sorted unique string array")
    if boolean(value["runtime_readiness_qualified"], "runtime_readiness_qualified"):
        raise ContractError("v1 cannot qualify runtime readiness")
    encoded_keys = " ".join(_all_keys(value)).lower()
    if any(fragment in encoded_keys for fragment in FORBIDDEN_RECEIPT_FRAGMENTS):
        raise ContractError("receipt contains a forbidden secret, private-content, approval, or authority field")
    encoded_values = " ".join(_all_strings(value)).lower()
    if re.search(r"\b(secret|credential|password|private[ -]content|approval|authority|token)\b", encoded_values):
        raise ContractError("receipt contains forbidden secret, private-content, approval, or authority material")


def _all_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return list(value) + [key for item in value.values() for key in _all_keys(item)]
    if isinstance(value, list):
        return [key for item in value for key in _all_keys(item)]
    return []


def _all_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [item for raw in value.values() for item in _all_strings(raw)]
    if isinstance(value, list):
        return [item for raw in value for item in _all_strings(raw)]
    return []


def validate_contract(value: dict[str, Any], *, repo_root: Path = ROOT) -> None:
    schema = value.get("schema")
    if schema == "kg-rag-source-ledger/1.0": validate_source_ledger(value, repo_root=repo_root)
    elif schema == "kg-rag-framework-manifest/1.0": validate_manifest(value, repo_root=repo_root)
    elif schema == "kg-rag-recipe-registry/1.0": validate_registry(value)
    elif schema == "kg-rag-blueprint/1.0": validate_blueprint(value, repo_root=repo_root)
    elif schema == "kg-rag-qualification/1.0": validate_qualification(value)
    elif schema == "kg-rag-harness-boot-receipt/1.0": validate_receipt(value)
    else: raise ContractError(f"unknown contract schema {schema!r}")


def validate_bundle(blueprint: dict[str, Any], manifest: dict[str, Any], registry: dict[str, Any], ledger: dict[str, Any], qualification: dict[str, Any], *, repo_root: Path = ROOT) -> None:
    validate_blueprint(blueprint, repo_root=repo_root)
    validate_manifest(manifest, repo_root=repo_root)
    validate_registry(registry)
    validate_source_ledger(ledger, repo_root=repo_root)
    validate_qualification(qualification)
    if blueprint["framework_id"] != manifest["framework_id"]:
        raise ContractError("blueprint framework_id does not match manifest")
    inventory = {item["path"]: item for item in manifest["artifacts"]}
    for path, contract in (
        ("kg-rag/source-ledger.json", ledger),
        ("kg-rag/recipe-registry.json", registry),
        ("kg-rag/qualification.json", qualification),
    ):
        ref = inventory.get(path)
        encoded = canonical(contract)
        if ref is None or ref["bytes"] != len(encoded) or ref["sha256"] != sha256(encoded):
            raise ContractError(f"manifest does not bind the supplied {path}")
    profile = next((item for item in manifest["profiles"] if item["name"] == blueprint["profile"]), None)
    if profile is None or blueprint["retrieval"]["route"] not in profile["allowed_routes"]:
        raise ContractError("unsupported query route for selected profile")
    if set(blueprint["selected_recipes"]) != {item["id"] for item in registry["recipes"]}:
        raise ContractError("selected recipes do not match registry")
    ledger_ids = {item["id"] for item in ledger["sources"]}
    unknown_sources = set(blueprint["corpus"]["source_ids"]) - ledger_ids
    if blueprint["profile"] == "call-e":
        unknown_sources.discard("call-e-authoritative-brief")
    if unknown_sources:
        raise ContractError(f"blueprint has unresolved source IDs: {', '.join(sorted(unknown_sources))}")
    any_network = any(item["network_enabled"] for item in blueprint["adapters"].values())
    if any_network != blueprint["governance_session"]["network_allowed"] or any_network:
        raise ContractError("network use must be explicitly declared and is forbidden by v1 profiles")
    if not blueprint["governance_session"]["licenses_verified"] or not blueprint["governance_session"]["consent_verified"]:
        raise ContractError("unlicensed or unauthorized inputs are forbidden")
    if blueprint["governance_session"]["recovery_restores_authority"]:
        raise ContractError("recovery cannot restore authority")


def boot(blueprint_bytes: bytes, manifest_bytes: bytes, registry: dict[str, Any], ledger: dict[str, Any], qualification: dict[str, Any], *, repo_root: Path = ROOT) -> bytes:
    blueprint = strict_json_bytes(blueprint_bytes, "blueprint", canonical_required=True)
    manifest = strict_json_bytes(manifest_bytes, "manifest", canonical_required=True)
    validate_bundle(blueprint, manifest, registry, ledger, qualification, repo_root=repo_root)
    blockers: list[str] = []
    warnings: list[str] = []
    if blueprint["profile"] == "call-e" and "call-e-authoritative-brief" not in {item["id"] for item in ledger["sources"]}:
        blockers.append("blocked_pending_authoritative_brief")
    if blueprint["profile"] == "production-adapter" or (blueprint["profile"] == "call-e" and not blockers):
        warnings.append("abstract_adapters_require_runtime_implementation")
    statuses: dict[str, dict[str, Any]] = {}
    blocked = False
    for plane in ("governance_session", "corpus", "retrieval", "evaluation"):
        reasons = ["declarations_validated_offline"]
        status = "ready"
        if blockers or blocked:
            status, blocked = "blocked", True
            reasons = sorted(set(blockers or ["upstream_plane_blocked"]))
        elif plane == "retrieval" and warnings:
            status, reasons = "degraded", sorted(warnings)
        statuses[plane] = {"status": status, "reason_codes": reasons}
    status = "blocked" if blockers else "degraded" if warnings else "ready"
    ontology = contained(repo_root, blueprint["corpus"]["ontology"]["path"], "ontology")
    shapes = contained(repo_root, blueprint["corpus"]["shapes"]["path"], "shapes")
    receipt = {
        "schema": "kg-rag-harness-boot-receipt/1.0",
        "qualification_scope": "blueprint",
        "blueprint_id": blueprint["blueprint_id"],
        "status": status,
        "planes": statuses,
        "digests": {
            "blueprint": sha256(blueprint_bytes),
            "framework_manifest": sha256(manifest_bytes),
            "source_ledger": sha256(canonical(ledger)),
            "recipe_registry": sha256(canonical(registry)),
            "qualification": sha256(canonical(qualification)),
            "ontology": sha256(ontology.read_bytes()),
            "shapes": sha256(shapes.read_bytes()),
        },
        "capabilities": manifest["capabilities"],
        "warnings": sorted(set(warnings)),
        "blockers": sorted(set(blockers)),
        "runtime_readiness_qualified": False,
    }
    validate_receipt(receipt)
    return canonical(receipt)


def atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise ContractError("temporary output path already exists")
    try:
        with temporary.open("xb") as handle:
            handle.write(content); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.is_file() and not temporary.is_symlink():
            temporary.unlink()
