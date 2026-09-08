from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "scripts" / "atlas"


class ProfileCliTests(unittest.TestCase):
    @staticmethod
    def run_profile(*arguments: str, check: bool = True, dkg_available: bool = False) -> subprocess.CompletedProcess[bytes]:
        environment = {
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        if not dkg_available:
            environment["DKG_FRAMEWORK_ROOT"] = "/definitely/unavailable-for-profile-discovery"
        return subprocess.run(
            [sys.executable, str(ATLAS), "profile", *arguments],
            env=environment,
            check=check,
            capture_output=True,
        )

    def test_profile_list_is_canonical_and_does_not_resolve_dkg(self) -> None:
        first = self.run_profile("list").stdout
        second = self.run_profile("list").stdout
        self.assertEqual(first, second)
        self.assertEqual(first, (json.dumps(json.loads(first), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode())
        self.assertEqual(
            [item["id"] for item in json.loads(first)["profiles"]],
            ["ai-tool-control-plane", "fullstack-contract-spine", "rag-evidence-firewall"],
        )

    def test_all_read_only_profile_routes_are_deterministic(self) -> None:
        for command in ("describe", "explain", "plan", "qualification"):
            with self.subTest(command=command):
                first = self.run_profile(command, "fullstack-contract-spine").stdout
                second = self.run_profile(command, "fullstack-contract-spine").stdout
                self.assertEqual(first, second)
                value = json.loads(first)
                self.assertEqual(value["operation"], "read-only")
                if command in {"explain", "plan"}:
                    self.assertFalse(value["execution_authorized"])
                if command == "plan":
                    self.assertEqual(value["status"], "blocked")
                    self.assertTrue(any(item["reason"] == "paired-dkg-contract-unavailable" for item in value["adapter_checks"]))
                if command == "qualification":
                    self.assertFalse(value["promotion_eligible"])
                    self.assertEqual(value["status"], "stale")
                    self.assertEqual(len(value["receipts"]), 1)

    def test_valid_separate_verification_is_required_for_eligibility(self) -> None:
        for profile_id in ("fullstack-contract-spine", "rag-evidence-firewall"):
            value = json.loads(self.run_profile("qualification", profile_id, dkg_available=True).stdout)
            self.assertTrue(value["promotion_eligible"])
            self.assertEqual(value["status"], "current")

    def test_unknown_profile_fails_closed(self) -> None:
        completed = self.run_profile("describe", "not-registered", check=False)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, b"")
        self.assertIn(b"missing or unsafe artifact", completed.stderr)

    def test_no_profile_execution_command_exists(self) -> None:
        completed = self.run_profile("run", "fullstack-contract-spine", check=False)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, b"")

    def test_verified_ai_receipt_is_visible_and_policy_eligible(self) -> None:
        value = json.loads(self.run_profile("qualification", "ai-tool-control-plane").stdout)
        self.assertTrue(value["promotion_eligible"])
        self.assertEqual(value["status"], "current")
        self.assertEqual(value["receipts"][0]["receipt"]["status"], "passed")
        self.assertEqual(value["receipts"][0]["receipt"]["failures"], [])
        self.assertEqual(value["operation"], "read-only")


if __name__ == "__main__":
    unittest.main()
