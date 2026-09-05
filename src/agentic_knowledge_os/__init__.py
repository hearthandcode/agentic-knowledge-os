"""Agentic Knowledge OS planning and manifest-owned workspace lifecycle."""

from .compiler import (
    build_plan,
    compile_bundle,
    core8_profiles,
    operating_policy,
    type_kernel,
    validate_brain,
    validate_plan,
)
from .operations import apply_plan, rollback, uninstall, validate_install_manifest, verify_install

__all__ = [
    "apply_plan",
    "build_plan",
    "compile_bundle",
    "core8_profiles",
    "operating_policy",
    "rollback",
    "type_kernel",
    "uninstall",
    "validate_brain",
    "validate_install_manifest",
    "validate_plan",
    "verify_install",
]
__version__ = "0.3.0a1"
