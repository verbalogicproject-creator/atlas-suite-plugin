#!/usr/bin/env python3
"""Validate Normative Grounded Framework Markdown without external packages."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from scripts import kg_rag_lib as lib
except ModuleNotFoundError:
    import kg_rag_lib as lib  # type: ignore[no-redef]

KEYS = {"ngf_format", "document_id", "title", "revision", "status", "authority_class", "source_manifest", "last_updated"}
DOCUMENT_ID = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?")
H2 = re.compile(r"^## \[(Normative|Explanatory|Proposed|Observed)\] (.+)$")
SOURCE = re.compile(r"\[source:([a-z0-9][a-z0-9.-]*)\]")
NORMATIVE = re.compile(r"\b(MUST(?: NOT)?|SHALL(?: NOT)?|SHOULD(?: NOT)?|MAY|REQUIRED|RECOMMENDED|OPTIONAL)\b")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def heading_slug(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9 -]", "", value.casefold()).replace(" ", "-")).strip("-")


def validate_links(body: str, path: Path) -> None:
    if re.search(r"https?://", body, flags=re.IGNORECASE):
        raise lib.ContractError(f"{path}: inline external addresses are forbidden; use source IDs")
    for raw in LINK.findall(body):
        target = raw.strip().strip("<>")
        relative, separator, fragment = target.partition("#")
        if "\\" in relative or Path(relative).is_absolute():
            raise lib.ContractError(f"{path}: unsafe or absolute Markdown link {raw!r}")
        resolved = path if not relative else (path.parent / relative)
        try:
            resolved.absolute().relative_to(lib.ROOT.absolute())
        except ValueError as error:
            raise lib.ContractError(f"{path}: Markdown link escapes repository root") from error
        if resolved.is_symlink() or not resolved.is_file():
            raise lib.ContractError(f"{path}: Markdown link target is missing or unsafe: {raw!r}")
        if separator:
            headings = {
                heading_slug(line.lstrip("#").strip())
                for line in resolved.read_text(encoding="utf-8").splitlines()
                if line.startswith("#")
            }
            if fragment not in headings:
                raise lib.ContractError(f"{path}: unresolved Markdown fragment {fragment!r}")


def parse_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise lib.ContractError(f"{path}: missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise lib.ContractError(f"{path}: unterminated YAML frontmatter") from error
    metadata: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.*?)\s*", line)
        if not match:
            raise lib.ContractError(f"{path}:{number}: frontmatter values must be scalar")
        key, value = match.groups()
        if key in metadata:
            raise lib.ContractError(f"{path}:{number}: duplicate frontmatter key {key}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        metadata[key] = value
    if set(metadata) != KEYS:
        missing = KEYS - metadata.keys(); extra = metadata.keys() - KEYS
        detail = []
        if missing: detail.append("missing " + ", ".join(sorted(missing)))
        if extra: detail.append("undeclared " + ", ".join(sorted(extra)))
        raise lib.ContractError(f"{path}: frontmatter has " + "; ".join(detail))
    return metadata, "\n".join(lines[end + 1:]) + "\n"


def validate_document(path: Path, *, expected_id: str | None = None) -> dict[str, str]:
    safe = lib.safe_existing_file(path, lib.ROOT, str(path))
    metadata, body = parse_frontmatter(safe.read_text(encoding="utf-8"), safe)
    if metadata["ngf_format"] != "normative-grounded-framework/1.0":
        raise lib.ContractError(f"{path}: unsupported ngf_format")
    if not DOCUMENT_ID.fullmatch(metadata["document_id"]):
        raise lib.ContractError(f"{path}: invalid document_id")
    if expected_id is not None and metadata["document_id"] != expected_id:
        raise lib.ContractError(f"{path}: document order/id mismatch, expected {expected_id}")
    if not metadata["title"]:
        raise lib.ContractError(f"{path}: title must not be empty")
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?", metadata["revision"]):
        raise lib.ContractError(f"{path}: revision must be semantic version")
    if metadata["status"] not in {"draft", "reviewed", "superseded", "retired"}:
        raise lib.ContractError(f"{path}: invalid status")
    if metadata["authority_class"] not in {"controlling-contract", "applied-framework", "methodology", "evidence"}:
        raise lib.ContractError(f"{path}: invalid authority_class")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", metadata["last_updated"]):
        raise lib.ContractError(f"{path}: last_updated must be ISO date")
    raw_manifest = metadata["source_manifest"]
    if not raw_manifest or "\\" in raw_manifest or Path(raw_manifest).is_absolute():
        raise lib.ContractError(f"{path}: source_manifest must be a safe relative POSIX path")
    manifest_path = safe.parent
    for part in raw_manifest.split("/"):
        if part in {"", "."}:
            raise lib.ContractError(f"{path}: source_manifest has an unsafe path segment")
        if part == "..":
            manifest_path = manifest_path.parent
        else:
            manifest_path = manifest_path / part
            if manifest_path.is_symlink():
                raise lib.ContractError(f"{path}: source_manifest must not traverse a symlink")
        try:
            manifest_path.absolute().relative_to(lib.ROOT.absolute())
        except ValueError as error:
            raise lib.ContractError(f"{path}: source_manifest escapes repository root") from error
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise lib.ContractError(f"{path}: source_manifest must name a regular non-symlink file")
    ledger = lib.read_json(manifest_path, root=lib.ROOT)
    schema = ledger.get("schema")
    if schema == "ngf-source-ledger/1.0":
        lib.validate_ngf_source_ledger(ledger)
    elif schema == "kg-rag-source-ledger/1.0":
        lib.validate_source_ledger(ledger)
    else:
        raise lib.ContractError(f"{path}: unsupported source ledger schema {schema!r}")
    source_ids = {item["id"] for item in ledger["sources"]}
    referenced = set(SOURCE.findall(body))
    missing_sources = referenced - source_ids
    if missing_sources:
        raise lib.ContractError(f"{path}: unresolved sources: {', '.join(sorted(missing_sources))}")
    validate_links(body, safe)
    headings: list[tuple[int, str, str]] = []
    current_class: str | None = None
    has_proof_limits = False
    has_change_history = False
    in_fence = False
    for number, line in enumerate(body.splitlines(), 1):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            match = H2.fullmatch(line)
            if not match:
                raise lib.ContractError(f"{path}: every H2 must have a recognized classification: {line}")
            current_class, title = match.groups()
            headings.append((number, current_class, title))
            has_proof_limits |= current_class == "Normative" and title.strip().casefold() == "proof limits"
            has_change_history |= current_class == "Observed" and title.strip().casefold() == "change history"
            continue
        if current_class != "Normative" and NORMATIVE.search(line):
            raise lib.ContractError(f"{path}: normative keyword outside a Normative H2 section")
    if not headings:
        raise lib.ContractError(f"{path}: requires classified H2 sections")
    if not has_proof_limits:
        raise lib.ContractError(f"{path}: missing required '## [Normative] Proof limits' section")
    if not has_change_history:
        raise lib.ContractError(f"{path}: missing required '## [Observed] Change history' section")
    return metadata


def check(directory: Path) -> list[Path]:
    root = directory.absolute()
    try:
        root.relative_to(lib.ROOT.absolute())
    except ValueError as error:
        raise lib.ContractError("NGF directory escapes repository root") from error
    if root.is_symlink() or not root.is_dir():
        raise lib.ContractError("NGF target must be a non-symlink directory")
    paths = sorted(root.glob("*.ngf.md"))
    if len(paths) != 6:
        raise lib.ContractError(f"expected exactly six NGF documents, found {len(paths)}")
    ids: list[str] = []
    for index, path in enumerate(paths):
        ids.append(validate_document(path, expected_id=f"kg-rag-0{index}")["document_id"])
    if len(set(ids)) != len(ids):
        raise lib.ContractError("NGF document_id values must be unique")
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", metavar="DIRECTORY", type=Path)
    mode.add_argument("--document", metavar="FILE", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.check is not None:
            paths = check(args.check)
            message = f"validated {len(paths)} NGF documents"
        else:
            validate_document(args.document)
            message = f"validated NGF document: {args.document}"
    except (OSError, UnicodeError, lib.ContractError) as error:
        print(f"NGF validation failed: {error}", file=sys.stderr)
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
