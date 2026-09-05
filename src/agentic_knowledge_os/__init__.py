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
from .host_packages import (
    build_host_package_plan,
    compile_host_package,
    validate_host_package_plan,
    verify_host_package,
    write_host_package,
)

__all__ = [
    "apply_plan",
    "build_plan",
    "build_host_package_plan",
    "compile_bundle",
    "compile_host_package",
    "core8_profiles",
    "operating_policy",
    "rollback",
    "type_kernel",
    "uninstall",
    "validate_brain",
    "validate_host_package_plan",
    "validate_install_manifest",
    "validate_plan",
    "verify_install",
    "verify_host_package",
    "write_host_package",
]
__version__ = "0.3.0a1"
