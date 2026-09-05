#!/usr/bin/env python3
"""Validate alpha source shape and public-safety invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agentic_knowledge_os.compiler import (  # noqa: E402
    build_plan,
    compile_bundle,
    core8_profiles,
    host_adapters,
    operating_policy,
    type_kernel,
    validate_brain,
    validate_plan,
)


TEXT_SUFFIXES = {".md", ".py", ".json", ".toml"}
FORBIDDEN_TEXT = (
    "/" + "home/",
    "cosma" + "trexis",
    "BEGIN PRIVATE" + " KEY",
    "AK" + "IA",
    "sk-" + "proj-",
    "verified:" + " true",
    '"verified":' + " true",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            fail(f"invalid JSON {path.relative_to(ROOT)}: {error}")

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if text and not text.endswith("\n"):
            fail(f"missing final newline in {path.relative_to(ROOT)}")
        if any(line.rstrip(" \t") != line for line in text.splitlines()):
            fail(f"trailing whitespace in {path.relative_to(ROOT)}")
        for marker in FORBIDDEN_TEXT:
            if marker in text:
                fail(f"public-safety marker {marker!r} in {path.relative_to(ROOT)}")

    profiles = core8_profiles()
    if len(profiles) != 8:
        fail("Core8 count is not eight")
    if set(host_adapters()) != {"neutral", "hermes", "pi", "exocore"}:
        fail("host adapter registry is incomplete")
    type_ids = {item["id"] for item in type_kernel()["types"]}
    profile_ids = {profile["id"] for profile in profiles}
    for profile in profiles:
        referenced = set((*profile["transformation"]["domain"], *profile["transformation"]["codomain"]))
        if not referenced.issubset(type_ids):
            fail(f"profile references an unknown type: {profile['id']}")
        if not set(profile["handoff_to"]).issubset(profile_ids - {profile['id']}):
            fail(f"profile handoff graph is open or self-referential: {profile['id']}")
    policy = operating_policy()
    if policy["semantic_orientation"]["canonical_meaning_default"] is not None:
        fail("semantic orientation defaults canonical meaning")

    valid_fixture = json.loads((ROOT / "fixtures/valid/brain.json").read_text(encoding="utf-8"))
    invalid_fixture = json.loads((ROOT / "fixtures/invalid/unknown-profile.json").read_text(encoding="utf-8"))
    validate_brain(valid_fixture)
    try:
        validate_brain(invalid_fixture)
    except ValueError:
        pass
    else:
        fail("invalid brain fixture was accepted")

    plan = build_plan(name="Validation Brain", workspace="/workspace/validation", host="hermes")
    validate_plan(plan)
    bundle = compile_bundle(plan)
    if set(bundle) != set(plan["files"]):
        fail("rendered bundle and plan inventory differ")
    if any(path.endswith(".hermes.md") for path in bundle):
        fail("Hermes projection unexpectedly emitted .hermes.md")
    if len([path for path in bundle if path.startswith(".akos/profiles/")]) != 8:
        fail("portable Core8 profile fleet is incomplete")
    for required_path in (".akos/type-kernel.json", ".akos/operating-policy.json", ".akos/ORIENTATION.md"):
        if required_path not in bundle:
            fail(f"refined orientation artifact is missing: {required_path}")
    if plan["effects"]["workspace_write"] != "exact-plan-confirmation-required":
        fail("workspace write is missing its exact confirmation gate")
    for effect in ("enablement", "configuration", "provider_use", "network_use", "publication"):
        if plan["effects"][effect] != "held":
            fail(f"downstream effect is not held: {effect}")

    template = (SRC / "agentic_knowledge_os" / "data" / "workspace-agents.template.md").read_text(encoding="utf-8")
    for placeholder in ("{{BRAIN_NAME}}", "{{PLAN_ID}}", "{{HOST}}", "{{CORE8_ROLES}}"):
        if placeholder not in template:
            fail(f"workspace template missing {placeholder}")

    profile_template = (SRC / "agentic_knowledge_os" / "data" / "profile.template.md").read_text(encoding="utf-8")
    for placeholder in (
        "{{PROFILE_LABEL}}", "{{PROFILE_ID}}", "{{MANDATE}}", "{{ATTENTION_SIGNAL}}",
        "{{ROUTING_QUESTION}}", "{{ADMISSION_TEST}}", "{{TRANSFORMATION_ID}}",
        "{{DOMAIN}}", "{{CODOMAIN}}", "{{PRECONDITIONS}}", "{{INVARIANTS}}",
        "{{FAILURE_RETURNS}}", "{{OWNED_OUTCOME}}", "{{NON_TRIGGERS}}",
        "{{BOUNDARIES}}", "{{FALSIFIER}}", "{{HANDOFFS}}",
    ):
        if placeholder not in profile_template:
            fail(f"profile template missing {placeholder}")

    if "# Extended Mind Constitution:" not in template:
        fail("workspace template is not oriented as an extended-mind constitution")

    orientation_template = (SRC / "agentic_knowledge_os" / "data" / "orientation.template.md").read_text(encoding="utf-8")
    for placeholder in ("{{BRAIN_NAME}}", "{{PLAN_ID}}", "{{HOST}}"):
        if placeholder not in orientation_template:
            fail(f"orientation template missing {placeholder}")

    if "AKOS-RFC-0001.5" not in template or "AKOS-RFC-0001.10" not in template:
        fail("workspace constitution lacks typed or operational-intelligence clauses")

    software_license = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if not software_license.startswith("PolyForm Noncommercial License 1.0.0\n"):
        fail("software license is not PolyForm Noncommercial 1.0.0")
    package_metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if 'license = "PolyForm-Noncommercial-1.0.0"' not in package_metadata:
        fail("package metadata and software license differ")
    documentation_license = (ROOT / "LICENSE-DOCUMENTATION.md").read_text(encoding="utf-8")
    if "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International" not in documentation_license:
        fail("documentation license is missing or changed")
    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    if "Required Notice: Copyright 2026 Scott Rallya and Hearth & Code." not in notice:
        fail("required PolyForm notice is missing")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "source-available, not OSI open source" not in readme:
        fail("README does not distinguish source-available from open source")
    if "scripts/evaluate_alpha.py" not in readme:
        fail("README does not expose the provider-free alpha evaluation")

    package_version = 'version = "0.3.0a1"'
    if package_version not in package_metadata:
        fail("Python package version does not match the public alpha")
    if not (ROOT / "CHANGELOG.md").is_file() or not (ROOT / "docs/evaluation-guide.md").is_file():
        fail("public alpha release surface is incomplete")

    print("PASS: alpha inventory, JSON, typed Core8, semantic policy, license split, adapter, determinism, lifecycle boundary, evaluation surface, and public-safety checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
