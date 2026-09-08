from __future__ import annotations

import sys
import copy
import json
import os
import subprocess
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import qualification_core as qc
from qualification_core import build_current_bindings, digest, load_json, receipt_can_promote, validate_profile, validate_registry
from qualification_receipts import generate


class QualificationReceiptTests(unittest.TestCase):
    def test_replays_are_repeatable_and_promotion_is_fail_closed(self) -> None:
        first = generate()
        second = generate()
        self.assertEqual(first, second)
        for observation in first["observations"].values():
            unsigned = dict(observation)
            observed = unsigned.pop("result_sha256")
            self.assertEqual(digest(unsigned), observed)
        registry = validate_registry(load_json(ROOT / "qualification" / "capability-registry.json"))
        for profile_id, receipt in first["receipts"].items():
            profile = validate_profile(load_json(ROOT / "qualification" / "profiles" / f"{profile_id}.atlas-profile.json"), registry)
            bindings = build_current_bindings(profile_id, profile, registry, ROOT, first["observations"][profile_id])
            promotable = receipt_can_promote(receipt, registry_sha256=digest(registry), profile_sha256=digest(profile), verification_record=first["verifications"][profile_id], expected_bindings=bindings)
            self.assertEqual(promotable, profile_id in {"fullstack-contract-spine", "rag-evidence-firewall"})

    def test_ai_profile_remains_failed_without_runtime_closure(self) -> None:
        result = generate()
        observation = result["observations"]["ai-tool-control-plane"]
        receipt = result["receipts"]["ai-tool-control-plane"]
        self.assertIsNone(observation["runtime"])
        self.assertEqual(receipt["status"], "failed")
        self.assertTrue(receipt["independent_verification"])
        self.assertEqual(result["verifications"]["ai-tool-control-plane"]["outcome"], "verified-fail")
        if observation["failures"] == ["itl-qualification-contract-unavailable"]:
            self.assertEqual(observation["static_validation"]["status"], "failed")
        else:
            self.assertEqual(observation["static_validation"]["status"], "passed")
            self.assertIn("real-runtime-artifact-absent", receipt["failures"])

    def test_all_bound_drift_is_ineligible_and_itl_drift_is_reported_stale(self) -> None:
        replay = generate()
        registry = validate_registry(load_json(ROOT / "qualification" / "capability-registry.json"))
        profile = validate_profile(load_json(ROOT / "qualification" / "profiles" / "fullstack-contract-spine.atlas-profile.json"), registry)
        receipt = replay["receipts"]["fullstack-contract-spine"]
        verification = replay["verifications"]["fullstack-contract-spine"]
        current = build_current_bindings("fullstack-contract-spine", profile, registry, ROOT, replay["observations"]["fullstack-contract-spine"])
        for name in ("result", "source_manifest", "adapter_bindings", "environment"):
            drift = copy.deepcopy(current)
            drift[name]["sha256"] = "f" * 64
            self.assertFalse(receipt_can_promote(receipt, registry_sha256=digest(registry), profile_sha256=digest(profile), verification_record=verification, expected_bindings=drift), name)
        changed_verification = copy.deepcopy(verification)
        changed_verification["checks"][0]["detail"] = "changed verification record"
        unsigned = dict(changed_verification); unsigned.pop("verification_sha256")
        changed_verification["verification_sha256"] = digest(unsigned)
        self.assertFalse(receipt_can_promote(receipt, registry_sha256=digest(registry), profile_sha256=digest(profile), verification_record=changed_verification, expected_bindings=current))

        ai_profile = validate_profile(load_json(ROOT / "qualification" / "profiles" / "ai-tool-control-plane.atlas-profile.json"), registry)
        ai_current = build_current_bindings("ai-tool-control-plane", ai_profile, registry, ROOT)
        paths = {item["path"] for item in ai_current["source_manifest"]["files"]}
        itl_contracts = [
            item["contract"] for item in ai_current["adapter_bindings"]["items"]
            if item["adapter"].startswith("itl-") or item["adapter"] == "atlas-itl-grounding/1.0"
        ]
        available = all(item["qualification_contract_available"] for item in itl_contracts)
        self.assertEqual("dependency/in-the-loop/0.4.1/scripts/lint_itl.py" in paths, available)
        itl_drift = copy.deepcopy(ai_current)
        itl_drift["source_manifest"]["sha256"] = "e" * 64
        with mock.patch.object(qc, "build_current_bindings", return_value=itl_drift):
            status = qc.profile_qualification("ai-tool-control-plane", ROOT)
        self.assertEqual(status["status"], "stale")
        self.assertFalse(status["promotion_eligible"])

    def test_standalone_verifier_replays_and_rejects_tampered_semantics(self) -> None:
        verifier = ROOT / "scripts" / "qualification_verifier.py"
        result = load_json(ROOT / "qualification" / "results" / "fullstack-contract-spine.result.json")
        completed = subprocess.run([sys.executable, str(verifier), "fullstack-contract-spine"], input=qc.canonical_bytes(result), capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        record = json.loads(completed.stdout)
        self.assertEqual(record["outcome"], "verified-pass")
        self.assertEqual(next(item for item in record["checks"] if item["id"] == "independent-double-replay")["status"], "passed")

        tampered = copy.deepcopy(result)
        tampered["metrics"]["false_negatives"] = 0
        tampered["results"][1]["failure"]["detail"] = "valid-looking but forged semantic detail"
        unsigned = dict(tampered); unsigned.pop("result_sha256")
        tampered["result_sha256"] = digest(unsigned)
        rejected = subprocess.run([sys.executable, str(verifier), "fullstack-contract-spine"], input=qc.canonical_bytes(tampered), capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(rejected.returncode, 1, rejected.stderr.decode())
        rejected_record = json.loads(rejected.stdout)
        self.assertEqual(rejected_record["outcome"], "verified-fail")
        self.assertEqual(next(item for item in rejected_record["checks"] if item["id"] == "candidate-replay-match")["status"], "failed")


if __name__ == "__main__":
    unittest.main()
