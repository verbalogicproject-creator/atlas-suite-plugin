#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT.parents[1]
KB = ROOT / "references" / "deterministic-rag-kb" / "v1"
BASELINE = ROOT / "references" / "kg-rag" / "workspace"
BASELINE_MANIFEST = ROOT / "references" / "baseline-manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((KB / name).read_text(encoding="utf-8"))


def baseline_tree() -> tuple[int, str]:
    entries = []
    roots = (
        (PLUGIN_ROOT / "vendor" / "kg-rag-specialist-baseline", PLUGIN_ROOT / "vendor" / "kg-rag-specialist-baseline"),
        (ROOT / "references" / "binding", ROOT),
        (ROOT / "references" / "kg-rag", ROOT),
        (ROOT / "scripts", ROOT),
    )
    for directory, relative_root in roots:
        for path in directory.rglob("*"):
            if (not path.is_file() or path.is_symlink() or "__pycache__" in path.parts
                    or path == Path(__file__).resolve()):
                continue
            entries.append({"path": path.relative_to(relative_root).as_posix(), "sha256": sha(path)})
    entries.sort(key=lambda item: item["path"])
    canonical = (json.dumps(entries, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return len(entries), hashlib.sha256(canonical).hexdigest()


def main() -> int:
    failures: list[str] = []
    baseline_manifest = json.loads(BASELINE_MANIFEST.read_text(encoding="utf-8"))
    baseline_count, baseline_sha = baseline_tree()
    if baseline_count != baseline_manifest.get("file_count_excluding_pycache"):
        failures.append("baseline-tree-file-count")
    if baseline_sha != baseline_manifest.get("canonical_tree_sha256"):
        failures.append("baseline-tree-digest")
    cookbook = BASELINE / "spec" / "kg-rag-cookbook.md"
    registry_path = BASELINE / "kg-rag" / "recipe-registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if sha(cookbook) != "2015bc3f30acfb6665745ab9d2598d24c590b00f465d33298ac0508331aca308":
        failures.append("baseline-cookbook-digest")
    if sha(registry_path) != "eec6c909651b6011ac78b594d36fce03044607667274436d2fcde280a900e223":
        failures.append("baseline-registry-digest")
    if len(registry.get("recipes", [])) != 18:
        failures.append("baseline-recipe-count")
    claims = load("claims.json")
    source_ids = {item["id"] for item in claims.get("sources", [])}
    if not claims.get("claims") or any(not set(item.get("source_ids", [])) <= source_ids for item in claims.get("claims", [])):
        failures.append("claim-source-resolution")
    candidates = load("candidate-recipes.json")
    if candidates.get("controlling_recipe_count") != 18 or candidates.get("activation") != "forbidden-until-cookbook-schema-revision":
        failures.append("candidate-recipe-boundary")
    profiles = load("platform-profiles.json")
    if any(item.get("network") not in {"forbidden", "loopback-only", "human-served-loopback-8143", "fresh-digest-bound-approval"} for item in profiles.get("profiles", [])):
        failures.append("profile-network-boundary")
    cases = load("adversarial-cases.json")
    if len(cases.get("cases", [])) < 16:
        failures.append("adversarial-coverage")
    boot = load("harness-boot.receipt.json")
    if boot.get("qualification_scope") != "blueprint" or boot.get("verdict") != "ready":
        failures.append("boot-scope")
    receipt = {
        "schema": "atlas-suite-kb-validation/1.0",
        "release_id": claims.get("release_id"),
        "baseline_tree": {"file_count": baseline_count, "canonical_tree_sha256": baseline_sha, "status": "verified" if not {"baseline-tree-file-count", "baseline-tree-digest"} & set(failures) else "failed"},
        "artifacts": {name: sha(KB / name) for name in sorted(("claims.json", "candidate-recipes.json", "platform-profiles.json", "adversarial-cases.json", "harness-boot.receipt.json", "index.md"))},
        "failures": sorted(failures),
        "status": "passed" if not failures else "failed",
        "proof_limit": "Static blueprint and baseline-integrity validation only.",
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
