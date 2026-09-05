#!/usr/bin/env python3
"""Audit the AKOS scorers and exercise comparative evaluation math."""

from __future__ import annotations

import json
from pathlib import Path

from agentic_knowledge_os.evaluation import (
    audit_governance_scorer,
    behavioral_experiment_plan,
    score_behavioral_experiment,
    score_trace_set,
    synthetic_behavioral_observations,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    traces = json.loads((ROOT / "fixtures/evaluation/conformant-traces.json").read_text(encoding="utf-8"))
    conformance = score_trace_set(traces)
    audit = audit_governance_scorer(traces)
    plan = behavioral_experiment_plan()
    behavioral = score_behavioral_experiment(synthetic_behavioral_observations(plan), plan)
    passed = (
        conformance["status"] == "passed"
        and audit["status"] == "passed"
        and audit["detection_score"] == 1.0
        and behavioral["status"] == "canary-only"
        and behavioral["effectiveness"]["status"] == "not-measured"
        and behavioral["scoring_model"]["composite_score"] == "prohibited"
    )
    summary = {
        "schema": "akos.evaluation-harness-audit.v1",
        "status": "passed" if passed else "failed",
        "governance_canary": {
            "conformance_score": conformance["conformance_score"],
            "gate_status": conformance["gate_status"],
            "evidence_class": "synthetic",
        },
        "scorer_audit": {
            "probe_count": audit["probe_count"],
            "detected_count": audit["detected_count"],
            "detection_score": audit["detection_score"],
        },
        "behavioral_math_canary": {
            "status": behavioral["status"],
            "effectiveness": behavioral["effectiveness"]["status"],
            "composite_score": behavioral["scoring_model"]["composite_score"],
            "comparisons": behavioral["comparisons"],
            "generalization_check": behavioral["generalization_check"],
        },
        "readiness": "source-ready-for-observed-runner-adapter",
        "held": ["host execution", "provider use", "publication", "effectiveness claim"],
        "review_status": "review-required",
        "verified": False,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
