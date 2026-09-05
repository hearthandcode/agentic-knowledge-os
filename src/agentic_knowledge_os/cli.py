"""Command-line surface for planning and manifest-owned local installation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .compiler import build_plan, compile_bundle, core8_profiles, operating_policy, type_kernel
from .artifact_contract import compile_request, evaluate_attempts, strict_json
from .evaluation import (
    audit_governance_scorer,
    benchmark_suite,
    behavioral_experiment_plan,
    behavioral_rubric,
    score_behavioral_experiment,
    score_trace_set,
    synthetic_behavioral_observations,
)
from .host_packages import (
    build_host_package_plan,
    compile_host_package,
    verify_host_package,
    write_host_package,
)
from .operations import SUCCESS_STATES, apply_plan, rollback, uninstall, verify_install


def _profile_selection(raw: str | None) -> list[str] | None:
    if raw is None:
        return None
    return [item.strip() for item in raw.split(",") if item.strip()]


def _add_plan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--name", required=True, help="Human-readable brain name")
    parser.add_argument("--workspace", required=True, help="Absolute proposed workspace path")
    parser.add_argument("--host", choices=("neutral", "hermes", "pi", "exocore"), default="neutral")
    parser.add_argument("--profiles", help="Comma-separated Core8 profile IDs; defaults to all eight")


def _add_package_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--name", default="Agentic Knowledge OS", help="Human-readable projected brain name")
    parser.add_argument("--output", required=True, help="Absolute proposed package output path")
    parser.add_argument("--host", choices=("hermes", "pi"), required=True)
    parser.add_argument("--profiles", help="Comma-separated Core8 profile IDs; defaults to all eight")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="akos", description="Plan a governed agentic knowledge workspace")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("profiles", help="List the public Core8 profile registry")
    subparsers.add_parser("policy", help="Print the semantic, operational-intelligence, and governance policy")
    subparsers.add_parser("types", help="Print the closed public type kernel")
    artifact_prompt = subparsers.add_parser("artifact-prompt", help="Compile a compact artifact prompt and output schema without calling a provider")
    artifact_prompt.add_argument("--request", required=True, help="Path to an artifact request JSON file")
    artifact_prompt.add_argument("--text", action="store_true", help="Print only the model-facing prompt")
    artifact_check = subparsers.add_parser("artifact-check", help="Gate candidate responses against consumer shape and source checks")
    artifact_check.add_argument("--request", required=True, help="Path to an artifact request JSON file")
    artifact_check.add_argument("--response", required=True, action="append", help="Response file; repeat once for a replacement attempt")
    subparsers.add_parser("benchmark-suite", help="Print the provider-neutral governance benchmark")
    benchmark_score = subparsers.add_parser("benchmark-score", help="Score an adapter-neutral evaluation trace set")
    benchmark_score.add_argument("--traces", required=True, help="Path to an evaluation trace-set JSON file")
    benchmark_audit = subparsers.add_parser("benchmark-audit", help="Mutation-test the governance scorer")
    benchmark_audit.add_argument("--traces", required=True, help="Path to a conformant trace-set JSON file")
    subparsers.add_parser("experiment-plan", help="Print the preregistered matched behavioral comparison")
    subparsers.add_parser("experiment-rubric", help="Print normalized behavioral metric definitions and methods")
    subparsers.add_parser("experiment-canary", help="Exercise behavioral comparison math with synthetic measurements")
    experiment_score = subparsers.add_parser("experiment-score", help="Score matched behavioral observations")
    experiment_score.add_argument("--observations", required=True, help="Path to behavioral-observations JSON")
    _add_plan_arguments(subparsers.add_parser("orient", help="Print the first-run orientation docket without writing"))
    _add_plan_arguments(subparsers.add_parser("plan", help="Print a deterministic no-write bootstrap plan"))
    _add_plan_arguments(subparsers.add_parser("render", help="Print proposed file contents without writing them"))
    _add_package_arguments(subparsers.add_parser("package-plan", help="Print a no-write host-package plan"))
    _add_package_arguments(subparsers.add_parser("package-render", help="Print proposed host-package files without writing"))
    package_apply = subparsers.add_parser("package-apply", help="Write an inspected host-package plan")
    package_apply.add_argument("--plan-file", required=True, help="Path to a host-package plan JSON file")
    package_apply.add_argument("--confirm-package", required=True, help="Exact package ID shown by package-plan")
    package_verify = subparsers.add_parser("package-verify", help="Check a generated host package against its manifest")
    package_verify.add_argument("--package-root", required=True, help="Generated host-package directory")
    apply_parser = subparsers.add_parser("apply", help="Apply an inspected plan to a clean local workspace")
    apply_parser.add_argument("--plan-file", required=True, help="Path to a bootstrap plan JSON file")
    apply_parser.add_argument("--confirm-plan", required=True, help="Exact plan ID shown by the plan command")
    verify_parser = subparsers.add_parser("verify", help="Check a workspace against its ownership manifest")
    verify_parser.add_argument("--workspace", required=True, help="Installed workspace path")
    for command in ("uninstall", "rollback"):
        removal = subparsers.add_parser(command, help=f"{command.title()} manifest-owned workspace files")
        removal.add_argument("--workspace", required=True, help="Installed workspace path")
        removal.add_argument("--confirm-manifest", required=True, help="Exact manifest digest from apply or verify")
        removal.add_argument(
            "--force-owned-changes",
            action="store_true",
            help="Remove changed owned files; user-created files remain preserved",
        )
    return parser


def _print_receipt(receipt: dict, success_states: set[str] | None = None) -> int:
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["status"] in (success_states or SUCCESS_STATES) else 2


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command in {"artifact-prompt", "artifact-check"}:
        try:
            request = strict_json(Path(args.request).read_text(encoding="utf-8"))
            if args.command == "artifact-prompt":
                result = compile_request(request)
                print(result["prompt"] if args.text else json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
                return 0
            attempts = [Path(path).read_text(encoding="utf-8") for path in args.response]
            result = evaluate_attempts(request, attempts)
        except (OSError, UnicodeError, ValueError, RecursionError) as error:
            raise SystemExit(str(error)) from error
        return _print_receipt(result, {"valid-candidate"})
    if args.command == "profiles":
        print(json.dumps(list(core8_profiles()), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "policy":
        print(json.dumps(operating_policy(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "types":
        print(json.dumps(type_kernel(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "benchmark-suite":
        print(json.dumps(benchmark_suite(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "benchmark-score":
        try:
            trace_set = json.loads(Path(args.traces).read_text(encoding="utf-8"))
            if not isinstance(trace_set, dict):
                raise ValueError("evaluation trace set must be a JSON object")
            receipt = score_trace_set(trace_set)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise SystemExit(str(error)) from error
        return _print_receipt(receipt, {"passed"})
    if args.command == "benchmark-audit":
        try:
            trace_set = json.loads(Path(args.traces).read_text(encoding="utf-8"))
            if not isinstance(trace_set, dict):
                raise ValueError("evaluation trace set must be a JSON object")
            receipt = audit_governance_scorer(trace_set)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise SystemExit(str(error)) from error
        return _print_receipt(receipt, {"passed"})
    if args.command == "experiment-plan":
        print(json.dumps(behavioral_experiment_plan(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "experiment-rubric":
        print(json.dumps(behavioral_rubric(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "experiment-canary":
        plan = behavioral_experiment_plan()
        receipt = score_behavioral_experiment(synthetic_behavioral_observations(plan), plan)
        return _print_receipt(receipt, {"canary-only"})
    if args.command == "experiment-score":
        try:
            observations = json.loads(Path(args.observations).read_text(encoding="utf-8"))
            if not isinstance(observations, dict):
                raise ValueError("behavioral observations must be a JSON object")
            receipt = score_behavioral_experiment(observations)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise SystemExit(str(error)) from error
        return _print_receipt(receipt, {"estimated", "partial-estimate", "canary-only"})
    if args.command == "verify":
        return _print_receipt(verify_install(args.workspace))
    if args.command == "package-verify":
        return _print_receipt(verify_host_package(args.package_root))
    if args.command in {"uninstall", "rollback"}:
        operation = uninstall if args.command == "uninstall" else rollback
        return _print_receipt(
            operation(args.workspace, args.confirm_manifest, force_owned_changes=args.force_owned_changes)
        )
    if args.command == "apply":
        try:
            plan = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
            if not isinstance(plan, dict):
                raise ValueError("bootstrap plan must be a JSON object")
            receipt = apply_plan(plan, args.confirm_plan)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise SystemExit(str(error)) from error
        return _print_receipt(receipt)
    if args.command == "package-apply":
        try:
            plan = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
            if not isinstance(plan, dict):
                raise ValueError("host-package plan must be a JSON object")
            receipt = write_host_package(plan, args.confirm_package)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise SystemExit(str(error)) from error
        return _print_receipt(receipt, SUCCESS_STATES | {"written"})
    if args.command in {"package-plan", "package-render"}:
        try:
            package_plan = build_host_package_plan(
                name=args.name,
                output_root=args.output,
                host=args.host,
                selected_profiles=_profile_selection(args.profiles),
            )
        except ValueError as error:
            raise SystemExit(str(error)) from error
        if args.command == "package-plan":
            print(json.dumps(package_plan, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(json.dumps({"plan": package_plan, "files": compile_host_package(package_plan)}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    try:
        plan = build_plan(
            name=args.name,
            workspace=args.workspace,
            host=args.host,
            selected_profiles=_profile_selection(args.profiles),
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if args.command == "plan":
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "orient":
        print(json.dumps({"plan": plan, "orientation": compile_bundle(plan)[".akos/ORIENTATION.md"]}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(json.dumps({"plan": plan, "files": compile_bundle(plan)}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0
