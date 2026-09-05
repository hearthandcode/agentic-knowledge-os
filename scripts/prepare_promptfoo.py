#!/usr/bin/env python3
"""Prepare a credential-free Promptfoo run bundle without calling a provider."""

from __future__ import annotations

import argparse
import json

from agentic_knowledge_os.promptfoo import AUTH_MODES, write_promptfoo_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auth-mode", choices=AUTH_MODES, required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    try:
        result = write_promptfoo_bundle(args.output_root, args.auth_mode)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
