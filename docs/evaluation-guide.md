# Alpha evaluation guide

## Purpose

The alpha evaluation demonstrates the smallest complete lifecycle that Agentic Knowledge OS currently claims: a deterministic, provider-free plan can generate a governed workspace, identify its own files, verify those exact bytes, and remove its control layer without claiming a user-created knowledge file.

It is an implementation check, not a benchmark of intelligence or a universal live-host compatibility claim.

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
