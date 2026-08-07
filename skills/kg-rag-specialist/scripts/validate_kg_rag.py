#!/usr/bin/env python3
"""Validate canonical KG-RAG contracts, fixtures, schemas, and receipts."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from scripts import build_kg_rag_assets as builder
    from scripts import kg_rag_lib as lib
except ModuleNotFoundError:
    import build_kg_rag_assets as builder  # type: ignore[no-redef]
    import kg_rag_lib as lib  # type: ignore[no-redef]


def check(root: Path = lib.ROOT) -> None:
    expected = builder.build()
    for relative, content in sorted(expected.items()):
        path = lib.contained(root, relative, f"canonical asset {relative}")
        if path.read_bytes() != content:
            raise lib.ContractError(f"{relative} is stale; run build_kg_rag_assets.py --write")
    for schema_name, path in sorted(lib.SCHEMA_FILES.items()):
        schema = lib.read_json(path)
        if schema.get("$id") != f"https://in-the-loop.local/schemas/kg-rag/{path.name}":
            raise lib.ContractError(f"{path}: wrong $id for {schema_name}")
        if schema.get("additionalProperties") is not False:
            raise lib.ContractError(f"{path}: root schema is not closed")
    ledger = lib.read_json(root / "kg-rag/source-ledger.json")
    manifest = lib.read_json(root / "kg-rag/framework-manifest.json")
    registry = lib.read_json(root / "kg-rag/recipe-registry.json")
    qualification = lib.read_json(root / "kg-rag/qualification.json")
    for value in (ledger, manifest, registry, qualification):
        lib.validate_contract(value, repo_root=root)
    for suite in qualification["suites"]:
        blueprint_path = lib.contained(root, suite["blueprint"], "qualification blueprint")
        generated = lib.boot(blueprint_path.read_bytes(), (root / "kg-rag/framework-manifest.json").read_bytes(), registry, ledger, qualification, repo_root=root)
        receipt = lib.strict_json_bytes(generated, "generated receipt", canonical_required=True)
        if receipt["status"] != suite["expected_status"] or receipt["blockers"] != suite["expected_blockers"]:
            raise lib.ContractError(f"{blueprint_path}: qualification result mismatch")
        golden = root / "fixtures/kg-rag/golden" / f"{blueprint_path.stem}.receipt.json"
        if generated != golden.read_bytes():
            raise lib.ContractError(f"{golden}: stale golden receipt")
    invalid = sorted((root / "fixtures/kg-rag/invalid").glob("*.json"))
    expected_invalid = {Path(path).stem for path in builder.invalid_files(builder.blueprint("local-deterministic", builder.canonical(builder.ontology_plan()), builder.canonical(builder.shapes_plan())))}
    if {path.stem for path in invalid} != expected_invalid:
        raise lib.ContractError("invalid fixture set is incomplete")
    for path in invalid:
        try:
            value = lib.read_json(path)
            lib.validate_bundle(value, manifest, registry, ledger, qualification, repo_root=root)
        except lib.ContractError:
            continue
        raise lib.ContractError(f"invalid fixture unexpectedly accepted: {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        check()
    except (OSError, UnicodeError, lib.ContractError) as error:
        print(f"KG-RAG validation failed: {error}", file=sys.stderr)
        return 1
    print("validated KG-RAG contracts, fixtures, schemas, and deterministic receipts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
