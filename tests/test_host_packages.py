"""Host-native Hermes and Pi package projection tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from agentic_knowledge_os.host_packages import (
    build_host_package_plan,
    compile_host_package,
    validate_host_package_plan,
    verify_host_package,
    write_host_package,
)


class HostPackageTests(unittest.TestCase):
    def test_hermes_package_uses_agent_plugins_v1_without_akos_paths(self) -> None:
        plan = build_host_package_plan(
            name="Hermes Extended Mind",
            output_root="/packages/hermes",
            host="hermes",
        )
        bundle = compile_host_package(plan)
        manifest = json.loads(bundle["plugin.json"])
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(manifest["name"], "agentic-knowledge-os")
        self.assertIn("skills/agentic-knowledge-os/SKILL.md", bundle)
        self.assertIn('version: "0.3.0-alpha.1"', bundle["skills/agentic-knowledge-os/SKILL.md"])
        self.assertNotIn("package.json", bundle)
        self.assertFalse(any(path.startswith(".akos") or "/.akos" in path for path in bundle))
        self.assertIn("host_installation", json.loads(bundle["package-manifest.json"]))

    def test_pi_package_declares_skill_and_prompt(self) -> None:
        plan = build_host_package_plan(
            name="Pi Extended Mind",
            output_root="/packages/pi",
            host="pi",
        )
        bundle = compile_host_package(plan)
        manifest = json.loads(bundle["package.json"])
        self.assertEqual(manifest["pi"]["skills"], ["./skills"])
        self.assertEqual(manifest["pi"]["prompts"], ["./prompts"])
        self.assertIn("prompts/orient-extended-mind.md", bundle)
        self.assertNotIn("plugin.json", bundle)
        self.assertFalse(any(path.startswith(".akos") or "/.akos" in path for path in bundle))

    def test_package_plan_is_deterministic_and_tamper_evident(self) -> None:
        plan = build_host_package_plan(name="Stable", output_root="/packages/stable", host="hermes")
        self.assertEqual(plan, build_host_package_plan(name="Stable", output_root="/packages/stable", host="hermes"))
        self.assertEqual(validate_host_package_plan(plan), plan)
        tampered = deepcopy(plan)
        tampered["host"] = "pi"
        with self.assertRaisesRegex(ValueError, "changed"):
            validate_host_package_plan(tampered)

    def test_write_requires_confirmation_and_empty_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "hermes"
            plan = build_host_package_plan(name="Review", output_root=str(target), host="hermes")
            blocked = write_host_package(plan, "sha256:wrong")
            self.assertEqual(blocked["status"], "blocked")
            self.assertFalse(target.exists())

            written = write_host_package(plan, plan["package_id"])
            self.assertEqual(written["status"], "written")
            self.assertEqual(verify_host_package(target)["status"], "clear")

            foreign = Path(temporary) / "foreign"
            foreign.mkdir()
            (foreign / "user.txt").write_text("keep\n", encoding="utf-8")
            foreign_plan = build_host_package_plan(name="Foreign", output_root=str(foreign), host="pi")
            refused = write_host_package(foreign_plan, foreign_plan["package_id"])
            self.assertEqual(refused["status"], "blocked")
            self.assertEqual((foreign / "user.txt").read_text(encoding="utf-8"), "keep\n")

    def test_verifier_detects_owned_file_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "pi"
            plan = build_host_package_plan(name="Drift", output_root=str(target), host="pi")
            self.assertEqual(write_host_package(plan, plan["package_id"])["status"], "written")
            (target / "package.json").write_text("{}\n", encoding="utf-8")
            verification = verify_host_package(target)
            self.assertEqual(verification["status"], "blocked")
            self.assertIn("owned file digest mismatch: package.json", verification["findings"])


if __name__ == "__main__":
    unittest.main()
