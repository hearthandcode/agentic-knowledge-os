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
from agentic_knowledge_os.host_packages import (  # noqa: E402
    build_host_package_plan,
    compile_host_package,
)
from agentic_knowledge_os.evaluation import (  # noqa: E402
    audit_governance_scorer,
    behavioral_experiment_plan,
    behavioral_rubric,
    benchmark_suite,
    score_behavioral_experiment,
    score_trace_set,
    synthetic_behavioral_observations,
    validate_behavioral_observations,
    validate_trace_set,
)
from agentic_knowledge_os.promptfoo import promptfoo_bundle, promptfoo_config  # noqa: E402
from agentic_knowledge_os.benchmark_v6 import load_plan as load_v6_plan  # noqa: E402


TEXT_SUFFIXES = {".md", ".py", ".json", ".toml", ".txt"}
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
    load_v6_plan(ROOT / 'src/agentic_knowledge_os/data/behavioral-experiment-v6.json')
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
        if profile.get("contract_version") != "akos.profile-contract.v1" or len(profile.get("rfc_rules", [])) != 4:
            fail(f"profile contract or RFC inventory is incomplete: {profile['id']}")
    policy = operating_policy()
    if policy["semantic_orientation"]["canonical_meaning_default"] is not None:
        fail("semantic orientation defaults canonical meaning")

    suite = benchmark_suite()
    traces = json.loads((ROOT / "fixtures/evaluation/conformant-traces.json").read_text(encoding="utf-8"))
    conformance = score_trace_set(traces, suite)
    if conformance["status"] != "passed" or conformance["conformance_score"] != 1.0:
        fail("governance benchmark conformant canary did not pass")
    if conformance["effectiveness"]["status"] != "not-measured":
        fail("governance benchmark overclaims effectiveness")
    if conformance["artifact_identity_ledger"]["claim_limit"] != "byte-identity-only":
        fail("evaluation identity ledger claim boundary changed")
    audit = audit_governance_scorer(traces)
    if audit["status"] != "passed" or audit["detection_score"] != 1.0:
        fail("governance scorer mutation audit did not detect every probe")
    experiment = behavioral_experiment_plan()
    if experiment["rubric_id"] != behavioral_rubric()["rubric_id"]:
        fail("behavioral experiment and rubric identities differ")
    behavioral = score_behavioral_experiment(synthetic_behavioral_observations(experiment), experiment)
    if behavioral["status"] != "canary-only" or behavioral["effectiveness"]["status"] != "not-measured":
        fail("behavioral math canary overclaims effectiveness")
    if behavioral["scoring_model"]["composite_score"] != "prohibited":
        fail("behavioral evaluation introduced a compensating composite score")
    invalid_behavioral = json.loads(
        (ROOT / "fixtures/evaluation/invalid-behavioral-observations.json").read_text(encoding="utf-8")
    )
    try:
        validate_behavioral_observations(invalid_behavioral, experiment)
    except ValueError:
        pass
    else:
        fail("invalid behavioral observations fixture was accepted")
    for auth_mode in ("api-key", "oauth"):
        promptfoo = promptfoo_config(auth_mode)
        if len(promptfoo["tests"]) != 72 or promptfoo.get("sharing") is not False:
            fail(f"Promptfoo {auth_mode} config is incomplete or shareable")
        serialized_promptfoo = json.dumps(promptfoo)
        if "MINIMAX_API_KEY" in serialized_promptfoo or '"apiKey"' in serialized_promptfoo:
            fail(f"Promptfoo {auth_mode} config contains credential material or a credential field")
        bundle = promptfoo_bundle(auth_mode)
        if set(bundle) != {"assertions.cjs", "minimax_oauth_provider.py", "behavioral-experiment-v5.json", "behavioral-rubric-v5.json", "promptfooconfig.json", "run-manifest.json"}:
            fail(f"Promptfoo {auth_mode} bundle inventory changed")
    negative = json.loads((ROOT / "fixtures/evaluation/invalid-missing-case.json").read_text(encoding="utf-8"))
    try:
        validate_trace_set(negative, suite)
    except ValueError:
        pass
    else:
        fail("invalid evaluation trace fixture was accepted")

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

    host_packages: dict[str, dict[str, str]] = {}
    for host, native_manifest in (("hermes", "plugin.json"), ("pi", "package.json")):
        package_plan = build_host_package_plan(
            name="Validation Package",
            output_root=f"/packages/{host}",
            host=host,
        )
        package = compile_host_package(package_plan)
        host_packages[host] = package
        if native_manifest not in package:
            fail(f"{host} native package manifest is missing")
        if any(path.startswith(".akos") or "/.akos" in path for path in package):
            fail(f"{host} package contains a portable .akos path")
        if "skills/agentic-knowledge-os/SKILL.md" not in package:
            fail(f"{host} package skill is missing")
        if "skills/agentic-knowledge-os/references/governance-benchmark.json" not in package:
            fail(f"{host} package governance benchmark is missing")
        if "skills/agentic-knowledge-os/references/behavioral-experiment.json" not in package:
            fail(f"{host} package behavioral experiment plan is missing")
        if "skills/agentic-knowledge-os/references/behavioral-rubric.json" not in package:
            fail(f"{host} package behavioral rubric is missing")
        if package_plan["effects"]["host_installation"] != "held":
            fail(f"{host} package plan does not hold installation")
    pi_manifest = json.loads(host_packages["pi"]["package.json"])
    if pi_manifest.get("pi") != {"skills": ["./skills"], "prompts": ["./prompts"]}:
        fail("Pi package resources changed")
    hermes_manifest = json.loads(host_packages["hermes"]["plugin.json"])
    if hermes_manifest.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        fail("Hermes Agent Plugins schema changed")

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
        "{{BOUNDARIES}}", "{{FALSIFIER}}", "{{HANDOFFS}}", "{{RFC_RULES}}",
    ):
        if placeholder not in profile_template:
            fail(f"profile template missing {placeholder}")

    if "# Extended Mind Constitution:" not in template:
        fail("workspace template is not oriented as an extended-mind constitution")

    orientation_template = (SRC / "agentic_knowledge_os" / "data" / "orientation.template.md").read_text(encoding="utf-8")
    for placeholder in ("{{BRAIN_NAME}}", "{{PLAN_ID}}", "{{HOST}}"):
        if placeholder not in orientation_template:
            fail(f"orientation template missing {placeholder}")

    if any(f"AKOS-RFC-0001.{index}" not in template for index in (5, 10, 16, 17)):
        fail("workspace constitution lacks typed or operational-intelligence clauses")

    software_license = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if not software_license.startswith("PolyForm Noncommercial License 1.0.0\n"):
        fail("software license is not PolyForm Noncommercial 1.0.0")
    packaged_license = (SRC / "agentic_knowledge_os" / "data" / "software-license.txt").read_text(encoding="utf-8")
    if packaged_license != software_license:
        fail("generated-package license bytes differ from the repository license")
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
    if "scripts/evaluate_governance.py" not in readme:
        fail("README does not expose the provider-free governance benchmark")
    if "scripts/evaluate_harness.py" not in readme:
        fail("README does not expose the evaluation harness audit")
    if "scripts/run_promptfoo.py" not in readme or "MiniMax-M3" not in readme:
        fail("README does not expose the optional MiniMax-M3 Promptfoo runner")
    if "scripts/generate_host_packages.py" not in readme:
        fail("README does not expose host-native package generation")

    package_version = 'version = "0.3.0a1"'
    if package_version not in package_metadata:
        fail("Python package version does not match the public alpha")
    if not (ROOT / "CHANGELOG.md").is_file() or not (ROOT / "docs/evaluation-guide.md").is_file():
        fail("public alpha release surface is incomplete")
    initial_release = ROOT / "docs/initial-release.md"
    if not initial_release.is_file():
        fail("initial release orientation is missing")
    release_text = initial_release.read_text(encoding="utf-8")
    for marker in ("v0.3.0-alpha.1", "Hermes Agent v0.21.0", "Pi v0.83.0", "generate_host_packages.py"):
        if marker not in release_text:
            fail(f"initial release orientation is missing {marker}")
    announcement = (ROOT / "docs/community-announcement.md").read_text(encoding="utf-8")
    long_post = announcement.split("## Nous Research Discord — 128 words", 1)[1].split("## Compact post", 1)[0]
    long_words = [word for line in long_post.splitlines() if line.startswith(">") for word in line[1:].split()]
    if len(long_words) != 128:
        fail(f"Discord announcement is {len(long_words)} words instead of 128")
    compact_section = announcement.split("## Compact post — 256 characters", 1)[1]
    compact_lines = [line[2:] for line in compact_section.splitlines() if line.startswith("> ")]
    if len(compact_lines) != 1 or len(compact_lines[0]) != 256:
        fail("compact announcement is not exactly one 256-character line")

    print("PASS: alpha inventory, JSON, typed Core8, semantic policy, governance benchmark, scorer mutation audit, matched behavioral canary, secret-free Promptfoo configs, byte-identity ledger, license split, host-native packages, determinism, lifecycle boundaries, evaluation surface, and public-safety checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
