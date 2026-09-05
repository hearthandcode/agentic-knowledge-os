# Alpha evaluation guide

## Purpose

The alpha evaluation demonstrates the smallest complete lifecycle that Agentic Knowledge OS currently claims: a deterministic, provider-free plan can generate a governed workspace, identify its own files, verify those exact bytes, and remove its control layer without claiming a user-created knowledge file.

It is an implementation check, not a benchmark of intelligence or a universal live-host compatibility claim. See the separate [governance and behavioral benchmark](governance-benchmark.md) for scorer auditing, matched comparison design, and evidence limits.

## Run

From the repository root with Python 3.11 or newer:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/evaluate_alpha.py
```

The script creates its workspace inside a temporary directory and removes that temporary evaluation area when it exits. It does not use the network, credentials, providers, or host configuration.

## Lifecycle exercised

1. Build a deterministic Hermes-targeted plan for all eight public roles.
2. Compile the proposed bundle in memory.
3. Apply it with the exact plan identifier.
4. Verify the ownership manifest and every installer-owned byte.
5. Add `knowledge/user-note.md` as simulated user-owned knowledge.
6. Uninstall with the exact manifest digest.
7. Confirm that all generated files were removed and the user note remains.

The output is a JSON receipt summary. A successful run ends with `"status": "passed"` and reports eight profiles, the generated-file count, lifecycle receipt states, and the preserved user path.

## What a pass establishes

- the same inputs produce the same plan identity;
- the portable bundle contains the selected Core8 profile surfaces;
- local apply requires exact plan confirmation;
- the ownership manifest can detect byte drift in generated files;
- clean uninstall removes only manifest-owned generated files and empty installer-created directories;
- the simulated user knowledge file survives the uninstall check.

## What a pass does not establish

- usefulness for a particular person's thinking or work;
- semantic correctness or human acceptance;
- live Hermes or Pi profile registration;
- Exocore runtime compatibility;
- provider, model, credential, or network behavior;
- security on every filesystem or operating system;
- permission to apply the system to a real workspace.

## Suggested human evaluation

After the automated check, inspect the generated materials without applying them:

```bash
PYTHONPATH=src python -m agentic_knowledge_os orient \
  --name "My Extended Mind" \
  --workspace /tmp/my-extended-mind \
  --host hermes

PYTHONPATH=src python -m agentic_knowledge_os render \
  --name "My Extended Mind" \
  --workspace /tmp/my-extended-mind \
  --host hermes
```

Review whether the constitution is understandable, the Core8 role boundaries are useful, the starter routes fit a real workflow, and the held effects are obvious. Those observations are more valuable at this stage than broad claims about autonomy.

## Host-package evaluation

Generate both native packages into a new or empty directory:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/generate_host_packages.py \
  --output-root /absolute/empty/review-directory
```

Inspect each native manifest, `skills/agentic-knowledge-os/SKILL.md`, its bounded references, and `package-manifest.json`. Neither package should contain a `.akos` directory.

The release candidate has been checked with Hermes Agent v0.21.0 `plugins doctor --ci` and installed from a local path under an isolated Pi v0.83.0 profile. Those checks demonstrate acceptance by the observed package parsers only. Testing a normal user profile, enabling the Hermes plugin, trusting a Pi project, and running a model session remain separate evaluations.

## Optional Promptfoo observation run

The Promptfoo adapter is an optional runner, not a new source of benchmark authority. Version 5 holds the model, twelve-task inventory, structured output contract, and assertions constant while changing only the injected methodology context across structured role-vocabulary, constitution-only, and full-AKOS conditions. Its 72 calls are twelve new held-out tasks × three conditions × two repetitions. The cases test all eight Core8 roles plus coordinated boundaries, with sealed primary-plus-ordered-handoff routes. The model never receives those route sets, typed source dispositions, human-boundary expectations, or outcome criteria. Full-AKOS contract adherence is scored against the selected valid profile after normalization and remains not applicable to baselines.

The v5 primary endpoint is `governed_task_success_rate`, reported from 0 to 100 as the proportion of trials that pass every mandatory outcome, exact typed source handling, the human-decision boundary, an accepted primary-plus-handoff route, output integrity, and all safety gates. Secondary metrics remain separate. Uncertainty is bootstrapped over task clusters so the two repetitions do not become twelve additional independent task families. The preregistered publication threshold requires at least 80/100 for AKOS, at least ten points of uplift over the structured baseline, a task-clustered interval whose lower bound is above zero, and zero candidate hard-gate failures.

It supports two MiniMax-M3 authentication boundaries:

- API key: Promptfoo's native MiniMax provider reads `MINIMAX_API_KEY` from the environment.
- OAuth: the repository's Python worker provider delegates message input over standard input to the official `mmx` CLI, whose device authorization flow with PKCE owns storage and refresh of its private tokens. Worker IPC avoids placing the full rendered AKOS prompt in an operating-system argument.

AKOS does not copy either credential class into configuration, prompts, results, or receipts. The OAuth and API-key paths are deliberately separate because a credential method, Token Plan entitlement, and pay-as-you-go key are not interchangeable claims.

Use `scripts/prepare_promptfoo.py` to inspect a no-call bundle, `scripts/minimax_auth.py` for allowlisted status or an explicitly confirmed OAuth login, and `scripts/run_promptfoo.py` for the exact-confirmation live run. The run uses synthetic public fixtures only, stores Promptfoo state inside its output directory, disables sharing and telemetry, and uses deterministic local assertions rather than a model judge.

The resulting receipt is a partial estimate pending human review. Promptfoo can observe structured task checks, source references, profile routing, declared contract coverage, frozen adversarial guards, latency, token usage, and hard-gate indicators. A malformed or open model response remains in the matched inventory as a `contract_violation` hard gate with fail-closed metric values; it is never silently dropped or repaired. The adapter cannot infer human correction burden or validate recovery behavior from this single-turn protocol, so those metric values remain `null`. A vector of measured deltas is reported; a blended intelligence score remains prohibited.

The first frozen v5 run is recorded in [the v5 evaluation result](evaluation-result-v5.md). It completed all 72 outputs and failed the preregistered qualification threshold. Preserve that result as negative evidence; do not tune against its held-out cases and rerun under the same version label.
