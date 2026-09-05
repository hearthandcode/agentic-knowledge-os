"""End-to-end check for the public alpha evaluation surface."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AlphaEvaluationTests(unittest.TestCase):
    def test_public_evaluation_completes(self) -> None:
        environment = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "evaluate_alpha.py")],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["profile_count"], 8)
        self.assertEqual(result["receipts"], {"apply": "applied", "verify": "clear", "uninstall": "removed"})
        self.assertTrue(result["user_note_preserved"])
        self.assertTrue(result["generated_paths_absent"])


if __name__ == "__main__":
    unittest.main()
