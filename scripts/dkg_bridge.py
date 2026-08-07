#!/usr/bin/env python3
"""Thin plugin bridge that executes the paired DKG CLI without contract drift."""

from __future__ import annotations

import os
import re
import sys
import tomllib
from pathlib import Path


def _framework_src() -> Path:
    configured = os.environ.get("DKG_FRAMEWORK_ROOT")
    if configured:
        root = Path(configured).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parents[2] / "deterministic-kg-rag-framework"
    source = root / "src"
    if not (source / "dkg" / "cli.py").is_file():
        raise SystemExit("atlas-suite: paired deterministic-kg-rag-framework was not found; set DKG_FRAMEWORK_ROOT")
    metadata_path = root / "pyproject.toml"
    try:
        with metadata_path.open("rb") as handle:
            project = tomllib.load(handle)["project"]
        name = project["name"]
        version = project["version"]
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit("atlas-suite: paired framework identity is missing or unparseable") from exc
    if name != "deterministic-kg-rag-framework" or not isinstance(version, str) or re.fullmatch(r"1\.\d+\.\d+(?:(?:a|b|rc)\d+)?(?:\.post\d+)?(?:\.dev\d+)?", version) is None:
        raise SystemExit("atlas-suite: paired framework must be deterministic-kg-rag-framework 1.x")
    return source


def main() -> int:
    sys.path.insert(0, str(_framework_src()))
    from dkg.cli import main as dkg_main

    return dkg_main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
