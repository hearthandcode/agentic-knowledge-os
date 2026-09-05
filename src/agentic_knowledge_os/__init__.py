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
from .evaluation import (
    audit_governance_scorer,
    benchmark_suite,
    behavioral_experiment_plan,
    behavioral_rubric,
    build_artifact_identity_ledger,
    score_behavioral_experiment,
    score_trace_set,
    synthetic_behavioral_observations,
    validate_behavioral_experiment_plan,
    validate_behavioral_observations,
    validate_benchmark_suite,
    validate_trace_set,
    verify_artifact_identity_ledger,
)

__all__ = [
    "apply_plan",
    "audit_governance_scorer",
    "benchmark_suite",
    "behavioral_experiment_plan",
    "behavioral_rubric",
    "build_plan",
    "build_artifact_identity_ledger",
    "build_host_package_plan",
    "compile_bundle",
    "compile_host_package",
    "core8_profiles",
    "operating_policy",
    "rollback",
    "score_behavioral_experiment",
    "score_trace_set",
    "synthetic_behavioral_observations",
    "type_kernel",
    "uninstall",
    "validate_brain",
    "validate_benchmark_suite",
    "validate_behavioral_experiment_plan",
    "validate_behavioral_observations",
    "validate_host_package_plan",
    "validate_install_manifest",
    "validate_plan",
    "validate_trace_set",
    "verify_artifact_identity_ledger",
    "verify_install",
    "verify_host_package",
    "write_host_package",
]
__version__ = "0.3.0a1"
