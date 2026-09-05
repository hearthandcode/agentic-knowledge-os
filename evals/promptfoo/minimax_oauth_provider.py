#!/usr/bin/env python3
"""Promptfoo Python provider that delegates OAuth handling to the official mmx CLI."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


def _invoke(prompt: str) -> dict[str, str]:
    executable = shutil.which("mmx")
    if not executable:
        return {"error": "official mmx CLI is not available on PATH"}
    messages = json.dumps([{"role": "user", "content": prompt}], ensure_ascii=False)
    process = subprocess.run(
        [
            executable,
            "text",
            "chat",
            "--model",
            "MiniMax-M3",
            "--messages-file",
            "-",
            "--output",
            "text",
        ],
        input=messages,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        return {"error": "MiniMax OAuth provider call failed; inspect mmx auth status privately"}
    return {"output": process.stdout}


def call_api(prompt: str, _options: dict | None = None, _context: dict | None = None) -> dict[str, str]:
    """Receive the rendered prompt over Promptfoo worker IPC, not a process argument."""

    return _invoke(prompt)


def main() -> int:
    if len(sys.argv) < 2:
        print("missing rendered prompt", file=sys.stderr)
        return 2
    result = _invoke(sys.argv[1])
    if "error" in result:
        print(result["error"], file=sys.stderr)
        return 3
    sys.stdout.write(result["output"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
