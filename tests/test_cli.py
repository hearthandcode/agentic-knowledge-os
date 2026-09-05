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
    def test_compact_artifact_commands(self) -> None:
        fixtures = Path(__file__).resolve().parents[1] / 'fixtures/evaluation'
        request = str(fixtures / 'compact-artifact-request.json')
        compiled = self._run('artifact-prompt', '--request', request)
        self.assertLess(compiled['kernel_characters'], 3000)
        invalid = str(fixtures / 'compact-artifact-invalid.json')
        valid = str(fixtures / 'compact-artifact-valid.json')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['artifact-check', '--request', request, '--response', invalid])
        self.assertEqual(code, 2)
        rejected = json.loads(output.getvalue())
        self.assertIsNone(rejected['artifact_candidate'])
        self.assertEqual(rejected['attempts'][0]['checks_applied'], [])
        repaired = self._run('artifact-check', '--request', request,
                             '--response', invalid, '--response', valid)
        self.assertFalse(repaired['first_attempt_passed'])
        self.assertEqual(len(repaired['attempts'][1]['checks_applied']), 4)

    def test_benchmark_commands(self) -> None:
        suite = self._run("benchmark-suite")
        self.assertEqual(len(suite["cases"]), 8)
        receipt = self._run(
            "benchmark-score",
            "--traces",
            str(Path(__file__).resolve().parents[1] / "fixtures/evaluation/conformant-traces.json"),
        )
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["effectiveness"]["status"], "not-measured")
        audit = self._run(
            "benchmark-audit",
            "--traces",
            str(Path(__file__).resolve().parents[1] / "fixtures/evaluation/conformant-traces.json"),
        )
        self.assertEqual(audit["detection_score"], 1.0)

    def test_behavioral_experiment_commands(self) -> None:
        plan = self._run("experiment-plan")
        self.assertEqual(plan["candidate_condition"], "akos")
        rubric = self._run("experiment-rubric")
        self.assertEqual(rubric["aggregation"], "single-conjunctive-primary-endpoint-with-disaggregated-secondary-metrics")
        receipt = self._run("experiment-canary")
        self.assertEqual(receipt["status"], "canary-only")
        self.assertEqual(receipt["scoring_model"]["composite_score"], "prohibited")

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

    def test_host_package_plan_render_apply_and_verify_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "hermes-package"
            plan = self._run(
                "package-plan",
                "--name",
                "CLI Host Package",
                "--output",
                str(target),
                "--host",
                "hermes",
            )
            rendered = self._run(
                "package-render",
                "--name",
                "CLI Host Package",
                "--output",
                str(target),
                "--host",
                "hermes",
            )
            self.assertEqual(rendered["plan"], plan)
            self.assertIn("plugin.json", rendered["files"])
            plan_file = parent / "package-plan.json"
            plan_file.write_text(json.dumps(plan) + "\n", encoding="utf-8")
            applied = self._run(
                "package-apply",
                "--plan-file",
                str(plan_file),
                "--confirm-package",
                plan["package_id"],
            )
            self.assertEqual(applied["status"], "written")
            verified = self._run("package-verify", "--package-root", str(target))
            self.assertEqual(verified["status"], "clear")


if __name__ == "__main__":
    unittest.main()
