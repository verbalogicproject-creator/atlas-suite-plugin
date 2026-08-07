from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FRAMEWORK = ROOT.parent / "deterministic-kg-rag-framework"


class PluginTests(unittest.TestCase):
    @staticmethod
    def _environment() -> dict[str, str]:
        return {**os.environ, "PYTHONPATH": str(FRAMEWORK / "src"), "DKG_FRAMEWORK_ROOT": str(FRAMEWORK)}

    @staticmethod
    def _make_source(root: Path) -> None:
        (root / "src" / "demo").mkdir(parents=True)
        (root / "src" / "demo" / "__init__.py").write_text("from .core import value\n", encoding="utf-8")
        (root / "src" / "demo" / "core.py").write_text("value = 1\n", encoding="utf-8")
        (root / "docs").mkdir()
        (root / "docs" / "architecture.md").write_text("# Architecture\n\n## Writer boundary\n", encoding="utf-8")
        (root / "config").mkdir()
        (root / "config" / "source-ledger.json").write_text('{"schema":"dkg-source-ledger/1.0","sources":[]}\n', encoding="utf-8")

    def test_manifest_and_seven_skills_are_closed(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "atlas-suite-plugin")
        self.assertEqual(manifest["version"], "1.0.0")
        skills = sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(
            skills,
            [
                "atlas-frontend-designer",
                "context-atlas",
                "evidence-rules-atlas",
                "kg-rag-specialist",
                "knowledge-atlas",
                "project-atlas",
                "topology-atlas",
            ],
        )
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            self.assertNotIn("TODO", path.read_text(encoding="utf-8"))

    def test_direct_and_bridge_plans_are_byte_identical(self) -> None:
        environment = self._environment()
        cases = [
            *[("--flags", value) for value in ("project", "context", "knowledge", "topology", "evidence-rules")],
            *[("--preset", value) for value in ("repo-orientation", "implementation", "kg-rag", "release-review")],
            ("--flags", "project,topology"),
            ("--flags", "topology,project"),
            ("--flags", "context,topology,evidence-rules"),
            ("--flags", "evidence-rules,topology,context"),
        ]
        self.assertEqual(len(cases), 13)
        for selector, value in cases:
            with self.subTest(selector=selector, value=value):
                direct = subprocess.run([sys.executable, "-m", "dkg", "atlas", "plan", selector, value], env=environment, check=True, capture_output=True).stdout
                bridge = subprocess.run([sys.executable, str(ROOT / "scripts" / "dkg_bridge.py"), "atlas", "plan", selector, value], env=environment, check=True, capture_output=True).stdout
                self.assertEqual(direct, bridge)

    def test_nine_stateful_direct_and_bridge_runs_and_boots_are_identical(self) -> None:
        environment = self._environment()
        cases = [
            *[("--flags", value) for value in ("project", "context", "knowledge", "topology", "evidence-rules")],
            *[("--preset", value) for value in ("repo-orientation", "implementation", "kg-rag", "release-review")],
        ]
        self.assertEqual(len(cases), 9)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            self._make_source(source)
            for index, (selector, value) in enumerate(cases):
                with self.subTest(selector=selector, value=value):
                    direct_state = root / f"direct-{index}"
                    bridge_state = root / f"bridge-{index}"
                    direct_run = subprocess.run([sys.executable, "-m", "dkg", "atlas", "run", selector, value, "--source", str(source), "--state-root", str(direct_state)], env=environment, check=True, capture_output=True).stdout
                    bridge_run = subprocess.run([sys.executable, str(ROOT / "scripts" / "dkg_bridge.py"), "atlas", "run", selector, value, "--source", str(source), "--state-root", str(bridge_state)], env=environment, check=True, capture_output=True).stdout
                    self.assertEqual(direct_run, bridge_run)
                    direct_boot = subprocess.run([sys.executable, "-m", "dkg", "boot", "--state-root", str(direct_state)], env=environment, check=True, capture_output=True).stdout
                    bridge_boot = subprocess.run([sys.executable, str(ROOT / "scripts" / "dkg_bridge.py"), "boot", "--state-root", str(bridge_state)], env=environment, check=True, capture_output=True).stdout
                    self.assertEqual(direct_boot, bridge_boot)

    def test_bridge_missing_framework_fails_closed(self) -> None:
        environment = {**os.environ, "DKG_FRAMEWORK_ROOT": str(ROOT / "missing-framework")}
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "dkg_bridge.py"), "atlas", "plan", "--flags", "project"], env=environment, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("paired deterministic-kg-rag-framework was not found", result.stderr)

    def test_bridge_rejects_incompatible_framework_before_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            framework = Path(temporary)
            package = framework / "src" / "dkg"
            package.mkdir(parents=True)
            marker = framework / "imported"
            (package / "cli.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('imported')\n", encoding="utf-8")
            (framework / "pyproject.toml").write_text('[project]\nname = "deterministic-kg-rag-framework"\nversion = "2.0.0"\n', encoding="utf-8")
            environment = {**os.environ, "DKG_FRAMEWORK_ROOT": str(framework)}
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "dkg_bridge.py"), "atlas", "plan", "--flags", "project"], env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("framework must be deterministic-kg-rag-framework 1.x", result.stderr)
            self.assertFalse(marker.exists())

    def test_baseline_identity_and_kb_validator(self) -> None:
        baseline = json.loads((ROOT / "skills" / "kg-rag-specialist" / "references" / "baseline-manifest.json").read_text())
        self.assertEqual(baseline["file_count_excluding_pycache"], 63)
        result = subprocess.run([sys.executable, str(ROOT / "skills" / "kg-rag-specialist" / "scripts" / "validate_deterministic_kb.py")], check=True, capture_output=True, text=True)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["baseline_tree"], {"file_count": 63, "canonical_tree_sha256": baseline["canonical_tree_sha256"], "status": "verified"})

    def test_no_marketplace_or_runtime_artifacts(self) -> None:
        relative_paths = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()]
        self.assertFalse(any("marketplace" in path.casefold() for path in relative_paths))
        forbidden_suffixes = {".db", ".sqlite", ".gguf", ".env"}
        self.assertFalse(any(Path(path).suffix.casefold() in forbidden_suffixes for path in relative_paths))


if __name__ == "__main__":
    unittest.main()
