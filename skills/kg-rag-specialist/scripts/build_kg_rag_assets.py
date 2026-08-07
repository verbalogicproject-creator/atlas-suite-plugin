#!/usr/bin/env python3
"""Build the canonical, offline KG-RAG contract assets and fixtures."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


_CANDIDATE_ROOT = Path(__file__).resolve().parent.parent
ROOT = _CANDIDATE_ROOT / "references/kg-rag/workspace" if (_CANDIDATE_ROOT / "references/kg-rag/workspace/kg-rag").is_dir() else _CANDIDATE_ROOT
COOKBOOK_VERSION = "0.1.0"
RECIPE_IDS = [
    "source-intake",
    "ontology-design",
    "chunking",
    "entity-relation-extraction",
    "entity-resolution",
    "graph-construction",
    "lexical-vector-indexing",
    "query-classification",
    "graph-traversal",
    "community-global-retrieval",
    "hybrid-fusion",
    "reranking",
    "evidence-packet-assembly",
    "cited-answering",
    "contradiction-handling",
    "abstention",
    "update-deletion-reindexing",
    "adversarial-evaluation",
]
METRIC_IDS = [
    "retrieval-recall",
    "retrieval-precision",
    "ranking",
    "entity-resolution",
    "triple-path-validity",
    "citation-precision",
    "citation-coverage",
    "factual-consistency",
    "contradiction-response",
    "abstention",
    "freshness-deletion",
    "latency",
    "cost-observability",
    "injection-refusal",
    "protected-effect-refusal",
]
ADVERSARIAL_IDS = [
    "retrieved-instruction-injection",
    "source-impersonation",
    "entity-collision",
    "contradiction-and-staleness",
    "deletion-followed-by-retrieval",
    "adapter-capability-mismatch",
    "secret-or-private-content-request",
    "protected-effect-request",
]
ADAPTER_KINDS = [
    "graph_store",
    "vector_index",
    "lexical_index",
    "embedder",
    "reranker",
    "answerer",
    "observability",
]
CAPABILITIES = [
    "canonical-json-graph",
    "canonical-jsonl-vector",
    "offline-validation",
    "lexical-baseline",
    "source-ledger",
    "ontology-shapes",
    "entity-relation-extraction",
    "entity-resolution",
    "graph-construction",
    "vector-indexing",
    "query-classification",
    "bounded-graph-traversal",
    "community-global-retrieval",
    "hybrid-fusion",
    "reranking",
    "evidence-packet-assembly",
    "cited-answering",
    "contradiction-handling",
    "abstention",
    "update-deletion-reindexing",
    "adversarial-evaluation",
    "cost-observability",
]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source(
    source_id: str,
    title: str,
    locator: str,
    locator_type: str,
    publisher: str,
    version_or_date: str,
    authority_class: str,
    license_status: str,
    usage_status: str,
    digest_status: str,
    sha256: str | None = None,
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "locator": locator,
        "locator_type": locator_type,
        "publisher": publisher,
        "version_or_date": version_or_date,
        "accessed": "2026-08-01",
        "authority_class": authority_class,
        "license_status": license_status,
        "usage_status": usage_status,
        "consent_status": "authorized",
        "retention_policy": "locator-and-metadata-only" if locator_type == "https" else "repository-lifecycle",
        "deletion_policy": "remove-ledger-entry-and-derived-artifacts",
        "freshness": "version-pinned" if version_or_date != "living" else "living-reverify-before-use",
        "digest_status": digest_status,
        "sha256": sha256,
        "provenance_is_integrity": False,
        "vendored_body": False,
    }


def source_ledger() -> dict[str, Any]:
    return {
        "schema": "kg-rag-source-ledger/1.0",
        "cookbook_version": COOKBOOK_VERSION,
        "sources": [
            source(
                "itl-terminology-177",
                "In the Loop architecture terminology corpus (177 entries)",
                "docs/knowledge/itl-architecture-terms.json",
                "repository-relative",
                "In the Loop contributors",
                "repository snapshot 2026-07-31",
                "local-grounding",
                "MIT-component",
                "human-authorized-local-grounding",
                "stable",
                "13b41347baf1ad00833fc7617c5fb0f33492fe53e3d7a659eb9dd9de353ef8fb",
            ),
            source("rdf-1.2-concepts", "RDF 1.2 Concepts and Abstract Data Model", "https://www.w3.org/TR/2026/CR-rdf12-concepts-20260407/", "https", "W3C", "Candidate Recommendation 2026-04-07", "external-primary", "W3C-document-license", "reference-only", "not-observed"),
            source("shacl", "Shapes Constraint Language (SHACL)", "https://www.w3.org/TR/2017/REC-shacl-20170720/", "https", "W3C", "Recommendation 2017-07-20", "external-primary", "W3C-document-license", "reference-only", "not-observed"),
            source("prov-o", "PROV-O: The PROV Ontology", "https://www.w3.org/TR/2013/REC-prov-o-20130430/", "https", "W3C", "Recommendation 2013-04-30", "external-primary", "W3C-document-license", "reference-only", "not-observed"),
            source("json-ld-1.1", "JSON-LD 1.1", "https://www.w3.org/TR/2020/REC-json-ld11-20200716/", "https", "W3C", "Recommendation 2020-07-16", "external-primary", "W3C-document-license", "reference-only", "not-observed"),
            source("rag-v4", "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "https://arxiv.org/abs/2005.11401v4", "https", "arXiv", "v4 2021-04-12", "external-research", "external-license-recorded-at-locator", "reference-only", "not-observed"),
            source("microsoft-graphrag", "Microsoft GraphRAG documentation", "https://microsoft.github.io/graphrag/", "https", "Microsoft", "living", "external-explanatory", "external-project-documentation", "explanatory-reference-only", "not-observed"),
            source("nist-ai-rmf-1.0", "Artificial Intelligence Risk Management Framework 1.0", "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf", "https", "NIST", "AI 100-1 2023-01", "external-primary", "US-government-publication", "reference-only", "not-observed"),
            source("otel-semconv-1.40.0", "OpenTelemetry Semantic Conventions", "https://github.com/open-telemetry/semantic-conventions/releases/tag/v1.40.0", "https", "OpenTelemetry", "v1.40.0", "external-explanatory", "Apache-2.0-project", "explanatory-reference-only", "not-observed"),
        ],
    }


def recipes() -> dict[str, Any]:
    details = {
        "source-intake": (["source candidates"], ["governed source ledger entries"], ["source-ledger"], ["freshness-deletion", "protected-effect-refusal"]),
        "ontology-design": (["intent", "source vocabulary"], ["ontology and shapes plans"], ["ontology-shapes"], ["triple-path-validity"]),
        "chunking": (["governed records"], ["stable addressable chunks"], ["canonical-json-graph"], ["retrieval-recall", "retrieval-precision"]),
        "entity-relation-extraction": (["chunks", "ontology"], ["entity mentions and relation claims"], ["entity-relation-extraction"], ["entity-resolution", "triple-path-validity"]),
        "entity-resolution": (["entity mentions"], ["stable entities and unresolved mentions"], ["entity-resolution"], ["entity-resolution"]),
        "graph-construction": (["claims", "provenance paths"], ["canonical graph snapshot"], ["graph-construction"], ["triple-path-validity"]),
        "lexical-vector-indexing": (["chunks", "graph snapshot"], ["lexical and vector index declarations"], ["lexical-baseline", "vector-indexing"], ["retrieval-recall", "retrieval-precision"]),
        "query-classification": (["query"], ["declared query route"], ["query-classification"], ["ranking"]),
        "graph-traversal": (["query seeds", "graph"], ["bounded subgraph"], ["bounded-graph-traversal"], ["triple-path-validity", "latency"]),
        "community-global-retrieval": (["query", "community declarations"], ["community or global candidates"], ["community-global-retrieval"], ["retrieval-recall", "ranking"]),
        "hybrid-fusion": (["lexical", "vector", "graph candidates"], ["fused candidates"], ["hybrid-fusion"], ["retrieval-precision", "ranking"]),
        "reranking": (["fused candidates"], ["ranked evidence"], ["reranking"], ["ranking", "latency"]),
        "evidence-packet-assembly": (["ranked evidence", "provenance"], ["evidence packet"], ["evidence-packet-assembly"], ["citation-coverage", "triple-path-validity"]),
        "cited-answering": (["evidence packet"], ["cited answer plan"], ["cited-answering"], ["citation-precision", "citation-coverage", "factual-consistency"]),
        "contradiction-handling": (["conflicting claims"], ["preserved contradiction set"], ["contradiction-handling"], ["contradiction-response"]),
        "abstention": (["evidence sufficiency"], ["answer or abstention decision"], ["abstention"], ["abstention"]),
        "update-deletion-reindexing": (["source mutation"], ["updated artifacts and tombstones"], ["update-deletion-reindexing"], ["freshness-deletion"]),
        "adversarial-evaluation": (["blueprint", "adversarial suite"], ["evaluation plan"], ["adversarial-evaluation"], ["injection-refusal", "protected-effect-refusal"]),
    }
    rows = []
    for order, recipe_id in enumerate(RECIPE_IDS, 1):
        inputs, outputs, capabilities, dimensions = details[recipe_id]
        rows.append({
            "order": order,
            "id": recipe_id,
            "inputs": inputs,
            "outputs": outputs,
            "required_capabilities": capabilities,
            "failure_behavior": "fail-closed-and-report-missing-input",
            "provenance_obligations": "preserve-record-to-output-lineage-and-contradictions",
            "evaluation_dimensions": dimensions,
            "compatible_profiles": ["local-deterministic", "production-adapter", "call-e"],
        })
    return {"schema": "kg-rag-recipe-registry/1.0", "cookbook_version": COOKBOOK_VERSION, "recipes": rows}


def ontology_plan() -> dict[str, Any]:
    return {
        "schema": "kg-rag-ontology-plan/1.0",
        "version": COOKBOOK_VERSION,
        "classes": ["Source", "Record", "Chunk", "Entity", "Claim", "EvidencePacket"],
        "relations": ["contains", "mentions", "asserts", "supports", "contradicts", "derivedFrom"],
        "identity_policy": "stable-source-scoped-identifiers-with-explicit-equivalence",
        "contradiction_policy": "preserve-both-claims-and-lineage",
    }


def shapes_plan() -> dict[str, Any]:
    return {
        "schema": "kg-rag-shapes-plan/1.0",
        "version": COOKBOOK_VERSION,
        "required_shapes": ["record-has-source", "claim-has-provenance", "edge-endpoints-resolve", "evidence-has-citation"],
        "severity_policy": {"warning": "degraded", "violation": "blocked"},
    }


def artifact_ref(path: str, data: bytes) -> dict[str, Any]:
    return {"path": path, "bytes": len(data), "sha256": digest(data), "version": COOKBOOK_VERSION}


def evaluation_plan() -> dict[str, Any]:
    directions = {"latency": "lte", "cost-observability": "lte"}
    criteria = []
    for index, metric_id in enumerate(METRIC_IDS):
        threshold = 1000 if metric_id == "latency" else 1 if metric_id in {"cost-observability", "injection-refusal", "protected-effect-refusal"} else round(0.55 + (index % 4) * 0.05, 2)
        criteria.append({
            "metric_id": metric_id,
            "population": f"project-fixtures-{metric_id}",
            "aggregation": "macro-average" if metric_id not in {"latency", "cost-observability"} else "p95",
            "direction": directions.get(metric_id, "gte"),
            "threshold": threshold,
            "rationale": f"project-specific predeclared acceptance boundary for {metric_id}",
            "minimum_samples": 1,
            "tolerance": 0.0,
            "evidence_status": "not_observed",
        })
    return {
        "baseline": "offline-lexical-baseline",
        "criteria": criteria,
        "adversarial_cases": [{"id": item, "expected": "refuse-or-preserve-boundary"} for item in ADVERSARIAL_IDS],
        "result_vocabulary": ["passed", "failed", "blocked", "not_observed"],
        "thresholds_are_universal": False,
    }


def blueprint(profile: str, ontology_bytes: bytes, shapes_bytes: bytes) -> dict[str, Any]:
    route = {"local-deterministic": "local-hybrid", "production-adapter": "production-hybrid", "call-e": "call-e"}[profile]
    implementation = "local-deterministic" if profile == "local-deterministic" else "abstract"
    source_ids = [item["id"] for item in source_ledger()["sources"]]
    if profile == "call-e":
        source_ids.append("call-e-authoritative-brief")
    return {
        "schema": "kg-rag-blueprint/1.0",
        "blueprint_id": profile,
        "framework_id": "itl-kg-rag-cookbook",
        "profile": profile,
        "qualification_scope": "blueprint",
        "selected_recipes": RECIPE_IDS,
        "governance_session": {
            "intent": "qualify a provider-neutral KG-RAG blueprint only",
            "privacy_class": "public-and-synthetic-only",
            "licenses_verified": True,
            "consent_verified": True,
            "secrets_excluded": True,
            "private_content_excluded": True,
            "network_allowed": False,
            "recovery_restores_authority": False,
            "retention": {"mode": "ephemeral", "days": 0},
            "budgets": {"latency_ms": 1000, "compute_units": 1, "cost_observability": "unobservable"},
        },
        "corpus": {
            "source_ids": source_ids,
            "ontology": artifact_ref("kg-rag/ontology-plan.json", ontology_bytes),
            "shapes": artifact_ref("kg-rag/shapes-plan.json", shapes_bytes),
            "extraction_policy": "bounded-and-source-addressable",
            "entity_resolution_policy": "preserve-unresolved-and-conflicting-identities",
            "contradiction_policy": "preserve-both-sides-with-lineage",
            "provenance_policy": "preserve-record-to-claim-transformation-paths-and-reject-derivation-cycles",
            "freshness_policy": "revalidate-pinned-snapshot-before-use",
            "deletion_policy": "tombstone-delete-derived-artifacts-and-reindex",
            "reindex_policy": "deterministic-rebuild-after-update-or-deletion",
        },
        "retrieval": {
            "route": route,
            "query_routes": [{"query_class": "local", "route": route}, {"query_class": "global", "route": route}],
            "traversal": {"direction": "both", "maximum_depth": 2, "maximum_candidates": 100},
            "fusion": {"method": "reciprocal-rank-fusion", "tie_break": "stable-identifier"},
            "reranking": {"enabled": True, "policy": "declared-adapter-only"},
            "context_budget": 4096,
            "fallback": "lexical-baseline-then-abstain",
            "abstention": "required-when-evidence-insufficient",
            "evidence_packet_required": True,
            "citations_required": True,
        },
        "adapters": {
            kind: {"kind": kind, "implementation": implementation, "network_enabled": False}
            for kind in ADAPTER_KINDS
        },
        "evaluation": evaluation_plan(),
    }


def qualification() -> dict[str, Any]:
    return {
        "schema": "kg-rag-qualification/1.0",
        "qualification_scope": "blueprint",
        "suites": [
            {"id": "local", "blueprint": "fixtures/kg-rag/valid/local-deterministic.json", "expected_status": "ready", "expected_blockers": []},
            {"id": "production", "blueprint": "fixtures/kg-rag/valid/production-adapter.json", "expected_status": "degraded", "expected_blockers": []},
            {"id": "call-e", "blueprint": "fixtures/kg-rag/valid/call-e-blocked.json", "expected_status": "blocked", "expected_blockers": ["blocked_pending_authoritative_brief"]},
        ],
        "required_planes": ["governance_session", "corpus", "retrieval", "evaluation"],
        "required_metrics": METRIC_IDS,
        "required_adversarial_cases": ADVERSARIAL_IDS,
        "baseline_state": "not_observed",
        "result_vocabulary": ["passed", "failed", "blocked", "not_observed"],
    }


def receipt_example() -> dict[str, Any]:
    return {
        "schema": "kg-rag-harness-boot-receipt/1.0",
        "qualification_scope": "blueprint",
        "blueprint_id": "example",
        "status": "ready",
        "planes": {name: {"status": "ready", "reason_codes": ["declared"]} for name in qualification()["required_planes"]},
        "digests": {name: "0" * 64 for name in ["blueprint", "framework_manifest", "source_ledger", "recipe_registry", "qualification", "ontology", "shapes"]},
        "capabilities": CAPABILITIES,
        "warnings": [],
        "blockers": [],
        "runtime_readiness_qualified": False,
    }


def infer_schema(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            "type": "object",
            "additionalProperties": False,
            "required": list(value),
            "properties": {key: infer_schema(item) for key, item in value.items()},
        }
    if isinstance(value, list):
        schemas = [infer_schema(item) for item in value]
        unique = {json.dumps(schema, sort_keys=True, separators=(",", ":")): schema for schema in schemas}
        if not unique:
            items: dict[str, Any] = {}
        elif len(unique) == 1:
            items = next(iter(unique.values()))
        else:
            items = {"anyOf": [unique[key] for key in sorted(unique)]}
        return {"type": "array", "items": items}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if value is None:
        return {"type": ["string", "null"]}
    return {"type": "string"}


def contract_schema(name: str, example: dict[str, Any]) -> dict[str, Any]:
    value = infer_schema(example)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://in-the-loop.local/schemas/kg-rag/{name}.schema.json",
        "title": name,
        **value,
    }


def framework(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    profiles = []
    for name, maturity, route in (
        ("local-deterministic", "blueprint", "local-hybrid"),
        ("production-adapter", "abstract", "production-hybrid"),
        ("call-e", "blocked", "call-e"),
    ):
        profiles.append({
            "name": name,
            "maturity": maturity,
            "network_policy": "forbidden",
            "allowed_routes": [route],
            "capabilities": CAPABILITIES,
            "required_adapters": ADAPTER_KINDS,
        })
    return {
        "schema": "kg-rag-framework-manifest/1.0",
        "framework_id": "itl-kg-rag-cookbook",
        "cookbook_version": COOKBOOK_VERSION,
        "integrity_notice": "Artifact digests prove exact local bytes, not provenance, truth, or runtime readiness.",
        "capabilities": CAPABILITIES,
        "profiles": profiles,
        "artifacts": artifacts,
    }


def ngf_schema() -> dict[str, Any]:
    example = {
        "ngf_format": "normative-grounded-framework/1.0",
        "document_id": "kg-rag-00",
        "title": "title",
        "revision": COOKBOOK_VERSION,
        "status": "reviewed",
        "authority_class": "controlling-contract",
        "source_manifest": "../../kg-rag/source-ledger.json",
        "last_updated": "2026-08-01",
    }
    return contract_schema("ngf-document", example)


def expected_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    ledger = source_ledger()
    registry = recipes()
    ontology = ontology_plan()
    shapes = shapes_plan()
    ontology_bytes = canonical(ontology)
    shapes_bytes = canonical(shapes)
    blueprints = {
        "local-deterministic": blueprint("local-deterministic", ontology_bytes, shapes_bytes),
        "production-adapter": blueprint("production-adapter", ontology_bytes, shapes_bytes),
        "call-e-blocked": blueprint("call-e", ontology_bytes, shapes_bytes),
    }
    qualify = qualification()
    files.update({
        "kg-rag/source-ledger.json": canonical(ledger),
        "kg-rag/recipe-registry.json": canonical(registry),
        "kg-rag/ontology-plan.json": ontology_bytes,
        "kg-rag/shapes-plan.json": shapes_bytes,
        "kg-rag/qualification.json": canonical(qualify),
    })
    for name, value in blueprints.items():
        files[f"fixtures/kg-rag/valid/{name}.json"] = canonical(value)
    examples = {
        "ngf-document": None,
        "kg-rag-source-ledger": ledger,
        "kg-rag-recipe-registry": registry,
        "kg-rag-blueprint": blueprints["local-deterministic"],
        "kg-rag-qualification": qualify,
        "kg-rag-harness-boot-receipt": receipt_example(),
        "kg-rag-framework-manifest": framework([artifact_ref("example.json", b"{}\n")]),
    }
    for name, value in examples.items():
        schema = ngf_schema() if value is None else contract_schema(name, value)
        files[f"schemas/kg-rag/{name}.schema.json"] = canonical(schema)
    inventory_paths = [
        "kg-rag/source-ledger.json",
        "kg-rag/recipe-registry.json",
        "kg-rag/qualification.json",
        "kg-rag/ontology-plan.json",
        "kg-rag/shapes-plan.json",
        *sorted(path for path in files if path.startswith("schemas/kg-rag/")),
        *sorted(path for path in files if path.startswith("fixtures/kg-rag/valid/")),
    ]
    artifacts = [artifact_ref(path, files[path]) for path in inventory_paths]
    files["kg-rag/framework-manifest.json"] = canonical(framework(artifacts))
    return files


def invalid_files(valid: dict[str, Any]) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    mutations: dict[str, Any] = {}
    value = copy.deepcopy(valid); value["corpus"]["ontology"]["path"] = "kg-rag/missing-ontology.json"; mutations["missing-ontology"] = value
    value = copy.deepcopy(valid); value["retrieval"]["route"] = "unsupported"; mutations["unsupported-route"] = value
    value = copy.deepcopy(valid); value["evaluation"]["criteria"][0].pop("threshold"); mutations["absent-threshold"] = value
    value = copy.deepcopy(valid); value["adapters"]["graph_store"]["network_enabled"] = True; mutations["undeclared-network"] = value
    value = copy.deepcopy(valid); value["governance_session"]["retention"] = {"mode": "undefined", "days": -1}; mutations["invalid-retention"] = value
    value = copy.deepcopy(valid); value["adapters"]["graph_store"]["kind"] = "vector_index"; mutations["adapter-mismatch"] = value
    value = copy.deepcopy(valid); value["corpus"]["shapes"]["path"] = "kg-rag/missing-shapes.json"; mutations["missing-shapes"] = value
    value = copy.deepcopy(valid); value["corpus"]["ontology"]["sha256"] = "0" * 64; mutations["digest-mismatch"] = value
    value = copy.deepcopy(valid); value["evaluation"]["adversarial_cases"].pop(); mutations["missing-adversarial-case"] = value
    value = copy.deepcopy(valid); value["governance_session"]["licenses_verified"] = False; mutations["unlicensed-input"] = value
    value = copy.deepcopy(valid); value["governance_session"]["secrets_excluded"] = False; mutations["secrets-not-excluded"] = value
    value = copy.deepcopy(valid); value["governance_session"]["private_content_excluded"] = False; mutations["private-content-not-excluded"] = value
    value = copy.deepcopy(valid); value["corpus"]["deletion_policy"] = "retain-private-derived-artifacts-forever"; mutations["invalid-deletion-policy"] = value
    value = copy.deepcopy(valid); value["retrieval"]["fusion"]["tie_break"] = "random"; mutations["nondeterministic-tie-break"] = value
    for name, mutation in mutations.items():
        result[f"fixtures/kg-rag/invalid/{name}.json"] = canonical(mutation)
    return result


def build() -> dict[str, bytes]:
    files = expected_files()
    valid = json.loads(files["fixtures/kg-rag/valid/local-deterministic.json"])
    files.update(invalid_files(valid))
    return files


def write(files: dict[str, bytes]) -> None:
    for relative, content in sorted(files.items()):
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def write_goldens() -> None:
    """Materialize receipts through the independently validated boot contract."""
    try:
        from scripts import kg_rag_lib as lib
    except ModuleNotFoundError:
        import kg_rag_lib as lib  # type: ignore[no-redef]
    manifest_bytes = (ROOT / "kg-rag/framework-manifest.json").read_bytes()
    registry = lib.read_json(ROOT / "kg-rag/recipe-registry.json")
    ledger = lib.read_json(ROOT / "kg-rag/source-ledger.json")
    qualification_value = lib.read_json(ROOT / "kg-rag/qualification.json")
    for suite in qualification_value["suites"]:
        blueprint_path = ROOT / suite["blueprint"]
        receipt = lib.boot(blueprint_path.read_bytes(), manifest_bytes, registry, ledger, qualification_value)
        target = ROOT / "fixtures/kg-rag/golden" / f"{blueprint_path.stem}.receipt.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(receipt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args()
    files = build()
    write(files)
    write_goldens()
    print(f"wrote {len(files)} canonical KG-RAG assets and three golden receipts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
