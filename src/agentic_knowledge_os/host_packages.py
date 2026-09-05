"""Compile and write host-native Hermes and Pi package projections."""

from __future__ import annotations

import json
import os
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .compiler import (
    DATA_PACKAGE,
    build_plan,
    compile_bundle,
    content_digest,
    object_digest,
)
from .evaluation import behavioral_experiment_plan, behavioral_rubric, benchmark_suite


PACKAGE_HOSTS = ("hermes", "pi")
PACKAGE_VERSION = "0.3.0-alpha.1"
PACKAGE_MANIFEST_PATH = "package-manifest.json"
SKILL_ROOT = "skills/agentic-knowledge-os"
REFERENCE_ROOT = f"{SKILL_ROOT}/references"


def _normalized_output_root(output_root: str) -> str:
    path = Path(output_root)
    if not path.is_absolute():
        raise ValueError("package output root must be an absolute path")
    resolved = path.resolve(strict=False)
    if resolved == Path("/"):
        raise ValueError("filesystem root cannot be a package output")
    return str(resolved)


def _selected_profiles(selected_profiles: Iterable[str] | None) -> list[str]:
    probe = build_plan(
        name="Agentic Knowledge OS",
        workspace="/replace-with-user-workspace",
        selected_profiles=selected_profiles,
    )
    return list(probe["brain"]["profiles"])


def _package_files(host: str, profile_ids: list[str]) -> list[str]:
    common = [
        "README.md",
        "LICENSE",
        "NOTICE",
        f"{SKILL_ROOT}/SKILL.md",
        f"{REFERENCE_ROOT}/constitution.md",
        f"{REFERENCE_ROOT}/orientation.md",
        f"{REFERENCE_ROOT}/core8.json",
        f"{REFERENCE_ROOT}/type-kernel.json",
        f"{REFERENCE_ROOT}/operating-policy.json",
        f"{REFERENCE_ROOT}/compact-runtime-contract.md",
        f"{REFERENCE_ROOT}/artifact-request.schema.json",
        f"{REFERENCE_ROOT}/governance-benchmark.json",
        f"{REFERENCE_ROOT}/behavioral-experiment.json",
        f"{REFERENCE_ROOT}/behavioral-rubric.json",
        f"{REFERENCE_ROOT}/host-contract.json",
        *(
            f"{REFERENCE_ROOT}/profiles/{identifier.removeprefix('akos.core8.')}.md"
            for identifier in profile_ids
        ),
    ]
    native = ["plugin.json"] if host == "hermes" else ["package.json", "prompts/orient-extended-mind.md"]
    return [*native, *common, PACKAGE_MANIFEST_PATH]


def build_host_package_plan(
    *,
    name: str,
    output_root: str,
    host: str,
    selected_profiles: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return a deterministic host-package plan without writing it."""

    if host not in PACKAGE_HOSTS:
        raise ValueError("host package must target hermes or pi")
    normalized_name = " ".join(name.split())
    if not normalized_name or len(normalized_name) > 80:
        raise ValueError("package name must contain 1 to 80 visible characters")
    profile_ids = _selected_profiles(selected_profiles)
    unsigned = {
        "schema": "akos.host-package-plan.v1",
        "name": normalized_name,
        "host": host,
        "output_root": _normalized_output_root(output_root),
        "profiles": profile_ids,
        "files": _package_files(host, profile_ids),
        "effects": {
            "package_write": "exact-package-id-confirmation-required",
            "host_installation": "held",
            "host_enablement": "held",
            "provider_use": "held",
            "network_use": "held",
        },
        "review_status": "review-required",
        "verified": False,
    }
    return {
        "schema": unsigned["schema"],
        "package_id": object_digest(unsigned),
        **{key: value for key, value in unsigned.items() if key != "schema"},
    }


def validate_host_package_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Reject a changed or digest-mismatched host-package plan."""

    required = {
        "schema",
        "package_id",
        "name",
        "host",
        "output_root",
        "profiles",
        "files",
        "effects",
        "review_status",
        "verified",
    }
    if set(plan) != required or plan.get("schema") != "akos.host-package-plan.v1":
        raise ValueError("unsupported or open host-package plan")
    rebuilt = build_host_package_plan(
        name=plan["name"],
        output_root=plan["output_root"],
        host=plan["host"],
        selected_profiles=plan["profiles"],
    )
    if plan != rebuilt:
        raise ValueError("host-package plan digest or fields changed")
    return plan


def _skill_text(host: str) -> str:
    host_note = (
        "Hermes loads this skill through an Agent Plugins v1 package. Installation and enablement remain separate human actions."
        if host == "hermes"
        else "Pi loads this skill from the package manifest. Package installation and project trust remain separate human actions."
    )
    return f"""---
name: agentic-knowledge-os
description: Orient and govern a user-owned extended mind.
license: PolyForm-Noncommercial-1.0.0
metadata:
  version: "{PACKAGE_VERSION}"
  author: "Scott Rallya and Hearth & Code"
  platforms: "linux, macos, windows"
  tags: "knowledge-engineering, governance, provenance, core8"
---

# Agentic Knowledge OS

Use this skill when a person wants to design, orient, review, or evolve a governed knowledge workspace across research, notes, evidence, decisions, projects, and workflows.

{host_note}

## Operating posture

- Treat the person or named source owner as the authority for accepted meaning.
- Keep source, evidence, inference, hypothesis, proposal, decision, projection, receipt, and unknown distinct.
- Keep planning, local writes, host activation, provider use, and external effects as independent gates.
- Select one primary Core8 role only when its admission test matches the request.
- Return a bounded hold when source, ownership, sensitivity, or authority is unresolved.
- Never infer diagnosis, stable traits, preferences, credentials, or consent from stored material.

## Orientation

For first use or a materially changed purpose, read `references/orientation.md` and ask only the questions needed for the current decision. Do not create accepted meaning or write knowledge automatically from the answers.

Read `references/constitution.md` before proposing durable workspace law or consequential operations. It is the shared RFC-style governance surface.

## Role selection

Read `references/core8.json` to identify the matching attention signal and admission test. Load only the selected role under `references/profiles/` unless a handoff requires another. The Coordinator composes boundaries and returns; it is not a super-role.

## Typed work

Read `references/type-kernel.json` when a transformation, relation, state transition, or machine-readable record is needed. Read `references/operating-policy.json` when semantic orientation, Operational Intelligence, or an effect gate materially changes the result.

## Evaluation

Read `references/governance-benchmark.json` only when evaluating routing and policy adherence. Read `references/behavioral-experiment.json` and `references/behavioral-rubric.json` before a matched comparison of structured role-vocabulary prompting, constitution-only prompting, and the full AKOS package. The structured baseline includes the common response schema and role identifiers but no AKOS governance or profile contracts. Record adapter-neutral evidence and score it with the source distribution. A policy-conformance score, fixture replay, behavioral estimate, or byte digest does not establish universal usefulness, semantic correctness, safety, or causality.

## Host boundary

Read `references/host-contract.json` before proposing host integration. A package being discoverable does not authorize installation, enablement, profile changes, provider configuration, credentials, network use, or publication.

## Return

State the objective, achieved and unresolved state, sources, role used, evidence, affected paths, performed and unperformed effects, proof limits, and smallest safe next action.
"""


def _pi_prompt() -> str:
    return """---
description: Orient a governed user-owned extended mind
---
Use the `agentic-knowledge-os` skill to orient a governed extended mind for ${ARGUMENTS:-the current workspace}. Begin with purpose, source ownership, semantic authority, sensitivity, allowed effects, and the desired return. Propose a bounded Core8 route and inspectable structure. Do not install, write, activate, configure a provider, or accept meaning without the corresponding explicit human gate.
"""


def _readme(host: str) -> str:
    if host == "hermes":
        install = """Validate the generated package without installing it:

```bash
hermes plugins doctor /absolute/path/to/hermes-agentic-knowledge-os --ci
```

For local integration, copy the reviewed package directory to the active profile's `plugins/agentic-knowledge-os/` directory, then inspect it with `hermes plugins list`. Enablement remains a separate action:

```bash
hermes plugins enable agentic-knowledge-os
```

For Git distribution, publish this package directory as the repository root and install it disabled with `hermes plugins install owner/repository --no-enable`."""
    else:
        install = """Install the reviewed package from a local path:

```bash
pi install /absolute/path/to/pi-agentic-knowledge-os
```

Or publish this package directory as the repository root and install a pinned Git ref:

```bash
pi install git:github.com/owner/repository@v0.3.0-alpha.1
```

The package provides the `agentic-knowledge-os` skill and `/orient-extended-mind` prompt template. Use project-local `-l` only when you deliberately want to amend `.pi/settings.json`."""
    return f"""# Agentic Knowledge OS for {host.title()}

This is a generated, host-native projection of the Agentic Knowledge OS Core8 source. It contains no `.akos` directory. The canonical public source is https://github.com/hearthandcode/agentic-knowledge-os.

## Integrate

{install}

## Boundaries

Generation does not install or enable this package. Installation does not authorize provider configuration, credentials, network use, workspace writes, semantic acceptance, or external effects. Review `skills/agentic-knowledge-os/SKILL.md`, the referenced constitution, and `package-manifest.json` before integration.

The package is source-level and `verified: false`. Host validation supports only the exact checks reported; it does not establish usefulness, safety, semantic correctness, or production compatibility.
"""


def _replace_portable_paths(text: str) -> str:
    return (
        text.replace("`.akos/ORIENTATION.md`", "`references/orientation.md`")
        .replace("`.akos/type-kernel.json`", "`references/type-kernel.json`")
    )


def compile_host_package(plan: dict[str, Any]) -> dict[str, str]:
    """Render one Hermes or Pi package in memory without writing it."""

    validate_host_package_plan(plan)
    host = plan["host"]
    portable_plan = build_plan(
        name=plan["name"],
        workspace="/replace-with-user-workspace",
        host=host,
        selected_profiles=plan["profiles"],
    )
    portable = compile_bundle(portable_plan)
    bundle: dict[str, str] = {
        "README.md": _readme(host),
        "LICENSE": files(DATA_PACKAGE).joinpath("software-license.txt").read_text(encoding="utf-8"),
        "NOTICE": files(DATA_PACKAGE).joinpath("package-notice.txt").read_text(encoding="utf-8"),
        f"{SKILL_ROOT}/SKILL.md": _skill_text(host),
        f"{REFERENCE_ROOT}/constitution.md": _replace_portable_paths(portable["AGENTS.md"]),
        f"{REFERENCE_ROOT}/orientation.md": portable[".akos/ORIENTATION.md"],
        f"{REFERENCE_ROOT}/core8.json": portable[".akos/core8.json"],
        f"{REFERENCE_ROOT}/type-kernel.json": portable[".akos/type-kernel.json"],
        f"{REFERENCE_ROOT}/operating-policy.json": portable[".akos/operating-policy.json"],
        f"{REFERENCE_ROOT}/compact-runtime-contract.md": files(DATA_PACKAGE).joinpath("compact-runtime-contract.md").read_text(encoding="utf-8"),
        f"{REFERENCE_ROOT}/artifact-request.schema.json": files(DATA_PACKAGE).joinpath("artifact-request.schema.json").read_text(encoding="utf-8"),
        f"{REFERENCE_ROOT}/governance-benchmark.json": json.dumps(
            benchmark_suite(), ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n",
        f"{REFERENCE_ROOT}/behavioral-experiment.json": json.dumps(
            behavioral_experiment_plan(), ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n",
        f"{REFERENCE_ROOT}/behavioral-rubric.json": json.dumps(
            behavioral_rubric(), ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n",
        f"{REFERENCE_ROOT}/host-contract.json": portable[f".akos/host/{host}.json"],
    }
    for profile_id in plan["profiles"]:
        slug = profile_id.removeprefix("akos.core8.")
        bundle[f"{REFERENCE_ROOT}/profiles/{slug}.md"] = portable[f".akos/profiles/{slug}.md"]

    if host == "hermes":
        bundle["plugin.json"] = json.dumps(
            {
                "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
                "name": "agentic-knowledge-os",
                "version": PACKAGE_VERSION,
                "description": "Governed Core8 orientation for a user-owned extended mind.",
                "author": {"name": "Scott Rallya and Hearth & Code"},
                "homepage": "https://github.com/hearthandcode/agentic-knowledge-os",
                "repository": "https://github.com/hearthandcode/agentic-knowledge-os",
                "license": "PolyForm-Noncommercial-1.0.0",
                "keywords": ["knowledge-engineering", "governance", "core8", "extended-mind"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
    else:
        bundle["package.json"] = json.dumps(
            {
                "name": "agentic-knowledge-os-pi",
                "version": PACKAGE_VERSION,
                "description": "Governed Core8 orientation for a user-owned extended mind.",
                "license": "PolyForm-Noncommercial-1.0.0",
                "keywords": ["pi-package", "knowledge-engineering", "ai-agents", "core8"],
                "repository": {
                    "type": "git",
                    "url": "https://github.com/hearthandcode/agentic-knowledge-os.git",
                },
                "pi": {
                    "skills": ["./skills"],
                    "prompts": ["./prompts"],
                },
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
        bundle["prompts/orient-extended-mind.md"] = _pi_prompt()

    expected_without_manifest = set(plan["files"]) - {PACKAGE_MANIFEST_PATH}
    if set(bundle) != expected_without_manifest:
        raise ValueError("host package and planned file inventory differ")
    if any(".akos" in path for path in bundle):
        raise ValueError("host-native package unexpectedly contains a .akos path")

    manifest = {
        "schema": "akos.host-package-manifest.v1",
        "package_id": plan["package_id"],
        "source_version": PACKAGE_VERSION,
        "host": host,
        "profiles": plan["profiles"],
        "owned_files": {path: content_digest(content) for path, content in sorted(bundle.items())},
        "host_installation": "not-performed",
        "host_enablement": "not-performed",
        "review_status": "review-required",
        "verified": False,
    }
    bundle[PACKAGE_MANIFEST_PATH] = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return {path: bundle[path] for path in plan["files"]}


def _safe_package_path(relative: str) -> PurePosixPath:
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe package path: {relative}")
    return path


def _atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("x", encoding="utf-8", newline="") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def write_host_package(plan: dict[str, Any], confirmation: str) -> dict[str, Any]:
    """Write one reviewed package to a new or empty local directory."""

    validate_host_package_plan(plan)
    root = Path(plan["output_root"])
    if confirmation != plan["package_id"]:
        return {"status": "blocked", "package_id": plan["package_id"], "findings": ["exact package-ID confirmation is required"]}
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        return {"status": "blocked", "package_id": plan["package_id"], "findings": ["package output must be a regular directory path"]}
    if root.exists() and any(root.iterdir()):
        return {"status": "blocked", "package_id": plan["package_id"], "findings": ["package output directory is not empty"]}
    if not root.exists() and (not root.parent.is_dir() or root.parent.is_symlink()):
        return {"status": "blocked", "package_id": plan["package_id"], "findings": ["package output parent must exist and cannot be a symbolic link"]}

    bundle = compile_host_package(plan)
    root_created = False
    created_files: list[Path] = []
    created_directories: list[Path] = []
    try:
        if not root.exists():
            root.mkdir()
            root_created = True
        for relative, content in bundle.items():
            safe = _safe_package_path(relative)
            path = root.joinpath(*safe.parts)
            parent = path.parent
            missing: list[Path] = []
            while parent != root and not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                created_directories.append(directory)
            if path.exists() or path.is_symlink():
                raise OSError(f"planned package path collision: {relative}")
            _atomic_write(path, content)
            created_files.append(path)
    except OSError as error:
        for path in reversed(created_files):
            path.unlink(missing_ok=True)
        for directory in reversed(created_directories):
            try:
                directory.rmdir()
            except OSError:
                pass
        if root_created:
            try:
                root.rmdir()
            except OSError:
                pass
        return {"status": "blocked", "package_id": plan["package_id"], "findings": [f"package write failed: {error}"]}

    verification = verify_host_package(root)
    return {
        "status": "written" if verification["status"] == "clear" else "blocked",
        "package_id": plan["package_id"],
        "host": plan["host"],
        "output_root": str(root),
        "changed_paths": list(bundle),
        "findings": verification["findings"],
    }


def verify_host_package(package_root: str | Path) -> dict[str, Any]:
    """Verify the generated package manifest and its owned file bytes."""

    root = Path(package_root).resolve(strict=False)
    manifest_path = root / PACKAGE_MANIFEST_PATH
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return {"status": "blocked", "output_root": str(root), "findings": [f"package manifest unavailable: {error}"]}
    required = {
        "schema", "package_id", "source_version", "host", "profiles", "owned_files",
        "host_installation", "host_enablement", "review_status", "verified",
    }
    if set(manifest) != required or manifest.get("schema") != "akos.host-package-manifest.v1":
        return {"status": "blocked", "output_root": str(root), "findings": ["package manifest shape is invalid"]}
    findings: list[str] = []
    for relative, expected in manifest["owned_files"].items():
        try:
            safe = _safe_package_path(relative)
            path = root.joinpath(*safe.parts)
            if path.is_symlink() or not path.is_file():
                findings.append(f"owned file is missing or not regular: {relative}")
            elif content_digest(path.read_text(encoding="utf-8")) != expected:
                findings.append(f"owned file digest mismatch: {relative}")
        except (OSError, UnicodeDecodeError, ValueError) as error:
            findings.append(f"owned file cannot be verified: {relative}: {error}")
    return {
        "status": "clear" if not findings else "blocked",
        "output_root": str(root),
        "package_id": manifest.get("package_id"),
        "host": manifest.get("host"),
        "findings": findings or ["manifest-owned host package files match"],
    }
