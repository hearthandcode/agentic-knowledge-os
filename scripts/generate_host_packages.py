#!/usr/bin/env python3
"""Generate reviewable Hermes and Pi packages without installing them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_knowledge_os.host_packages import build_host_package_plan, write_host_package


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate host-native Agentic Knowledge OS packages")
    parser.add_argument("--output-root", required=True, help="Absolute empty parent for generated package directories")
    parser.add_argument("--name", default="Agentic Knowledge OS", help="Human-readable projected brain name")
    parser.add_argument("--profiles", help="Comma-separated Core8 profile IDs; defaults to all eight")
    args = parser.parse_args()

    output_root = Path(args.output_root).resolve(strict=False)
    if output_root == Path("/"):
        raise SystemExit("filesystem root cannot be an output root")
    if output_root.exists() and (not output_root.is_dir() or any(output_root.iterdir())):
        raise SystemExit("output root must be absent or an empty directory")
    if not output_root.exists():
        if not output_root.parent.is_dir() or output_root.parent.is_symlink():
            raise SystemExit("output parent must exist and cannot be a symbolic link")
        output_root.mkdir()

    selected = None if args.profiles is None else [item.strip() for item in args.profiles.split(",") if item.strip()]
    results = []
    for host in ("hermes", "pi"):
        package_root = output_root / f"{host}-agentic-knowledge-os"
        plan = build_host_package_plan(
            name=args.name,
            output_root=str(package_root),
            host=host,
            selected_profiles=selected,
        )
        receipt = write_host_package(plan, plan["package_id"])
        results.append(receipt)
        if receipt["status"] != "written":
            print(json.dumps({"status": "blocked", "packages": results}, ensure_ascii=False, indent=2, sort_keys=True))
            return 2

    print(json.dumps({"status": "written", "packages": results}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
