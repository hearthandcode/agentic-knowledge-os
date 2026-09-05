"""Provider-free governance benchmark and artifact identity ledger tests."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from agentic_knowledge_os.evaluation import (
    benchmark_suite,
    build_artifact_identity_ledger,
    score_trace_set,
    validate_trace_set,
    verify_artifact_identity_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
CONFORMANT = ROOT / "fixtures" / "evaluation" / "conformant-traces.json"


class GovernanceEvaluationTests(unittest.TestCase):
    def _traces(self) -> dict:
        return json.loads(CONFORMANT.read_text(encoding="utf-8"))

    def test_suite_covers_each_core8_profile_once(self) -> None:
        suite = benchmark_suite()
        profiles = [case["expected_profile"] for case in suite["cases"]]
        self.assertEqual(len(suite["cases"]), 8)
        self.assertEqual(len(profiles), len(set(profiles)))
        self.assertEqual(set(suite["axes"]), set(suite["thresholds"]["minimum_axis_scores"]))
        self.assertTrue(all(case["governance_refs"] for case in suite["cases"]))
        self.assertTrue(
            all(reference.startswith("AKOS-RFC-0001.") for case in suite["cases"] for reference in case["governance_refs"])
        )

    def test_conformant_fixture_passes_without_effectiveness_claim(self) -> None:
        receipt = score_trace_set(self._traces())
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["gate_status"], "clear")
        self.assertEqual(receipt["conformance_score"], 1.0)
        self.assertEqual(receipt["effectiveness"]["status"], "not-measured")
        self.assertEqual(receipt["case_count"], 8)
        self.assertEqual(receipt["artifact_identity_ledger"]["claim_limit"], "byte-identity-only")

    def test_hard_gate_failure_overrides_average_score(self) -> None:
        traces = self._traces()
        traces["cases"][0]["events"].append("semantic_auto_acceptance")
        traces["cases"][0]["unauthorized_effects"].append("semantic-acceptance")
        receipt = score_trace_set(traces)
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["gate_status"], "blocked")
        self.assertIn("akos.eval.semantic-authority", receipt["hard_gate_failures"])

    def test_trace_inventory_is_closed(self) -> None:
        traces = self._traces()
        traces["cases"].pop()
        with self.assertRaisesRegex(ValueError, "case inventory"):
            validate_trace_set(traces, benchmark_suite())

    def test_artifact_identity_ledger_is_deterministic_and_detects_drift(self) -> None:
        artifacts = {"suite.json": b"{}\n", "trace.json": b'{"status":"held"}\n'}
        ledger = build_artifact_identity_ledger("evaluation-inputs", artifacts)
        self.assertEqual(ledger, build_artifact_identity_ledger("evaluation-inputs", artifacts))
        self.assertEqual(verify_artifact_identity_ledger(ledger, artifacts)["status"], "clear")
        changed = deepcopy(artifacts)
        changed["trace.json"] = b'{"status":"complete"}\n'
        verification = verify_artifact_identity_ledger(ledger, changed)
        self.assertEqual(verification["status"], "blocked")
        self.assertIn("digest mismatch: trace.json", verification["findings"])

    def test_identity_ledger_rejects_duplicate_locator(self) -> None:
        ledger = build_artifact_identity_ledger("test", {"a.md": b"alpha\n"})
        ledger["entries"].append(dict(ledger["entries"][0]))
        verification = verify_artifact_identity_ledger(ledger, {"a.md": b"alpha\n"})
        self.assertEqual(verification["status"], "blocked")
        self.assertIn("artifact ledger contains a duplicate locator", verification["findings"])


if __name__ == "__main__":
    unittest.main()
