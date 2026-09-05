# Agentic Knowledge OS

**A governed starter kit for building a user-owned extended mind with AI agents.**

**Initial release candidate: `v0.3.0-alpha.1`**

Agentic Knowledge OS is a host-neutral, local-first, noncommercial source-available distribution that gives an agent harness a durable way to organize knowledge work. It combines a specialized Core8 fleet, an RFC-style `AGENTS.md` constitution, explicit knowledge routes, typed operating boundaries, and a reversible installation lifecycle.

It is meant for builders who enjoy the speed of vibe-coding but want the resulting system to remember where information came from, distinguish evidence from interpretation, ask before consequential effects, and leave the person's files intact.

> [!IMPORTANT]
> This repository is an alpha source distribution. Its workspace lifecycle is tested only in disposable workspaces; its generated Hermes package passed Hermes Agent v0.21.0 package-doctor discovery, and its Pi package installed under an isolated Pi v0.83.0 profile. No live user profile has been changed or enabled, and no host is represented as production-ready. `verified` remains `false` pending human review.

## Why this exists

Most agent-memory projects begin with storage or retrieval. Agentic Knowledge OS begins one layer earlier: **who owns meaning, which transformation is happening, what evidence supports it, and which effect has actually been authorized?**

That makes the project useful as a legible operating layer around ordinary files and agent instructions. It does not require a model provider, vector database, orchestration framework, or hosted service.

## Evaluate it in one command

For schema-bound artifact work, the optional [compact operational contract](docs/compact-artifact-contract.md) uses one role and a local content gate. It rejects invalid shapes and declared source-value mismatches, with at most one repair attempt. Enforcement checks alone do not establish higher model effectiveness.

The [v7 development comparison](docs/evaluation-result-v7.md) measured 11/12 post-repair task successes for compact AKOS and constitution-only, versus 6/12 for the structured baseline. Compact prompts were smaller, but the twelve-task run does not establish broad effectiveness or an advantage over the constitution alone.

The [supporting evidence bundle](evals/results/v7/README.md) includes frozen prompts, raw responses and scoring code. Replay it without a provider using `python scripts/verify_public_v7.py`.

Requires Python 3.11 or newer. Clone the repository and run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/evaluate_alpha.py
```

The evaluation uses a disposable temporary directory. It plans and renders a complete workspace, applies the reviewed plan, verifies manifest-owned bytes, adds a simulated user-owned note, uninstalls the generated control layer, and checks that the note survived. It makes no network request and does not configure a host.

The expected final result is `"status": "passed"`. See the [evaluation guide](docs/evaluation-guide.md) for the exact predicates and limitations.

Run the separate governance scorer canary with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/evaluate_governance.py
```

It replays one conformant trace set and one deliberately prohibited semantic-acceptance event. A passing canary shows that the rubric accepts the former, blocks the latter, and keeps effectiveness marked `not-measured`; it does not show that a live model or host behaves effectively.

Audit the complete evaluation harness with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/evaluate_harness.py
```

This mutation-tests every governance axis and hard gate, then exercises the paired behavioral-comparison math across structured role-vocabulary, `AGENTS.md`-only, and full-AKOS conditions. Its behavioral inputs are visibly synthetic: the command evaluates the harness, not the operating system's real-world effectiveness.

## First-release path

1. Run the provider-free evaluation above.
2. Generate the Hermes and Pi packages into a new or empty review directory.
3. Inspect the native manifest, shared Agent Skill, Core8 references, license, and ownership manifest.
4. Integrate only the package for the host you actually use.

The generator performs steps 2–3 without installing, enabling, configuring, or contacting either host. See [Initial release](docs/initial-release.md) for the complete release orientation and bounded integration path.

## Who it is for

The project is intended for people interested in knowledge engineering who want agents to help manage research, notes, decisions, evidence, projects, and evolving mental models without turning the system into an opaque autonomous authority.

For vibe-coders and AI builders, it supplies the part a fast prototype often lacks:

- a ready-made `AGENTS.md` operating constitution instead of an improvised system prompt;
- eight bounded roles with explicit inputs, outputs, failure returns, and handoffs;
- durable routes for sources, decisions, evidence, workflows, and receipts;
- a clear distinction between generating a plan and authorizing an effect;
- a local, provider-free foundation that can be inspected and adapted before host integration.

## What the source provides

- one portable `brain.json` contract;
- a first-run human orientation docket;
- a closed public type kernel and machine-readable operating policy;
- eight specialized, provider-neutral transformation profiles;
- deterministic bootstrap planning and in-memory rendering;
- a detailed RFC-style `AGENTS.md` extended-mind constitution;
- Hermes, Pi, and Exocore adapter descriptors;
- host-native Hermes Agent Plugins v1 and Pi package generation without a `.akos` directory;
- exact-confirmation workspace creation with an ownership manifest;
- drift verification, rollback, and uninstall that preserve user-created knowledge;
- an eight-case Core8 policy-conformance benchmark and byte-identity evidence ledger;
- a preregistered three-condition behavioral experiment with repeated calibration and held-out tasks;
- an optional Promptfoo runner for MiniMax-M3 with API-key and official `mmx` OAuth routes;
- valid and invalid fixtures;
- provider-free tests and a public-safety validator.

Planning and rendering never write the workspace. `apply` is a separate explicit effect: it requires the exact displayed plan ID, accepts only a clean or already-owned target, installs the selected portable profile files, records the generated bytes it owns, and performs no host activation, provider call, or network use.

## Core8

| Role | Responsibility |
| --- | --- |
| Coordinator | Orient, route, sequence, and return work |
| Context Curator | Select bounded context and report omissions |
| Evidence Analyst | Separate sources, observations, claims, and uncertainty |
| Knowledge Architect | Design navigable structures and explicit boundaries |
| Knowledge Engineer | Define schemas, relations, vocabularies, and transformations |
| Builder | Produce bounded artifacts and direct verification evidence |
| Reviewer | Compare work against named criteria and preserve dissent |
| Steward | Protect privacy, continuity, recovery, and lifecycle boundaries |

These are original public adaptations of abstract capability patterns. No private Core32 profile body is copied or distributed. Core8 is a functional compression: each role has an attention signal, closed typed partial transformation, four public RFC rules, named failure returns, owned outcome, non-triggers, falsifier, and handoff seams. It is not eight always-on personalities. Every profile reports admitted domain and codomain types, evaluated rule IDs, failed guards, and performed versus unperformed effects through a common return envelope.

The portable workspace renders each selected role as `.akos/profiles/<role>.md`. Host-native packages project the same role material under `skills/agentic-knowledge-os/references/profiles/`, alongside the constitution, type kernel, operating policy, and first-run orientation. Neither form automatically creates or activates eight native host accounts.

## Plan and inspect

You can evaluate the source directly with `PYTHONPATH=src`, or install it into a virtual environment with `python -m pip install -e .` and replace `PYTHONPATH=src python -m agentic_knowledge_os` with `akos`.

```bash
PYTHONPATH=src python -m agentic_knowledge_os profiles
PYTHONPATH=src python -m agentic_knowledge_os policy
PYTHONPATH=src python -m agentic_knowledge_os types
PYTHONPATH=src python -m agentic_knowledge_os benchmark-suite
PYTHONPATH=src python -m agentic_knowledge_os benchmark-score \
  --traces fixtures/evaluation/conformant-traces.json
PYTHONPATH=src python -m agentic_knowledge_os benchmark-audit \
  --traces fixtures/evaluation/conformant-traces.json
PYTHONPATH=src python -m agentic_knowledge_os experiment-plan
PYTHONPATH=src python -m agentic_knowledge_os experiment-rubric
PYTHONPATH=src python -m agentic_knowledge_os experiment-canary
PYTHONPATH=src python -m agentic_knowledge_os orient \
  --name "Example Brain" \
  --workspace /tmp/example-brain \
  --host hermes
PYTHONPATH=src python -m agentic_knowledge_os plan \
  --name "Example Brain" \
  --workspace /tmp/example-brain \
  --host hermes
PYTHONPATH=src python -m agentic_knowledge_os render \
  --name "Example Brain" \
  --workspace /tmp/example-brain \
  --host neutral
```

`policy` and `types` expose the machine-readable operating contract. `orient` emits the first-run human orientation docket and its deterministic plan identity. `plan` emits paths, actions, gates, and omissions. `render` emits the proposed file contents as JSON. None of these commands writes to the target workspace.

## Apply after review

Save the `plan` output as JSON, inspect it, and pass its exact `plan_id` back as confirmation:

```bash
PYTHONPATH=src python -m agentic_knowledge_os apply \
  --plan-file /tmp/example-plan.json \
  --confirm-plan sha256:REVIEWED_PLAN_ID
PYTHONPATH=src python -m agentic_knowledge_os verify \
  --workspace /tmp/example-brain
```

The apply receipt returns the exact manifest digest needed for `rollback` or `uninstall`. Removal checks owned-file drift first, deletes only manifest-owned generated files, removes only empty installer-created directories, and leaves the workspace root and user-created knowledge in place.

## Give it to a coding agent

If you are evaluating through Hermes, Pi, Codex, or another coding harness, start with this bounded orientation prompt:

> Inspect this repository's `README.md` and `AGENTS.md`. Run the provider-free alpha evaluation. Then use only the read-only `profiles`, `policy`, `types`, `orient`, `plan`, and `render` surfaces to propose a workspace for me. Explain the Core8 roles, generated paths, omissions, and held effects. Do not run `apply`, change host configuration, activate profiles, or connect a provider until I review the exact plan and authorize that effect.

The prompt asks an agent to demonstrate the system before it writes anything. The generated `.akos/ORIENTATION.md` then guides the human conversation about purpose, source ownership, meaning, sensitivity, allowed effects, and return conditions.

## Generate host-native packages

The portable `.akos` workspace remains available as an inspectable intermediate representation, but it is no longer the only integration surface. Generate separate native package directories for Hermes and Pi:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/generate_host_packages.py \
  --output-root /absolute/empty/review-directory
```

The output contains:

- `hermes-agentic-knowledge-os/`: an Agent Plugins v1 package rooted at `plugin.json` with a discoverable `skills/agentic-knowledge-os/SKILL.md`;
- `pi-agentic-knowledge-os/`: a Pi package rooted at `package.json`, providing the same skill plus `/orient-extended-mind` as a prompt template.

Neither package contains a `.akos` directory. Both carry the constitution, orientation, Core8 profiles, type kernel, operating policy, governance benchmark, behavioral experiment plan and rubric, host contract, license, notices, and a digest manifest under ordinary host-package paths. Generation writes only to a new or empty output directory and does not install or enable either package.

For a single reviewed package, use the exact-confirmation flow exposed by `package-plan`, `package-render`, `package-apply`, and `package-verify`. See [Host adapters](docs/host-adapters.md) for integration commands and present compatibility evidence.

## Host posture

- **Neutral:** emits only the portable workspace contract.
- **Hermes:** can emit a portable Agent Plugins v1 skill package rooted at `plugin.json`. Generation does not install, enable, or configure a profile.
- **Pi:** can emit a package rooted at `package.json` with one Agent Skill and one orientation prompt template. Generation does not change Pi settings or project trust.
- **Exocore:** emits a held interface projection only. Runtime bridge implementation waits for an accepted Exocore-owned interface.

## Optional observed MiniMax-M3 comparison

The [v6 remediation protocol](docs/evaluation-v6.md) adds substantive artifact checks, minimal routing, and typed effects through a separate frozen runner. Its [first frozen result](docs/evaluation-result-v6.md) was 54.17/100 for full AKOS, 50/100 for the constitution alone and 41.67/100 for the structured baseline, with no candidate hard gates. It did not meet qualification. V6 scores are not directly comparable with v5. The v5 tooling below remains a historical protocol; current source changes do not reproduce the original frozen v5 intervention.

The provider-free canaries remain the default. The optional Promptfoo v5 publication-candidate adapter runs a frozen 72-row matched comparison against the same MiniMax-M3 model across a structured role-vocabulary baseline, `AGENTS.md`-only, and full-AKOS conditions: twelve new held-out tasks × three conditions × two repetitions. The first condition is not an ordinary unconstrained prompt: it receives the common output schema and Core8 role identifiers, but no AKOS constitution, operating policy, or profile contracts. V5 tests bounded upstream completion, typed source dispositions, exact primary-plus-ordered-handoff routes, and the distinction between preparing a candidate and performing its held effect. It reports one conjunctive Governed Task Success Rate alongside disaggregated secondary metrics, not a blended intelligence score.

The first frozen v5 MiniMax-M3 OAuth run completed all 72 calls but did **not** qualify for publication effectiveness: AKOS scored 12.5/100 against 0/100 for the structured baseline, with a task-clustered uplift interval of 0 to 29.17 points, one candidate hard-gate classification, and only the minimum-uplift check passing. This is negative evidence, not a release claim. See the [v5 result note](docs/evaluation-result-v5.md) for the complete bounded interpretation.

Prepare a secret-free run bundle without making a provider call:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/prepare_promptfoo.py \
  --auth-mode oauth \
  --output-root /absolute/path/to/new-run-directory
```

For MiniMax OAuth, the adapter uses the official `mmx` CLI's device authorization route; it does not read or copy tokens:

```bash
mmx auth login --recommend --region=global
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/minimax_auth.py status --mode oauth
```

The alternate `api-key` route reads only `MINIMAX_API_KEY` from the process environment through Promptfoo's native MiniMax provider. Neither route places a key or OAuth token in the generated config. After reviewing `run-manifest.json`, execute with an exact provider confirmation:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/run_promptfoo.py \
  --auth-mode oauth \
  --output-root /absolute/path/to/new-run-directory \
  --confirm-provider MiniMax-M3
```

Promptfoo sharing, telemetry, update checks, remote generation, cache reuse, and concurrent calls are disabled for this runner. The raw output remains local. AKOS deterministically scores task utility, source fidelity, resource efficiency when counters exist, agency preservation, profile routing, typed contract adherence, adversarial resistance, and hard gates. Correction efficiency and recovery quality remain unmeasured until a separate protocol collects their required evidence; no composite intelligence score is produced. See [the adapter runbook](evals/promptfoo/README.md).

See [Governance benchmark](docs/governance-benchmark.md), [Evaluation guide](docs/evaluation-guide.md), [Core8 orientation](docs/core8-orientation.md), [Refined Agentic OS design](docs/refined-agentic-os.md), [Architecture](docs/architecture.md), [Phase 2 lifecycle](docs/phase-2-lifecycle.md), [Host adapters](docs/host-adapters.md), and [Source boundary](docs/source-boundary.md).

## Public release preparation

An [initial release orientation](docs/initial-release.md), [public projection](docs/public-projection-candidate.md), [release checklist](docs/public-release-checklist.md), [community announcement](docs/community-announcement.md), [licensing decision record](docs/licensing-model-candidate.md), and [low-cost IP baseline](docs/ip-protection-baseline.md) are available for review.

The selected licensing distribution is:

- software and operational artifacts: [PolyForm Noncommercial 1.0.0](LICENSE);
- original narrative documentation: [CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md);
- project marks: reserved under [TRADEMARKS.md](TRADEMARKS.md).

This permits bounded noncommercial use, modification, and redistribution while reserving commercial licensing. It is source-available, not OSI open source. See [LICENSE-POLICY.md](LICENSE-POLICY.md) for scope and precedence.

## Validate

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/validate_repo.py
python -m compileall -q src tests scripts
git diff --check
```

Passing these checks establishes source shape, deterministic planning, scorer mutation sensitivity, comparison arithmetic, and the tested temporary-workspace lifecycle only. It does not establish usefulness, live-host compatibility, universal filesystem safety, causality, or human acceptance. Those require observed matched runs and human review.
