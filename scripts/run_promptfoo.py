#!/usr/bin/env python3
"""Run the isolated Promptfoo + MiniMax-M3 comparison and normalize its evidence."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from agentic_knowledge_os.promptfoo import (
    AUTH_MODES,
    MODEL_ID,
    PROMPTFOO_ENV,
    minimax_auth_status,
    promptfoo_config,
    score_promptfoo_results,
    write_promptfoo_bundle,
)


def _prepare_or_verify(root: Path, auth_mode: str) -> None:
    if not root.exists() or not any(root.iterdir()):
        write_promptfoo_bundle(root, auth_mode)
        return
    manifest_path = root / "run-manifest.json"
    config_path = root / "promptfooconfig.json"
    if not manifest_path.is_file() or not config_path.is_file():
        raise ValueError("existing output root is not an AKOS Promptfoo run bundle")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if manifest.get("auth_mode") != auth_mode or config != promptfoo_config(auth_mode):
        raise ValueError("existing Promptfoo bundle does not match the requested auth mode or current source")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auth-mode", choices=AUTH_MODES, required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--confirm-provider", required=True)
    parser.add_argument("--promptfoo-command", default="promptfoo")
    args = parser.parse_args()
    if args.confirm_provider != MODEL_ID:
        raise SystemExit(f"confirmation must exactly equal {MODEL_ID}")
    auth = minimax_auth_status(args.auth_mode)
    if auth["status"] != "ready":
        print(json.dumps(auth, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    executable = shutil.which(args.promptfoo_command)
    if not executable:
        raise SystemExit("Promptfoo executable is not available on PATH; install it separately or pass --promptfoo-command")
    root = Path(args.output_root).expanduser().resolve()
    try:
        _prepare_or_verify(root, args.auth_mode)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
    promptfoo_state = root / ".promptfoo"
    env = os.environ.copy()
    env.update(PROMPTFOO_ENV)
    env.update({
        "PROMPTFOO_CONFIG_DIR": str(promptfoo_state),
        "PROMPTFOO_CACHE_PATH": str(promptfoo_state / "cache"),
        "PROMPTFOO_LOG_DIR": str(promptfoo_state / "logs"),
    })
    raw_path = root / "promptfoo-results.json"
    process = subprocess.run(
        [
            executable,
            "eval",
            "-c",
            str(root / "promptfooconfig.json"),
            "--no-cache",
            "--no-share",
            "--max-concurrency",
            "1",
            "--no-table",
            "--output",
            str(raw_path),
        ],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    (root / "promptfoo-stdout.log").write_text(process.stdout, encoding="utf-8")
    (root / "promptfoo-stderr.log").write_text(process.stderr, encoding="utf-8")
    if not raw_path.is_file():
        print(json.dumps({
            "status": "runner-failed",
            "promptfoo_exit_code": process.returncode,
            "auth": auth,
            "logs": [str(root / "promptfoo-stdout.log"), str(root / "promptfoo-stderr.log")],
            "credential_material": "not-read-or-returned",
            "verified": False,
        }, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    try:
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        observations, receipt = score_promptfoo_results(raw)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Promptfoo result normalization failed: {error}") from error
    observations_path = root / "behavioral-observations.json"
    receipt_path = root / "behavioral-evaluation-receipt.json"
    observations_path.write_text(json.dumps(observations, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "status": "evaluated",
        "promptfoo_exit_code": process.returncode,
        "auth_mode": args.auth_mode,
        "model": MODEL_ID,
        "observation_count": len(observations["records"]),
        "evaluation_status": receipt["status"],
        "gate_status": receipt["gate_status"],
        "effectiveness": receipt["effectiveness"],
        "outputs": {
            "raw": str(raw_path),
            "observations": str(observations_path),
            "receipt": str(receipt_path),
        },
        "publication": "held",
        "review_status": "review-required",
        "verified": False,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
