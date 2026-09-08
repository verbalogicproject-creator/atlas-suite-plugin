#!/usr/bin/env python3
"""Thin plugin bridge that executes the paired DKG CLI without contract drift."""

from __future__ import annotations

import os
import json
import re
import sys
import tomllib
from pathlib import Path


REQUIRED_CAPABILITIES = {
    "api-schema-projection",
    "atlas-five-core",
    "backend-read-v1",
    "domain-mining",
    "domain-qualification",
    "project-atlas-four-file",
    "query-capabilities-16",
}

VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def _compatible_framework_version(value: object) -> bool:
    if not isinstance(value, str):
        return False
    matched = VERSION_RE.fullmatch(value)
    if matched is None:
        return False
    version = tuple(int(part) for part in matched.groups())
    return (0, 3, 0) <= version < (0, 4, 0)


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
    interface_path = root / "config" / "framework-interface.json"
    try:
        with metadata_path.open("rb") as handle:
            project = tomllib.load(handle)["project"]
        name = project["name"]
        version = project["version"]
        python_requires = project["requires-python"]
        interface = json.loads(interface_path.read_text(encoding="utf-8"))
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit("atlas-suite: paired framework identity is missing or unparseable") from exc
    expected_interface = {
        "schema", "distribution", "framework_version", "cli_contract",
        "python_requires", "capabilities", "proof_limit",
    }
    compatible = (
        name == "deterministic-kg-rag-framework"
        and _compatible_framework_version(version)
        and python_requires == ">=3.11"
        and sys.version_info >= (3, 11)
        and isinstance(interface, dict)
        and set(interface) == expected_interface
        and interface["schema"] == "dkg-framework-interface/1.0"
        and interface["distribution"] == name
        and interface["framework_version"] == version
        and interface["cli_contract"] == "dkg-cli/1.0"
        and interface["python_requires"] == python_requires
        and isinstance(interface["capabilities"], list)
        and interface["capabilities"] == sorted(set(interface["capabilities"]))
        and all(isinstance(item, str) and item for item in interface["capabilities"])
    )
    if not compatible:
        raise SystemExit("atlas-suite: paired framework must be version >=0.3.0,<0.4.0 with Python >=3.11, dkg-framework-interface/1.0, and dkg-cli/1.0")
    missing = sorted(REQUIRED_CAPABILITIES - set(interface["capabilities"]))
    if missing:
        raise SystemExit(f"atlas-suite: paired framework is missing required capabilities: {','.join(missing)}")
    return source


def main() -> int:
    arguments = sys.argv[1:] or ["menu"]
    if arguments[0] == "profile":
        from qualification_core import main as profile_main

        return profile_main(arguments[1:])
    sys.path.insert(0, str(_framework_src()))
    from dkg.cli import main as dkg_main

    return dkg_main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
