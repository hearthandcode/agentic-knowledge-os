from __future__ import annotations

import json
from copy import deepcopy
import unittest

from pathlib import Path

from agentic_knowledge_os import (
    build_plan,
    compile_bundle,
    core8_profiles,
    operating_policy,
    type_kernel,
    validate_brain,
    validate_plan,
)


class Core8Tests(unittest.TestCase):
    def test_distribution_has_exactly_eight_unique_profiles(self) -> None:
        profiles = core8_profiles()
        self.assertEqual(len(profiles), 8)
        self.assertEqual(len({profile["id"] for profile in profiles}), 8)
        self.assertTrue(all(profile["default_enabled"] is False for profile in profiles))
        self.assertTrue(all(profile["authority_class"] == "advisory-template" for profile in profiles))
        self.assertTrue(all(profile["transformation"]["domain"] for profile in profiles))
        self.assertTrue(all(profile["transformation"]["codomain"] for profile in profiles))

    def test_profile_types_and_handoffs_are_closed(self) -> None:
        profiles = core8_profiles()
        profile_ids = {profile["id"] for profile in profiles}
        type_ids = {item["id"] for item in type_kernel()["types"]}
        for profile in profiles:
            referenced = set((*profile["transformation"]["domain"], *profile["transformation"]["codomain"]))
            self.assertLessEqual(referenced, type_ids)
            self.assertLessEqual(set(profile["handoff_to"]), profile_ids - {profile["id"]})

    def test_operating_policy_separates_layers_and_gates(self) -> None:
        policy = operating_policy()
        self.assertEqual(
            [layer["id"] for layer in policy["operational_intelligence"]["layers"]],
            ["L1", "L2", "L3"],
        )
        self.assertIsNone(policy["semantic_orientation"]["canonical_meaning_default"])
        self.assertEqual(len(policy["governance"]["independent_gates"]), 6)

    def test_plan_is_deterministic_and_runtime_effects_are_held(self) -> None:
        first = build_plan(name="Example Brain", workspace="/workspace/example", host="hermes")
        second = build_plan(name="Example Brain", workspace="/workspace/example", host="hermes")
        self.assertEqual(first, second)
        self.assertEqual(first["effects"]["workspace_write"], "exact-plan-confirmation-required")
        self.assertEqual(first["effects"]["installation"], "manifest-owned-local-only")
        self.assertTrue(all(first["effects"][key] == "held" for key in ("enablement", "configuration", "provider_use", "network_use", "publication")))
        self.assertEqual(first["control_files"], [".akos/install-manifest.json"])
        self.assertEqual(validate_plan(first), first)

    def test_tampered_plan_is_rejected_before_render(self) -> None:
        plan = build_plan(name="Original Brain", workspace="/workspace/original", host="neutral")
        tampered = deepcopy(plan)
        tampered["brain"]["name"] = "Changed After Review"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            compile_bundle(tampered)

    def test_hermes_bundle_uses_agents_without_hermes_md(self) -> None:
        plan = build_plan(name="Hermes Brain", workspace="/workspace/hermes", host="hermes")
        bundle = compile_bundle(plan)
        self.assertIn("AGENTS.md", bundle)
        self.assertEqual(len([path for path in bundle if path.startswith(".akos/profiles/")]), 8)
        self.assertFalse(any(path.endswith(".hermes.md") for path in bundle))
        self.assertIn("Hermes Brain", bundle["AGENTS.md"])
        self.assertIn("## Transformation contract", bundle[".akos/profiles/coordinator.md"])
        self.assertIn("## Return contract", bundle[".akos/profiles/coordinator.md"])
        self.assertIn("First-run orientation", bundle[".akos/ORIENTATION.md"])
        self.assertIn(".akos/type-kernel.json", bundle)
        self.assertIn(".akos/operating-policy.json", bundle)

    def test_pi_projection_is_contract_only(self) -> None:
        plan = build_plan(name="Pi Brain", workspace="/workspace/pi", host="pi")
        self.assertEqual(plan["adapter"]["status"], "contract-only-live-untested")
        self.assertEqual(plan["adapter"]["runtime_effect"], "held")

    def test_exocore_projection_remains_held(self) -> None:
        plan = build_plan(name="Exocore Brain", workspace="/workspace/exocore", host="exocore")
        self.assertEqual(plan["adapter"]["status"], "held-interface")

    def test_profile_subset_preserves_registry_order(self) -> None:
        selected = ["akos.core8.reviewer", "akos.core8.coordinator"]
        plan = build_plan(
            name="Review Brain",
            workspace="/workspace/review",
            selected_profiles=selected,
        )
        self.assertEqual(plan["brain"]["profiles"], ["akos.core8.coordinator", "akos.core8.reviewer"])
        projected = json.loads(compile_bundle(plan)[".akos/core8.json"])
        self.assertEqual([profile["id"] for profile in projected["profiles"]], plan["brain"]["profiles"])

    def test_unknown_profile_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown Core8 profile"):
            build_plan(
                name="Invalid Brain",
                workspace="/workspace/invalid",
                selected_profiles=["akos.core8.unknown"],
            )

    def test_relative_and_root_workspace_targets_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "absolute path"):
            build_plan(name="Relative", workspace="relative/path")
        with self.assertRaisesRegex(ValueError, "filesystem root"):
            build_plan(name="Root", workspace="/")

    def test_valid_and_invalid_brain_fixtures(self) -> None:
        root = Path(__file__).resolve().parents[1]
        valid = json.loads((root / "fixtures/valid/brain.json").read_text(encoding="utf-8"))
        invalid = json.loads((root / "fixtures/invalid/unknown-profile.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_brain(valid), valid)
        with self.assertRaisesRegex(ValueError, "unknown Core8 profile"):
            validate_brain(invalid)


if __name__ == "__main__":
    unittest.main()
