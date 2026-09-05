from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from agentic_knowledge_os import build_plan
from agentic_knowledge_os.cli import main


class CliTests(unittest.TestCase):
    def test_policy_types_and_orientation_commands_are_read_only(self) -> None:
        policy = self._run("policy")
        self.assertEqual(policy["schema"], "akos.operating-policy.v1")
        kernel = self._run("types")
        self.assertEqual(kernel["schema"], "akos.type-kernel.v1")
        oriented = self._run(
            "orient",
            "--name",
            "CLI Orientation",
            "--workspace",
            "/workspace/cli-orientation",
        )
        self.assertEqual(oriented["plan"]["schema"], "akos.bootstrap-plan.v2")
        self.assertIn("Orientation questions", oriented["orientation"])

    def _run(self, *arguments: str) -> dict:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(list(arguments))
        self.assertEqual(result, 0)
        return json.loads(output.getvalue())

    def test_profiles_command(self) -> None:
        profiles = self._run("profiles")
        self.assertEqual(len(profiles), 8)

    def test_plan_command(self) -> None:
        plan = self._run("plan", "--name", "CLI Brain", "--workspace", "/workspace/cli", "--host", "hermes")
        self.assertEqual(plan["brain"]["host"], "hermes")
        self.assertEqual(plan["effects"]["workspace_write"], "exact-plan-confirmation-required")

    def test_render_command_does_not_claim_application(self) -> None:
        result = self._run("render", "--name", "Rendered Brain", "--workspace", "/workspace/rendered")
        self.assertEqual(set(result), {"files", "plan"})
        self.assertNotIn("applied", result)

    def test_apply_and_verify_commands_return_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = build_plan(name="CLI Extended Mind", workspace=str(parent / "mind"), host="pi")
            plan_file = parent / "plan.json"
            plan_file.write_text(json.dumps(plan) + "\n", encoding="utf-8")
            applied = self._run(
                "apply",
                "--plan-file",
                str(plan_file),
                "--confirm-plan",
                plan["plan_id"],
            )
            self.assertEqual(applied["status"], "applied")
            verified = self._run("verify", "--workspace", str(parent / "mind"))
            self.assertEqual(verified["status"], "clear")


if __name__ == "__main__":
    unittest.main()
