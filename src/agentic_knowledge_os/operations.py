"""Manifest-owned workspace operations with explicit confirmation gates."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .compiler import (
    HOSTS,
    INSTALL_MANIFEST_PATH,
    WORKSPACE_DIRECTORIES,
    byte_digest,
    compile_bundle,
    content_digest,
    object_digest,
    core8_profiles,
    validate_plan,
)


SOURCE_VERSION = "0.3.0-alpha.1"
CONTROL_DIRECTORIES = (".akos", ".akos/host", ".akos/profiles")
SUCCESS_STATES = {"applied", "already-applied", "clear", "removed"}


def _receipt(
    operation: str,
    status: str,
    workspace_root: str,
    *,
    plan_id: str | None = None,
    manifest_digest: str | None = None,
    changed_paths: list[str] | None = None,
    preserved_paths: list[str] | None = None,
    findings: list[str] | None = None,
) -> dict[str, Any]:
    changed = changed_paths or []
    return {
        "schema": "akos.operation-receipt.v1",
        "operation": operation,
        "status": status,
        "workspace_root": workspace_root,
        "plan_id": plan_id,
        "manifest_digest": manifest_digest,
        "changed_paths": changed,
        "preserved_paths": preserved_paths or [],
        "findings": findings or [],
        "effects": {
            "workspace_write": "performed" if status in {"applied", "removed"} or changed else "none",
            "host_activation": "not-performed",
            "provider_use": "not-performed",
            "network_use": "not-performed",
        },
        "verified": False,
    }


def _expected_owned_paths(host: str, profiles: list[str]) -> set[str]:
    return {
        "AGENTS.md",
        "brain.json",
        ".akos/core8.json",
        ".akos/type-kernel.json",
        ".akos/operating-policy.json",
        ".akos/ORIENTATION.md",
        f".akos/host/{host}.json",
        *(f".akos/profiles/{identifier.removeprefix('akos.core8.')}.md" for identifier in profiles),
    }


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or "." in path.parts:
        raise ValueError(f"unsafe manifest path: {value}")
    return path


def _symlink_component(root: Path, relative: Path, *, include_final: bool = True) -> str | None:
    candidate = root
    parts = relative.parts if include_final else relative.parts[:-1]
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            return str(candidate.relative_to(root))
    return None


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _atomic_write(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _manifest_for(plan: dict[str, Any], bundle: dict[str, str]) -> dict[str, Any]:
    unsigned = {
        "schema": "akos.install-manifest.v2",
        "source_version": SOURCE_VERSION,
        "plan_id": plan["plan_id"],
        "workspace_root": plan["brain"]["workspace_root"],
        "host": plan["brain"]["host"],
        "profiles": plan["brain"]["profiles"],
        "owned_files": {path: content_digest(bundle[path]) for path in sorted(bundle)},
        "created_directories": [*WORKSPACE_DIRECTORIES, *CONTROL_DIRECTORIES],
        "review_status": "review-required",
        "verified": False,
        "live_host_activation": "none",
    }
    return {
        "schema": unsigned["schema"],
        "manifest_digest": object_digest(unsigned),
        **{key: value for key, value in unsigned.items() if key != "schema"},
    }


def validate_install_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate the closed manifest before trusting its ownership claims."""

    required = {
        "schema",
        "manifest_digest",
        "source_version",
        "plan_id",
        "workspace_root",
        "host",
        "profiles",
        "owned_files",
        "created_directories",
        "review_status",
        "verified",
        "live_host_activation",
    }
    if set(manifest) != required:
        raise ValueError("install manifest fields are not closed")
    if manifest.get("schema") != "akos.install-manifest.v2":
        raise ValueError("unsupported install manifest schema")
    if manifest.get("source_version") != SOURCE_VERSION:
        raise ValueError("unsupported install manifest source version")
    if manifest.get("host") not in HOSTS:
        raise ValueError("unsupported install manifest host")
    if not _is_digest(manifest.get("plan_id")):
        raise ValueError("invalid install manifest plan identity")
    root = Path(manifest.get("workspace_root", ""))
    if not root.is_absolute() or root == Path("/") or str(root.resolve(strict=False)) != str(root):
        raise ValueError("install manifest workspace root is not canonical")
    owned_files = manifest.get("owned_files")
    profiles = manifest.get("profiles")
    available = [profile["id"] for profile in core8_profiles()]
    if not isinstance(profiles, list) or not profiles or not all(isinstance(item, str) for item in profiles):
        raise ValueError("install manifest profile inventory is invalid")
    if profiles != [item for item in available if item in profiles]:
        raise ValueError("install manifest profile inventory is invalid")
    if len(profiles) != len(set(profiles)) or not set(profiles).issubset(available):
        raise ValueError("install manifest profile inventory is invalid")
    if not isinstance(owned_files, dict) or set(owned_files) != _expected_owned_paths(manifest["host"], profiles):
        raise ValueError("install manifest ownership inventory changed")
    for relative, digest in owned_files.items():
        _safe_relative_path(relative)
        if not _is_digest(digest):
            raise ValueError("invalid owned-file digest")
    expected_directories = [*WORKSPACE_DIRECTORIES, *CONTROL_DIRECTORIES]
    if manifest.get("created_directories") != expected_directories:
        raise ValueError("install manifest directory inventory changed")
    if manifest.get("review_status") != "review-required" or manifest.get("verified") is not False:
        raise ValueError("install manifest must remain review-required and unverified")
    if manifest.get("live_host_activation") != "none":
        raise ValueError("install manifest cannot claim host activation")
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_digest"}
    if manifest.get("manifest_digest") != object_digest(unsigned):
        raise ValueError("install manifest digest mismatch")
    return manifest


def _load_manifest(workspace: Path) -> dict[str, Any]:
    manifest_path = workspace / INSTALL_MANIFEST_PATH
    component = _symlink_component(workspace, Path(INSTALL_MANIFEST_PATH))
    if component:
        raise ValueError(f"install manifest path contains a symbolic link: {component}")
    if not manifest_path.is_file():
        raise ValueError("install manifest is missing")
    manifest = validate_install_manifest(_read_json(manifest_path))
    if manifest["workspace_root"] != str(workspace):
        raise ValueError("install manifest belongs to another workspace")
    return manifest


def _remaining_paths(workspace: Path) -> list[str]:
    if not workspace.is_dir():
        return []
    remaining: list[str] = []
    for current, directories, files in os.walk(workspace, topdown=True, followlinks=False):
        current_path = Path(current)
        for name in sorted((*directories, *files)):
            remaining.append(str((current_path / name).relative_to(workspace)))
    return sorted(set(remaining))


def verify_install(workspace: str | Path) -> dict[str, Any]:
    """Check only the manifest and the bytes it claims to own."""

    root = Path(workspace).resolve(strict=False)
    try:
        manifest = _load_manifest(root)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        return _receipt("verify", "blocked", str(root), findings=[str(error)])
    findings: list[str] = []
    for relative, expected_digest in manifest["owned_files"].items():
        relative_path = _safe_relative_path(relative)
        path = root / relative_path
        component = _symlink_component(root, relative_path)
        if component:
            findings.append(f"owned path contains a symbolic link: {relative}: {component}")
        elif not path.is_file():
            findings.append(f"owned file is missing or not a regular file: {relative}")
        else:
            try:
                observed = byte_digest(path.read_bytes())
            except OSError as error:
                findings.append(f"owned file cannot be read: {relative}: {error}")
            else:
                if observed != expected_digest:
                    findings.append(f"owned file digest mismatch: {relative}")
    return _receipt(
        "verify",
        "clear" if not findings else "blocked",
        str(root),
        plan_id=manifest["plan_id"],
        manifest_digest=manifest["manifest_digest"],
        preserved_paths=_remaining_paths(root),
        findings=findings or ["manifest identity and all owned file digests match"],
    )


def apply_plan(plan: dict[str, Any], confirmation: str) -> dict[str, Any]:
    """Create a clean workspace only after exact plan-ID confirmation."""

    validate_plan(plan)
    root = Path(plan["brain"]["workspace_root"])
    if confirmation != plan["plan_id"]:
        return _receipt(
            "apply",
            "blocked",
            str(root),
            plan_id=plan["plan_id"],
            findings=["exact plan-ID confirmation is required"],
        )
    if root.is_symlink():
        return _receipt("apply", "blocked", str(root), plan_id=plan["plan_id"], findings=["workspace cannot be a symbolic link"])
    if root.exists() and not root.is_dir():
        return _receipt("apply", "blocked", str(root), plan_id=plan["plan_id"], findings=["workspace target is not a directory"])
    manifest_path = root / INSTALL_MANIFEST_PATH
    if manifest_path.exists() or manifest_path.is_symlink():
        try:
            manifest = _load_manifest(root)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            return _receipt("apply", "blocked", str(root), plan_id=plan["plan_id"], findings=[str(error)])
        if manifest["plan_id"] != plan["plan_id"]:
            return _receipt(
                "apply",
                "blocked",
                str(root),
                plan_id=plan["plan_id"],
                manifest_digest=manifest["manifest_digest"],
                findings=["workspace is owned by a different plan"],
            )
        verification = verify_install(root)
        if verification["status"] == "clear":
            verification["operation"] = "apply"
            verification["status"] = "already-applied"
        return verification
    if root.exists() and any(root.iterdir()):
        return _receipt(
            "apply",
            "blocked",
            str(root),
            plan_id=plan["plan_id"],
            preserved_paths=_remaining_paths(root),
            findings=["non-empty workspace has no trusted Agentic Knowledge OS manifest"],
        )
    if not root.exists() and (not root.parent.is_dir() or root.parent.is_symlink()):
        return _receipt(
            "apply",
            "blocked",
            str(root),
            plan_id=plan["plan_id"],
            findings=["workspace parent must already exist and cannot be a symbolic link"],
        )

    bundle = compile_bundle(plan)
    manifest = _manifest_for(plan, bundle)
    created_files: list[Path] = []
    created_directories: list[Path] = []
    root_created = False
    try:
        if not root.exists():
            root.mkdir()
            root_created = True
        for relative in manifest["created_directories"]:
            directory = root / _safe_relative_path(relative)
            if directory.exists() or directory.is_symlink():
                raise OSError(f"planned directory collision: {relative}")
            directory.mkdir()
            created_directories.append(directory)
        for relative, content in bundle.items():
            path = root / _safe_relative_path(relative)
            if path.exists() or path.is_symlink():
                raise OSError(f"planned file collision: {relative}")
            _atomic_write(path, content)
            created_files.append(path)
        _atomic_write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        created_files.append(manifest_path)
    except OSError as error:
        for path in reversed(created_files):
            path.unlink(missing_ok=True)
        for directory in sorted(created_directories, key=lambda item: len(item.parts), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass
        if root_created:
            try:
                root.rmdir()
            except OSError:
                pass
        return _receipt("apply", "blocked", str(root), plan_id=plan["plan_id"], findings=[f"workspace creation failed: {error}"])

    verification = verify_install(root)
    if verification["status"] != "clear":
        cleanup = remove_install(root, manifest["manifest_digest"], force_owned_changes=True, operation="rollback")
        return _receipt(
            "apply",
            "blocked",
            str(root),
            plan_id=plan["plan_id"],
            manifest_digest=manifest["manifest_digest"],
            changed_paths=cleanup["changed_paths"],
            preserved_paths=cleanup["preserved_paths"],
            findings=["post-write verification failed and transactional rollback was attempted", *verification["findings"]],
        )
    return _receipt(
        "apply",
        "applied",
        str(root),
        plan_id=plan["plan_id"],
        manifest_digest=manifest["manifest_digest"],
        changed_paths=[
            *manifest["created_directories"],
            *manifest["owned_files"].keys(),
            INSTALL_MANIFEST_PATH,
        ],
        findings=["manifest-owned workspace created and owned bytes rechecked"],
    )


def remove_install(
    workspace: str | Path,
    confirmation: str,
    *,
    force_owned_changes: bool = False,
    operation: str = "uninstall",
) -> dict[str, Any]:
    """Remove only manifest-owned files and empty installer-created directories."""

    if operation not in {"uninstall", "rollback"}:
        raise ValueError("unsupported removal operation")
    root = Path(workspace).resolve(strict=False)
    try:
        manifest = _load_manifest(root)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        return _receipt(operation, "blocked", str(root), findings=[str(error)])
    if confirmation != manifest["manifest_digest"]:
        return _receipt(
            operation,
            "blocked",
            str(root),
            plan_id=manifest["plan_id"],
            manifest_digest=manifest["manifest_digest"],
            findings=["exact manifest-digest confirmation is required"],
        )
    verification = verify_install(root)
    if verification["status"] != "clear" and not force_owned_changes:
        verification["operation"] = operation
        verification["findings"] = [
            "owned files changed; removal requires --force-owned-changes",
            *verification["findings"],
        ]
        return verification

    paths_to_remove: list[Path] = []
    for relative in manifest["owned_files"]:
        relative_path = _safe_relative_path(relative)
        component = _symlink_component(root, relative_path, include_final=False)
        if component:
            return _receipt(
                operation,
                "blocked",
                str(root),
                plan_id=manifest["plan_id"],
                manifest_digest=manifest["manifest_digest"],
                findings=[f"owned file parent contains a symbolic link and will not be traversed: {component}"],
            )
        path = root / relative_path
        if path.exists() and path.is_dir() and not path.is_symlink():
            return _receipt(
                operation,
                "blocked",
                str(root),
                plan_id=manifest["plan_id"],
                manifest_digest=manifest["manifest_digest"],
                findings=[f"owned file path is now a directory and will not be removed: {relative}"],
            )
        paths_to_remove.append(path)
    changed: list[str] = []
    try:
        for path in paths_to_remove:
            if path.exists() or path.is_symlink():
                path.unlink()
                changed.append(str(path.relative_to(root)))
        manifest_path = root / INSTALL_MANIFEST_PATH
        manifest_path.unlink()
        changed.append(INSTALL_MANIFEST_PATH)
        for relative in reversed(manifest["created_directories"]):
            directory = root / _safe_relative_path(relative)
            try:
                directory.rmdir()
            except OSError:
                continue
            changed.append(relative)
    except OSError as error:
        return _receipt(
            operation,
            "blocked",
            str(root),
            plan_id=manifest["plan_id"],
            manifest_digest=manifest["manifest_digest"],
            changed_paths=changed,
            preserved_paths=_remaining_paths(root),
            findings=[f"partial removal stopped: {error}"],
        )
    return _receipt(
        operation,
        "removed",
        str(root),
        plan_id=manifest["plan_id"],
        manifest_digest=manifest["manifest_digest"],
        changed_paths=changed,
        preserved_paths=_remaining_paths(root),
        findings=["only manifest-owned files and empty installer-created directories were removed"],
    )


def uninstall(workspace: str | Path, confirmation: str, *, force_owned_changes: bool = False) -> dict[str, Any]:
    return remove_install(workspace, confirmation, force_owned_changes=force_owned_changes, operation="uninstall")


def rollback(workspace: str | Path, confirmation: str, *, force_owned_changes: bool = False) -> dict[str, Any]:
    return remove_install(workspace, confirmation, force_owned_changes=force_owned_changes, operation="rollback")


def _is_digest(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 71 or not value.startswith("sha256:"):
        return False
    return all(character in "0123456789abcdef" for character in value.removeprefix("sha256:"))
