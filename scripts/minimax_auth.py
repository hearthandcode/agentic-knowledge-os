#!/usr/bin/env python3
"""Operate the MiniMax auth boundary without exposing credential material."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess

from agentic_knowledge_os.promptfoo import AUTH_MODES, PROVIDER_CONFIRMATION, minimax_auth_status


def _mmx() -> str:
    executable = shutil.which("mmx")
    if not executable:
        raise SystemExit("official mmx CLI is not available on PATH")
    return executable


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status", help="Return only an allowlisted auth status")
    status.add_argument("--mode", choices=AUTH_MODES, required=True)
    login = subparsers.add_parser("login-oauth", help="Start official MiniMax device authorization")
    login.add_argument("--region", choices=("global", "cn"), default="global")
    login.add_argument("--confirm-provider", required=True)
    refresh = subparsers.add_parser("refresh-oauth", help="Ask the official CLI to refresh OAuth")
    refresh.add_argument("--confirm-provider", required=True)
    args = parser.parse_args()
    if args.command == "status":
        result = minimax_auth_status(args.mode)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "ready" else 2
    if args.confirm_provider != PROVIDER_CONFIRMATION:
        raise SystemExit(f"confirmation must exactly equal {PROVIDER_CONFIRMATION}")
    executable = _mmx()
    command = (
        [executable, "auth", "login", "--recommend", f"--region={args.region}"]
        if args.command == "login-oauth"
        else [executable, "auth", "refresh"]
    )
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
