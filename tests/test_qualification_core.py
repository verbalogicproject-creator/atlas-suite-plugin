from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("qualification_core", ROOT / "scripts" / "qualification_core.py")
assert SPEC and SPEC.loader
qc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qc)


class QualificationCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = qc.validate_registry(qc.load_json(ROOT / "qualification" / "capability-registry.json"))

    def profile(self, identifier: str = "ai-tool-control-plane") -> dict:
        return qc.load_json(ROOT / "qualification" / "profiles" / f"{identifier}.atlas-profile.json")

    def test_contract_artifacts_are_closed_and_canonical(self) -> None:
        paths = [ROOT / "qualification" / "capability-registry.json"]
        paths += sorted((ROOT / "qualification" / "profiles").glob("*.json"))
        paths += sorted((ROOT / "qualification" / "proof-plans").glob("*.json"))
        paths += sorted((ROOT / "qualification" / "receipts").rglob("*.json"))
        paths += sorted((ROOT / "qualification" / "verifications").glob("*.json"))
        for path in paths:
            value = qc.load_json(path)
            self.assertEqual(path.read_bytes(), qc.canonical_bytes(value), path)
        for path in (ROOT / "qualification" / "schemas").glob("*.json"):
            schema = qc.load_json(path)
            self.assertFalse(schema["additionalProperties"], path)

    def test_duplicate_keys_unknown_keys_and_enums_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"schema":"x","schema":"y"}\n', encoding="utf-8")
            with self.assertRaisesRegex(qc.QualificationError, "duplicate JSON key"):
                qc.load_json(path)
        unknown = copy.deepcopy(self.registry)
        unknown["surprise"] = True
        with self.assertRaisesRegex(qc.QualificationError, "unknown=.*surprise"):
            qc.validate_registry(unknown)
        enum = copy.deepcopy(self.registry)
        enum["claims"][0]["standing"] = "nearly-proven"
        with self.assertRaisesRegex(qc.QualificationError, "unknown standing"):
            qc.validate_registry(enum)

    def test_initial_registry_profiles_and_proof_plans_validate(self) -> None:
        listed = qc.list_profiles(ROOT)
        self.assertEqual([item["id"] for item in listed["profiles"]], ["ai-tool-control-plane", "fullstack-contract-spine", "rag-evidence-firewall"])
        for item in listed["profiles"]:
            profile = qc.validate_profile(self.profile(item["id"]), self.registry)
            plan = qc.profile_qualification(item["id"], ROOT)["proof_plan"]
            self.assertEqual(plan["profile_id"], profile["id"])
            self.assertTrue(plan["falsifying_cases"])

    def test_describe_is_byte_identical_and_exposes_effects_gates_and_limits(self) -> None:
        first = qc.canonical_bytes(qc.describe_profile("ai-tool-control-plane", ROOT))
        second = qc.canonical_bytes(qc.describe_profile("ai-tool-control-plane", ROOT))
        self.assertEqual(first, second)
        description = json.loads(first)
        profile = description["profile"]
        self.assertEqual({item["id"] for item in profile["effects"]}, qc.EFFECTS)
        self.assertEqual({item["kind"] for item in profile["gates"]}, qc.GATE_KINDS)
        self.assertTrue(profile["proof_limits"])
        self.assertEqual(profile["qualification"]["receipt_refs"], description["available_receipt_refs"])
        self.assertEqual(description["available_receipt_refs"], ["qualification/receipts/candidates/ai-tool-control-plane.receipt.json"])

    def test_unknown_and_incompatible_profile_references_fail(self) -> None:
        unknown = self.profile()
        unknown["components"][0]["id"] = "atlas.not-registered"
        with self.assertRaisesRegex(qc.QualificationError, "unknown component"):
            qc.validate_profile(unknown, self.registry)
        incompatible_registry = copy.deepcopy(self.registry)
        incompatible_registry["claims"][0]["incompatible_with"] = ["codex.acting-host"]
        qc.validate_registry(incompatible_registry)
        with self.assertRaisesRegex(qc.QualificationError, "incompatible components"):
            qc.validate_profile(self.profile(), incompatible_registry)

    def test_context_cannot_populate_authority(self) -> None:
        profile = self.profile()
        authority = next(item for item in profile["inputs"] if item["kind"] == "authority")
        authority["source"] = "repository"
        with self.assertRaisesRegex(qc.QualificationError, "cannot populate authority"):
            qc.validate_profile(profile, self.registry)
        profile = self.profile()
        gate = next(item for item in profile["gates"] if item["kind"] == "authority")
        gate["input"] = "repository_roots"
        with self.assertRaisesRegex(qc.QualificationError, "context cannot populate"):
            qc.validate_profile(profile, self.registry)

    def test_receipt_digest_and_promotion_fail_closed(self) -> None:
        receipt = qc.load_json(ROOT / "qualification" / "receipts" / "candidates" / "fullstack-contract-spine.receipt.json")
        verification = qc.load_json(ROOT / "qualification" / "verifications" / "fullstack-contract-spine.verification.json")
        registry_sha = qc.digest(self.registry)
        profile = qc.validate_profile(self.profile("fullstack-contract-spine"), self.registry)
        profile_sha = qc.digest(profile)
        bindings = qc.build_current_bindings("fullstack-contract-spine", profile, self.registry, ROOT)
        self.assertTrue(qc.receipt_can_promote(receipt, registry_sha256=registry_sha, profile_sha256=profile_sha, verification_record=verification, expected_bindings=bindings))
        self.assertFalse(qc.receipt_can_promote(receipt, registry_sha256=registry_sha, profile_sha256=profile_sha))
        tampered = copy.deepcopy(receipt)
        tampered["bindings"]["result"]["sha256"] = "b" * 64
        with self.assertRaisesRegex(qc.QualificationError, "receipt_sha256 mismatch"):
            qc.validate_receipt(tampered)
        with self.assertRaisesRegex(qc.QualificationError, "registry digest is stale"):
            qc.receipt_can_promote(receipt, registry_sha256="b" * 64, profile_sha256=profile_sha, verification_record=verification)
        self_attested = copy.deepcopy(verification)
        self_attested["verifier"] = self_attested["producer"]
        self_attested["verifier_sha256"] = self_attested["producer_sha256"]
        unsigned = dict(self_attested); unsigned.pop("verification_sha256")
        self_attested["verification_sha256"] = qc.digest(unsigned)
        with self.assertRaisesRegex(qc.QualificationError, "producer-only"):
            qc.validate_verification_record(self_attested)

    def test_itl_contracts_resolve_from_installed_plugin_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary) / "cache"
            base = cache / "atlas-suite-local" / "atlas-suite-plugin" / "1.1.0"
            installed = cache / "in-the-loop-local" / "in-the-loop" / "0.4.1"
            expected = {
                "roster": installed / "skills" / "kg-rag-specialist" / "references" / "binding" / "roster.json",
                "linter": installed / "skills" / "run-itl-workflow" / "scripts" / "lint_itl.py",
                "locker": installed / "skills" / "run-itl-workflow" / "scripts" / "workflow_lock.py",
                "core": installed / "skills" / "in-the-loop" / "references" / "spec" / "core-contract.md",
                "orchestration": installed / "skills" / "in-the-loop" / "references" / "spec" / "orchestration-format.md",
            }
            for path in expected.values():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("frozen contract\n", encoding="utf-8")
            self.assertEqual(qc._itl_contract_paths(base), expected)

    def test_profile_operations_are_read_only(self) -> None:
        before = {path: path.read_bytes() for path in (ROOT / "qualification").rglob("*") if path.is_file()}
        plan = qc.plan_profile("fullstack-contract-spine", ROOT)
        qualification = qc.profile_qualification("rag-evidence-firewall", ROOT)
        after = {path: path.read_bytes() for path in (ROOT / "qualification").rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertFalse(plan["execution_authorized"])
        self.assertTrue(qualification["promotion_eligible"])
        self.assertEqual(qualification["operation"], "read-only")


if __name__ == "__main__":
    unittest.main()
