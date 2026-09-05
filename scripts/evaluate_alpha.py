#!/usr/bin/env python3
"""Run the provider-free Agentic Knowledge OS alpha lifecycle evaluation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from agentic_knowledge_os.compiler import build_plan, compile_bundle
from agentic_knowledge_os.operations import apply_plan, uninstall, verify_install


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="akos-alpha-") as temporary_root:
        workspace = Path(temporary_root) / "extended-mind"
        plan = build_plan(name="Alpha Evaluation", workspace=str(workspace), host="hermes")
        bundle = compile_bundle(plan)
        applied = apply_plan(plan, plan["plan_id"])
        verified = verify_install(workspace)

        user_note = workspace / "knowledge" / "user-note.md"
        user_note.write_text("# User-owned evaluation note\n", encoding="utf-8")

        removed = uninstall(workspace, applied.get("manifest_digest", ""))
        generated_paths_absent = all(not (workspace / relative).exists() for relative in bundle)
        user_note_preserved = user_note.read_text(encoding="utf-8") == "# User-owned evaluation note\n"

        passed = (
            applied["status"] == "applied"
            and verified["status"] == "clear"
            and removed["status"] == "removed"
            and generated_paths_absent
            and user_note_preserved
        )
        result = {
            "evaluation": "akos.alpha-lifecycle.v1",
            "status": "passed" if passed else "failed",
            "host_projection": plan["brain"]["host"],
            "profile_count": len(plan["brain"]["profiles"]),
            "generated_file_count": len(bundle),
            "receipts": {
                "apply": applied["status"],
                "verify": verified["status"],
                "uninstall": removed["status"],
            },
            "user_note_preserved": user_note_preserved,
            "generated_paths_absent": generated_paths_absent,
            "limits": [
                "temporary workspace only",
                "no live host activation",
                "no provider or network use",
                "no semantic or usefulness claim",
            ],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
