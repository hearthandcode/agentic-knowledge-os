"""Scorer mutation-audit and comparative behavioral evaluation tests."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from agentic_knowledge_os.evaluation import (
    audit_governance_scorer,
    behavioral_experiment_plan,
    behavioral_rubric,
    score_behavioral_experiment,
    synthetic_behavioral_observations,
    validate_behavioral_experiment_plan,
    validate_behavioral_observations,
)


ROOT = Path(__file__).resolve().parents[1]
CONFORMANT = ROOT / "fixtures/evaluation/conformant-traces.json"


class EvaluationHarnessTests(unittest.TestCase):
    def test_mutation_audit_detects_every_declared_probe(self) -> None:
        traces = json.loads(CONFORMANT.read_text(encoding="utf-8"))
        audit = audit_governance_scorer(traces)
        self.assertEqual(audit["status"], "passed")
        self.assertEqual(audit["detection_score"], 1.0)
        self.assertGreaterEqual(audit["probe_count"], 12)
        self.assertTrue(all(probe["detected"] for probe in audit["probes"]))

    def test_behavioral_plan_is_deterministic_and_tamper_evident(self) -> None:
        plan = behavioral_experiment_plan()
        self.assertEqual(plan, behavioral_experiment_plan())
        self.assertEqual(len(plan["conditions"]), 3)
        self.assertEqual(len(plan["tasks"]), 12)
        self.assertEqual({task["expected_profile"] for task in plan["tasks"]}, {profile["id"] for profile in __import__("agentic_knowledge_os").core8_profiles()})
        self.assertEqual({task["split"] for task in plan["tasks"]}, {"held-out"})
        self.assertEqual(plan["repetitions"], 2)
        self.assertEqual(len(synthetic_behavioral_observations(plan)["records"]), 72)
        self.assertEqual(plan["rubric_id"], behavioral_rubric()["rubric_id"])
        self.assertTrue(all(task["prompt"] and task["fixture_records"] and task["outcome_checks"] for task in plan["tasks"]))
        changed = deepcopy(plan)
        changed["repetitions"] = 1
        with self.assertRaisesRegex(ValueError, "digest or fields changed"):
            validate_behavioral_experiment_plan(changed)

    def test_synthetic_behavioral_canary_never_claims_effectiveness(self) -> None:
        plan = behavioral_experiment_plan()
        observations = synthetic_behavioral_observations(plan)
        validate_behavioral_observations(observations, plan)
        receipt = score_behavioral_experiment(observations, plan)
        self.assertEqual(receipt["status"], "canary-only")
        self.assertEqual(receipt["effectiveness"]["status"], "not-measured")
        self.assertNotIn("overall_effectiveness_score", receipt)
        self.assertGreater(
            receipt["comparisons"]["agents-md-only"]["metrics"]["task_utility"]["mean_delta"],
            0,
        )
        self.assertEqual(receipt["artifact_identity_ledger"]["claim_limit"], "byte-identity-only")

    def test_behavioral_hard_gate_blocks_candidate_claim(self) -> None:
        plan = behavioral_experiment_plan()
        observations = synthetic_behavioral_observations(plan)
        candidate = next(record for record in observations["records"] if record["condition"] == "akos")
        candidate["hard_gate_failures"].append("silent_write_back")
        receipt = score_behavioral_experiment(observations, plan)
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["gate_status"], "blocked")
        self.assertEqual(receipt["effectiveness"]["status"], "not-eligible")

    def test_behavioral_inventory_must_be_exactly_paired(self) -> None:
        plan = behavioral_experiment_plan()
        observations = synthetic_behavioral_observations(plan)
        observations["records"].pop()
        with self.assertRaisesRegex(ValueError, "record inventory"):
            validate_behavioral_observations(observations, plan)

    def test_runner_observations_must_use_preregistered_methods(self) -> None:
        plan = behavioral_experiment_plan()
        observations = synthetic_behavioral_observations(plan)
        observations["measurement_class"] = "runner-observed"
        observations["runner"] = "example-adapter"
        with self.assertRaisesRegex(ValueError, "preregistered rubric"):
            validate_behavioral_observations(observations, plan)

    def test_runner_observations_hold_metrics_without_inventing_scores(self) -> None:
        plan = behavioral_experiment_plan()
        observations = synthetic_behavioral_observations(plan)
        observations["measurement_class"] = "runner-observed"
        observations["runner"] = "promptfoo"
        methods = {record["id"]: record["method"] for record in behavioral_rubric()["metrics"]}
        for record in observations["records"]:
            record["measurement_methods"] = methods.copy()
            record["metrics"]["correction_efficiency"] = None
            record["metrics"]["recovery_quality"] = None
        receipt = score_behavioral_experiment(observations, plan)
        self.assertEqual(receipt["status"], "estimated")
        self.assertEqual(receipt["effectiveness"]["status"], "qualified-pending-human-review")
        held = receipt["comparisons"]["agents-md-only"]["metrics"]["correction_efficiency"]
        self.assertEqual(held["status"], "not-measured")
        self.assertEqual(held["paired_observations"], 0)
        self.assertEqual(receipt["comparisons"]["agents-md-only"]["metrics"]["task_utility"]["status"], "measured")

    def test_baseline_hard_gate_does_not_block_candidate_eligibility(self) -> None:
        plan = behavioral_experiment_plan()
        observations = synthetic_behavioral_observations(plan)
        baseline = next(record for record in observations["records"] if record["condition"] == "structured-baseline")
        baseline["hard_gate_failures"].append("private_source_disclosure")
        receipt = score_behavioral_experiment(observations, plan)
        self.assertEqual(receipt["gate_status"], "clear")
        self.assertEqual(receipt["candidate_hard_gate_failures"], [])


if __name__ == "__main__":
    unittest.main()
