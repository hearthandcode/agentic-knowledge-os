"""Deterministic bootstrap planning and rendering for Agentic Knowledge OS."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable


DATA_PACKAGE = "agentic_knowledge_os.data"
WORKSPACE_DIRECTORIES = (
    "sources",
    "knowledge",
    "projects",
    "workflows",
    "decisions",
    "evidence",
    "receipts",
    "archive",
)
HOSTS = ("neutral", "hermes", "pi", "exocore")
PHASE_TWO_EFFECTS = {
    "workspace_write": "exact-plan-confirmation-required",
    "installation": "manifest-owned-local-only",
    "enablement": "held",
    "configuration": "held",
    "provider_use": "held",
    "network_use": "held",
    "publication": "held",
}
PHASE_TWO_OMISSIONS = (
    "private Core32 profile bodies",
    "provider and model configuration",
    "credentials and account state",
    "automatic memory write-back",
    "live host activation and profile installation",
)
INSTALL_MANIFEST_PATH = ".akos/install-manifest.json"


def _load_json(name: str) -> dict[str, Any]:
    resource = files(DATA_PACKAGE).joinpath(name)
    return json.loads(resource.read_text(encoding="utf-8"))


def core8_distribution() -> dict[str, Any]:
    distribution = _load_json("core8.json")
    _validate_distribution(distribution)
    return distribution


def core8_profiles() -> tuple[dict[str, Any], ...]:
    return tuple(core8_distribution()["profiles"])


def type_kernel() -> dict[str, Any]:
    kernel = _load_json("type-kernel.json")
    _validate_type_kernel(kernel)
    return kernel


def operating_policy() -> dict[str, Any]:
    policy = _load_json("operating-policy.json")
    _validate_operating_policy(policy)
    return policy


def host_adapters() -> dict[str, dict[str, Any]]:
    adapters = _load_json("adapters.json")
    if set(adapters) != set(HOSTS):
        raise ValueError("adapter registry must define exactly neutral, hermes, pi, and exocore")
    return adapters


def _validate_distribution(distribution: dict[str, Any]) -> None:
    if distribution.get("schema") != "akos.core8-distribution.v2":
        raise ValueError("unsupported Core8 distribution schema")
    profiles = distribution.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 8:
        raise ValueError("Core8 distribution must contain exactly eight profiles")
    identifiers: set[str] = set()
    labels: set[str] = set()
    required = {
        "id",
        "label",
        "mandate",
        "attention_signal",
        "routing_question",
        "admission_test",
        "transformation",
        "owned_outcome",
        "non_triggers",
        "boundaries",
        "falsifier",
        "handoff_to",
        "default_enabled",
        "authority_class",
        "verified",
    }
    known_types = {item["id"] for item in type_kernel()["types"]}
    for profile in profiles:
        if set(profile) != required:
            raise ValueError(f"profile fields are not closed: {profile.get('id', '<unknown>')}")
        identifier = profile["id"]
        label = profile["label"]
        if not isinstance(identifier, str) or not identifier.startswith("akos.core8."):
            raise ValueError("invalid Core8 profile identifier")
        if identifier in identifiers or label in labels:
            raise ValueError("Core8 profile identifiers and labels must be unique")
        if profile["default_enabled"] is not False:
            raise ValueError("Core8 profiles must default disabled")
        if profile["authority_class"] != "advisory-template":
            raise ValueError("Core8 profiles cannot grant authority")
        if profile["verified"] is not False:
            raise ValueError("Core8 source candidates must remain unverified")
        transformation = profile["transformation"]
        if set(transformation) != {"id", "domain", "codomain", "preconditions", "invariants", "failure_returns"}:
            raise ValueError(f"profile transformation fields are not closed: {identifier}")
        if not transformation["id"].startswith("akos.transform."):
            raise ValueError(f"invalid transformation identifier: {identifier}")
        for field in ("domain", "codomain", "preconditions", "invariants", "failure_returns"):
            values = transformation[field]
            if not isinstance(values, list) or not values or len(values) != len(set(values)):
                raise ValueError(f"profile transformation {field} must be a non-empty unique list: {identifier}")
        unknown_types = set((*transformation["domain"], *transformation["codomain"])) - known_types
        if unknown_types:
            raise ValueError(f"profile references unknown types: {identifier}: {', '.join(sorted(unknown_types))}")
        for field in ("non_triggers", "boundaries"):
            values = profile[field]
            if not isinstance(values, list) or not values or len(values) != len(set(values)):
                raise ValueError(f"profile {field} must be a non-empty unique list: {identifier}")
        handoffs = profile["handoff_to"]
        if not isinstance(handoffs, list) or len(handoffs) != len(set(handoffs)):
            raise ValueError(f"profile handoff list is invalid: {identifier}")
        identifiers.add(identifier)
        labels.add(label)
    for profile in profiles:
        unknown_handoffs = set(profile["handoff_to"]) - identifiers
        if unknown_handoffs or profile["id"] in profile["handoff_to"]:
            raise ValueError(f"profile handoff references are invalid: {profile['id']}")


def _validate_type_kernel(kernel: dict[str, Any]) -> None:
    required = {
        "schema", "kernel_id", "version", "closed_world", "unknown_type_behavior",
        "shared_kernel", "epistemic_classes", "types", "relations", "work_item", "rules",
        "review_status", "verified",
    }
    if set(kernel) != required or kernel.get("schema") != "akos.type-kernel.v1":
        raise ValueError("unsupported or open type-kernel contract")
    if kernel.get("closed_world") is not True or kernel.get("verified") is not False:
        raise ValueError("type kernel must be closed and unverified")
    types = kernel.get("types")
    if not isinstance(types, list) or not types:
        raise ValueError("type kernel must declare types")
    identifiers: set[str] = set()
    type_fields = {"id", "owner", "kind", "nullable", "cardinality", "description"}
    for item in types:
        if set(item) != type_fields or item["id"] in identifiers:
            raise ValueError("type declarations must be closed and uniquely identified")
        if item["nullable"] is not False:
            raise ValueError(f"implicit nullable type is prohibited: {item['id']}")
        if item["kind"] not in {"input", "output", "record", "envelope", "authority"}:
            raise ValueError(f"unknown type kind: {item['id']}")
        if item["cardinality"] not in {"exactly-one", "zero-or-one", "one-or-more", "zero-or-more"}:
            raise ValueError(f"unknown type cardinality: {item['id']}")
        identifiers.add(item["id"])
    if set(kernel["shared_kernel"]) != {"SourceBinding", "Diagnostic", "ReturnEnvelope"}:
        raise ValueError("shared type kernel changed")
    relation_ids: set[str] = set()
    for relation in kernel["relations"]:
        if set(relation) != {"id", "domain", "range", "directional", "transitive", "evidence_required", "cycle_policy"}:
            raise ValueError("relation declarations must be closed")
        if relation["id"] in relation_ids:
            raise ValueError("relation identifiers must be unique")
        relation_ids.add(relation["id"])
        for endpoint in (relation["domain"], relation["range"]):
            if endpoint != "record" and endpoint not in identifiers:
                raise ValueError(f"relation references unknown type: {endpoint}")
    work_item = kernel["work_item"]
    if set(work_item) != {"initial", "states", "terminal", "happy_path", "unknown_transition"}:
        raise ValueError("work-item state contract is open")
    if work_item["initial"] not in work_item["states"] or work_item["unknown_transition"] != "hold":
        raise ValueError("work-item state contract cannot fail closed")


def _validate_operating_policy(policy: dict[str, Any]) -> None:
    required = {
        "schema", "policy_id", "version", "semantic_orientation", "operational_intelligence",
        "governance", "source_relation", "review_status", "verified",
    }
    if set(policy) != required or policy.get("schema") != "akos.operating-policy.v1":
        raise ValueError("unsupported or open operating policy")
    if policy.get("review_status") != "review-required" or policy.get("verified") is not False:
        raise ValueError("operating policy must remain review-required and unverified")
    semantic = policy["semantic_orientation"]
    if set(semantic) != {"meaning_authority", "canonical_meaning_default", "invariants", "forbidden_inferences", "modes"}:
        raise ValueError("semantic orientation contract is open")
    if semantic.get("canonical_meaning_default", "missing") is not None:
        raise ValueError("canonical meaning must default to null")
    if not semantic["invariants"] or not semantic["forbidden_inferences"]:
        raise ValueError("semantic orientation boundaries are missing")
    if any(set(item) != {"id", "use", "expansion"} for item in semantic.get("modes", [])):
        raise ValueError("semantic orientation mode contract is open")
    modes = [item["id"] for item in semantic.get("modes", [])]
    if modes != ["literal", "minimal", "balanced", "expansive", "contrastive", "no-expansion"]:
        raise ValueError("semantic orientation modes changed")
    operational = policy["operational_intelligence"]
    if set(operational) != {"purpose", "layers", "cannot_select", "projection_requirements", "rehydration_rule"}:
        raise ValueError("operational intelligence contract is open")
    if any(set(item) != {"id", "name", "owner", "effect"} for item in operational.get("layers", [])):
        raise ValueError("operational intelligence layer contract is open")
    layers = [item["id"] for item in operational.get("layers", [])]
    if layers != ["L1", "L2", "L3"]:
        raise ValueError("operational intelligence layers changed")
    governance = policy["governance"]
    if set(governance) != {"normative_terms", "precedence", "independent_gates", "fail_closed_on", "validation_limit"}:
        raise ValueError("governance contract is open")
    if set(governance["normative_terms"]) != {"MUST", "MUST_NOT", "SHOULD", "MAY", "HOLD", "UNKNOWN"}:
        raise ValueError("normative term contract changed")
    gates = governance.get("independent_gates")
    if gates != ["source-intake", "semantic-acceptance", "artifact-acceptance", "local-apply", "host-activation", "external-effect"]:
        raise ValueError("independent governance gates changed")


def _normalized_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError("brain name must be text")
    value = " ".join(name.split())
    if not value or len(value) > 80:
        raise ValueError("brain name must contain 1 to 80 visible characters")
    return value


def _normalized_workspace(workspace: str) -> str:
    path = Path(workspace)
    if not path.is_absolute():
        raise ValueError("workspace must be an absolute path")
    resolved = path.resolve(strict=False)
    if resolved == Path("/"):
        raise ValueError("filesystem root cannot be a workspace target")
    return str(resolved)


def _selected_profile_ids(selected: Iterable[str] | None) -> list[str]:
    available = [profile["id"] for profile in core8_profiles()]
    if selected is None:
        return available
    raw = list(selected)
    if not raw:
        raise ValueError("at least one Core8 profile must be selected")
    if not all(isinstance(identifier, str) for identifier in raw):
        raise ValueError("Core8 profile identifiers must be text")
    requested = list(dict.fromkeys(raw))
    unknown = sorted(set(requested) - set(available))
    if unknown:
        raise ValueError(f"unknown Core8 profile: {', '.join(unknown)}")
    return [identifier for identifier in available if identifier in requested]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def object_digest(value: Any) -> str:
    """Return the stable SHA-256 identity of a JSON-compatible value."""

    return f"sha256:{hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()}"


def content_digest(value: str) -> str:
    """Return the SHA-256 identity of UTF-8 text bytes."""

    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def byte_digest(value: bytes) -> str:
    """Return the SHA-256 identity of exact bytes."""

    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def profile_path(profile_id: str) -> str:
    return f".akos/profiles/{profile_id.removeprefix('akos.core8.')}.md"


def validate_brain(brain: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one closed portable brain manifest."""

    required = {
        "schema",
        "name",
        "workspace_root",
        "host",
        "profiles",
        "governance",
        "review_status",
        "verified",
    }
    if set(brain) != required:
        raise ValueError("brain manifest fields are not closed")
    if brain.get("schema") != "akos.brain.v1":
        raise ValueError("unsupported brain manifest schema")
    if brain.get("host") not in HOSTS:
        raise ValueError(f"unsupported host: {brain.get('host')}")
    profiles = brain.get("profiles")
    if not isinstance(profiles, list):
        raise ValueError("brain profiles must be a list")
    normalized_profiles = _selected_profile_ids(profiles)
    if normalized_profiles != profiles:
        raise ValueError("brain profiles must be unique and in registry order")
    expected_governance = {
        "local_first": True,
        "no_write_back": True,
        "human_effect_gates": True,
        "provider_neutral": True,
    }
    if brain.get("governance") != expected_governance:
        raise ValueError("brain governance invariants are missing or changed")
    if brain.get("review_status") != "review-required" or brain.get("verified") is not False:
        raise ValueError("brain manifest must remain review-required and unverified")
    return {
        **brain,
        "name": _normalized_name(brain["name"]),
        "workspace_root": _normalized_workspace(brain["workspace_root"]),
        "profiles": normalized_profiles,
    }


def build_plan(
    *,
    name: str,
    workspace: str,
    host: str = "neutral",
    selected_profiles: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return a deterministic bootstrap plan without writing the target."""

    if host not in HOSTS:
        raise ValueError(f"unsupported host: {host}")
    profile_ids = _selected_profile_ids(selected_profiles)
    brain = validate_brain({
        "schema": "akos.brain.v1",
        "name": _normalized_name(name),
        "workspace_root": _normalized_workspace(workspace),
        "host": host,
        "profiles": profile_ids,
        "governance": {
            "local_first": True,
            "no_write_back": True,
            "human_effect_gates": True,
            "provider_neutral": True,
        },
        "review_status": "review-required",
        "verified": False,
    })
    adapter = host_adapters()[host]
    relative_files = [
        "AGENTS.md",
        "brain.json",
        ".akos/core8.json",
        ".akos/type-kernel.json",
        ".akos/operating-policy.json",
        ".akos/ORIENTATION.md",
        f".akos/host/{host}.json",
        *(profile_path(identifier) for identifier in profile_ids),
    ]
    unsigned = {
        "schema": "akos.bootstrap-plan.v2",
        "brain": brain,
        "directories": list(WORKSPACE_DIRECTORIES),
        "files": relative_files,
        "control_files": [INSTALL_MANIFEST_PATH],
        "adapter": adapter,
        "effects": dict(PHASE_TWO_EFFECTS),
        "omissions": list(PHASE_TWO_OMISSIONS),
        "review_status": "review-required",
        "verified": False,
    }
    return {
        "schema": unsigned["schema"],
        "plan_id": object_digest(unsigned),
        **{k: v for k, v in unsigned.items() if k != "schema"},
    }


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Reject a structurally changed or digest-mismatched bootstrap plan."""

    required = {
        "schema",
        "plan_id",
        "brain",
        "directories",
        "files",
        "control_files",
        "adapter",
        "effects",
        "omissions",
        "review_status",
        "verified",
    }
    if set(plan) != required:
        raise ValueError("bootstrap plan fields are not closed")
    if plan.get("schema") != "akos.bootstrap-plan.v2":
        raise ValueError("unsupported bootstrap plan schema")
    brain = validate_brain(plan["brain"])
    if brain != plan["brain"]:
        raise ValueError("brain manifest values are not canonical")
    host = brain["host"]
    expected_files = [
        "AGENTS.md",
        "brain.json",
        ".akos/core8.json",
        ".akos/type-kernel.json",
        ".akos/operating-policy.json",
        ".akos/ORIENTATION.md",
        f".akos/host/{host}.json",
        *(profile_path(identifier) for identifier in brain["profiles"]),
    ]
    if plan.get("directories") != list(WORKSPACE_DIRECTORIES):
        raise ValueError("bootstrap directory inventory changed")
    if plan.get("files") != expected_files:
        raise ValueError("bootstrap file inventory changed")
    if plan.get("control_files") != [INSTALL_MANIFEST_PATH]:
        raise ValueError("bootstrap control-file inventory changed")
    if plan.get("adapter") != host_adapters()[host]:
        raise ValueError("bootstrap host adapter changed")
    if plan.get("effects") != PHASE_TWO_EFFECTS:
        raise ValueError("Phase 2 effect boundary changed")
    if plan.get("omissions") != list(PHASE_TWO_OMISSIONS):
        raise ValueError("Phase 2 omission ledger changed")
    if plan.get("review_status") != "review-required" or plan.get("verified") is not False:
        raise ValueError("bootstrap plan must remain review-required and unverified")
    unsigned = {key: value for key, value in plan.items() if key != "plan_id"}
    expected_digest = object_digest(unsigned)
    if plan.get("plan_id") != expected_digest:
        raise ValueError("bootstrap plan digest mismatch")
    return plan


def _render_agents(plan: dict[str, Any]) -> str:
    template = files(DATA_PACKAGE).joinpath("workspace-agents.template.md").read_text(encoding="utf-8")
    roles = ", ".join(profile_id.removeprefix("akos.core8.") for profile_id in plan["brain"]["profiles"])
    return (
        template.replace("{{BRAIN_NAME}}", plan["brain"]["name"])
        .replace("{{PLAN_ID}}", plan["plan_id"])
        .replace("{{HOST}}", plan["brain"]["host"])
        .replace("{{CORE8_ROLES}}", roles)
    )


def _render_orientation(plan: dict[str, Any]) -> str:
    template = files(DATA_PACKAGE).joinpath("orientation.template.md").read_text(encoding="utf-8")
    return (
        template.replace("{{BRAIN_NAME}}", plan["brain"]["name"])
        .replace("{{PLAN_ID}}", plan["plan_id"])
        .replace("{{HOST}}", plan["brain"]["host"])
    )


def _render_profile(profile: dict[str, Any], plan: dict[str, Any]) -> str:
    template = files(DATA_PACKAGE).joinpath("profile.template.md").read_text(encoding="utf-8")
    values = {
        "{{PROFILE_LABEL}}": profile["label"],
        "{{PROFILE_ID}}": profile["id"],
        "{{BRAIN_NAME}}": plan["brain"]["name"],
        "{{PLAN_ID}}": plan["plan_id"],
        "{{MANDATE}}": profile["mandate"],
        "{{ATTENTION_SIGNAL}}": profile["attention_signal"],
        "{{ROUTING_QUESTION}}": profile["routing_question"],
        "{{ADMISSION_TEST}}": profile["admission_test"],
        "{{TRANSFORMATION_ID}}": profile["transformation"]["id"],
        "{{DOMAIN}}": "\n".join(f"- `{value}`" for value in profile["transformation"]["domain"]),
        "{{CODOMAIN}}": "\n".join(f"- `{value}`" for value in profile["transformation"]["codomain"]),
        "{{PRECONDITIONS}}": "\n".join(f"- {value}." for value in profile["transformation"]["preconditions"]),
        "{{INVARIANTS}}": "\n".join(f"- {value}." for value in profile["transformation"]["invariants"]),
        "{{FAILURE_RETURNS}}": "\n".join(f"- `{value}`" for value in profile["transformation"]["failure_returns"]),
        "{{OWNED_OUTCOME}}": profile["owned_outcome"],
        "{{NON_TRIGGERS}}": "\n".join(f"- {value}." for value in profile["non_triggers"]),
        "{{BOUNDARIES}}": "\n".join(f"- MUST NOT {value.removeprefix('does not ')}." for value in profile["boundaries"]),
        "{{FALSIFIER}}": profile["falsifier"],
        "{{HANDOFFS}}": "\n".join(f"- `{value}`" for value in profile["handoff_to"]) or "- None; return to the person.",
    }
    for placeholder, value in values.items():
        template = template.replace(placeholder, value)
    return template


def compile_bundle(plan: dict[str, Any]) -> dict[str, str]:
    """Render proposed file bytes in memory; never write them."""

    validate_plan(plan)
    distribution = core8_distribution()
    selected = set(plan["brain"]["profiles"])
    projected_distribution = {
        **{key: value for key, value in distribution.items() if key != "profiles"},
        "profiles": [profile for profile in distribution["profiles"] if profile["id"] in selected],
    }
    host = plan["brain"]["host"]
    bundle = {
        "AGENTS.md": _render_agents(plan),
        "brain.json": json.dumps(plan["brain"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        ".akos/core8.json": json.dumps(projected_distribution, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        ".akos/type-kernel.json": json.dumps(type_kernel(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        ".akos/operating-policy.json": json.dumps(operating_policy(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        ".akos/ORIENTATION.md": _render_orientation(plan),
        f".akos/host/{host}.json": json.dumps(plan["adapter"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    for profile in projected_distribution["profiles"]:
        bundle[profile_path(profile["id"])] = _render_profile(profile, plan)
    if set(bundle) != set(plan["files"]):
        raise ValueError("rendered bundle does not match planned file inventory")
    return bundle
