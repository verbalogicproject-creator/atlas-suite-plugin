#!/usr/bin/env python3
"""Fail-closed, offline Harness Boot for a KG-RAG blueprint."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from scripts import kg_rag_lib as lib
except ModuleNotFoundError:
    import kg_rag_lib as lib  # type: ignore[no-redef]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=lib.ROOT / "kg-rag/recipe-registry.json")
    parser.add_argument("--ledger", type=Path, default=lib.ROOT / "kg-rag/source-ledger.json")
    parser.add_argument("--qualification", type=Path, default=lib.ROOT / "kg-rag/qualification.json")
    parser.add_argument("--output", type=str)
    args = parser.parse_args(argv)
    try:
        blueprint_path = lib.safe_existing_file(args.blueprint, lib.ROOT, "blueprint")
        manifest_path = lib.safe_existing_file(args.manifest, lib.ROOT, "manifest")
        registry = lib.read_json(args.registry)
        ledger = lib.read_json(args.ledger)
        qualification = lib.read_json(args.qualification)
        content = lib.boot(blueprint_path.read_bytes(), manifest_path.read_bytes(), registry, ledger, qualification)
        if args.output is None:
            sys.stdout.buffer.write(content)
        else:
            output = lib.contained(Path.cwd(), args.output, "output", must_exist=False)
            if output.exists() and (output.is_symlink() or not output.is_file()):
                raise lib.ContractError("output must be a regular file when it exists")
            if not output.parent.is_dir() or output.parent.is_symlink():
                raise lib.ContractError("output parent must be an existing non-symlink directory")
            lib.atomic_write(output, content)
    except (OSError, UnicodeError, lib.ContractError) as error:
        print(f"Harness Boot failed closed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
