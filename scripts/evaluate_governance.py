#!/usr/bin/env python3
"""Run provider-free AKOS governance scorer canaries."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

from agentic_knowledge_os.evaluation import score_trace_set


ROOT = Path(__file__).resolve().parents[1]
CONFORMANT = ROOT / "fixtures" / "evaluation" / "conformant-traces.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("evaluation traces must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Score AKOS policy-conformance traces")
    parser.add_argument("--traces", type=Path, help="Score one adapter-neutral trace set instead of the canaries")
    args = parser.parse_args()
    if args.traces:
        receipt = score_trace_set(_load(args.traces))
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if receipt["status"] == "passed" else 2

    conformant_traces = _load(CONFORMANT)
    conformant = score_trace_set(conformant_traces)
    negative_traces = deepcopy(conformant_traces)
    negative_traces["condition"] = "synthetic-hard-gate-canary"
    negative_traces["cases"][0]["events"].append("semantic_auto_acceptance")
    negative_traces["cases"][0]["unauthorized_effects"].append("semantic-acceptance")
    negative = score_trace_set(negative_traces)
    passed = (
        conformant["status"] == "passed"
        and conformant["conformance_score"] == 1.0
        and negative["status"] == "failed"
        and negative["gate_status"] == "blocked"
        and conformant["effectiveness"]["status"] == "not-measured"
    )
    summary = {
        "schema": "akos.governance-harness-canary.v1",
        "status": "passed" if passed else "failed",
        "conformant": {
            "status": conformant["status"],
            "conformance_score": conformant["conformance_score"],
            "axis_scores": conformant["axis_scores"],
        },
        "negative_control": {
            "status": negative["status"],
            "gate_status": negative["gate_status"],
            "hard_gate_failures": negative["hard_gate_failures"],
        },
        "effectiveness": "not-measured",
        "limits": [
            "synthetic fixture replay only",
            "no model or host executed",
            "no task utility or semantic correctness measured",
            "human review remains required",
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
