# AGENTS: Agentic Knowledge OS

## Scope

This repository owns the host-neutral, public-safe Agentic Knowledge OS source distribution: the user-owned extended-mind contract, Core8 role templates, RFC-style workspace constitution, deterministic bootstrap planning, manifest-owned local installation, host adapter descriptors, fixtures, tests, and documentation.

Hermes, Pi, and Exocore remain independent hosts. This repository may describe adapters for them but does not own their runtimes, profiles, providers, credentials, or release processes.

## Current implementation boundary

The current authorization includes downstream source implementation for host-native package projections and a provider-free governance and behavioral-evaluation harness. Local source creation, deterministic tests, generated-output inspection, package-doctor checks, fixture-replay scoring, scorer mutation audits, synthetic matched-comparison checks, and installation-lifecycle tests inside isolated temporary profiles and workspaces are permitted. The source may expose gated local workspace and package writes, but this authorization does not apply either output to a person's live workspace or host profile.

The following remain held unless separately authorized:

- installation into a live user workspace or agent profile during repository development;
- plugin enablement or runtime configuration;
- provider, network, credential, or external-service use;
- copying private Core32 profile bodies or internal Hub material;
- Exocore bridge implementation against an unaccepted interface;
- Git staging, commit, remote creation, push, tag, package publication, deployment, or announcement.

## Source and projection rules

- Public Core8 profiles are original, compact adaptations of abstract capability patterns. They are not copies of private Core32 profile bodies.
- Every generated artifact must identify its source template, transformation, omissions, review state, and authority limit.
- User sources remain user-owned. Generated indexes, summaries, plans, and receipts never become their source automatically.
- Unknown authority, sensitivity, host capability, or target identity holds only the dependent effect.
- Structural validation proves only the checked predicates. Keep `verified: false` until exact human review says otherwise.
- Software and operational artifacts use PolyForm Noncommercial 1.0.0; narrative documentation uses CC BY-NC-SA 4.0; project marks and undistributed private material remain outside those grants.
- Moving content across license classes, accepting contributor rights, commercial licensing, or changing license terms requires exact human review.

## Product invariants

- The canonical portable input is `brain.json`; host outputs are projections.
- `.akos` is the portable workspace/control representation, not a required host-package layout.
- Hermes packages use Agent Plugins v1 `plugin.json` plus `skills/`; Pi packages use `package.json` plus declared `skills/` and `prompts/`.
- `AGENTS.md` is the default workspace instruction surface.
- Do not emit `.hermes.md` alongside `AGENTS.md` by default because Hermes gives the former priority over the latter instruction family.
- Core8 profiles default disabled and provider-neutral.
- Planning remains the default operation. Applying requires an exact reviewed plan ID, an empty or already-owned target, and a manifest-owned rollback path.
- Install manifests may own only generated control files. They never own user-created sources, knowledge, decisions, evidence, projects, workflows, receipts, or archive content.
- Verify reports byte identity for manifest-owned files only. It does not establish semantic quality, live-host compatibility, or human acceptance.
- Artifact identity ledgers prove only the named artifacts' exact bytes under the stated digest algorithm. They do not prove meaning, provenance truth, acceptance, currency, or effectiveness.
- Governance benchmark scores measure only the declared checks against recorded traces. Any hard-gate violation blocks conformance regardless of the average score.
- Synthetic fixture replay is a scorer canary, not evidence that a model, host, or installed system follows the policy in practice.
- Evaluation runners and orchestration frameworks are replaceable adapters; they do not own the rubric, evidence boundary, or release claim.
- Behavioral evaluation must compare frozen structured role-vocabulary, constitution-only, and full-AKOS conditions through complete task-condition-repetition pairs. The structured baseline is not an ordinary unconstrained prompt and must not be described as one.
- Report metric vectors and paired uncertainty independently. A composite effectiveness or intelligence score is prohibited because it can conceal regressions and encode unreviewed value judgments.
- Calibration and held-out results remain separate. Synthetic values evaluate harness arithmetic only; runner-observed values remain estimates pending source review and human disposition.
- No command may infer consent, personal meaning, diagnosis, credentials, or provider configuration.
- Host-package generation never implies package installation, profile placement, enablement, or project trust.
- No generated profile may broaden filesystem, network, Git, publication, or runtime authority.
- Uninstall and rollback specifications must preserve user-created knowledge unless the user explicitly selects it for removal.

## Repository practice

- Keep the core standard-library-only unless a dependency has a demonstrated need and public maintenance plan.
- Keep schemas closed, versioned, and paired with valid and invalid fixtures.
- Add or update tests for every behavior change.
- Keep generated examples synthetic and free of personal paths, credentials, or private source text.
- Preserve unrelated work and stop on concurrent ownership of the same path.
- Do not edit sibling repositories during work in this repository.

## Verification

Before handoff, run:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/validate_repo.py
python -m compileall -q src tests scripts
git diff --check
git status --short
```

Report the exact checks, limitations, changed paths, held effects, and next human gate. A passing check does not install, enable, publish, or verify the system.
