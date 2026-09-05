# Compact artifact operation

Status: source candidate; context profile: artifact-write; audience: public; verified: false.

The compact contract separates **what the consumer needs** from **what the harness records**. It addresses development failures observed in v6: extra wrappers, expanded metadata, changed identifiers and well-formed but incorrect content. It does not amend that benchmark or establish improved model performance.

## The smaller contract

Load the six-rule `src/agentic_knowledge_os/data/compact-runtime-contract.md`, at most one selected Core8 role's owned outcome and boundaries, and one explicit artifact request. Do not inject the full fleet or evaluation rubric. This is a narrow artifact-preparation operation, not replacement workspace law.

The agent returns only a prepared envelope containing the consumer object, or an explicit hold with a missing prerequisite. The checker generates source dispositions, byte digests, per-attempt diagnostics and review posture outside the consumer artifact. Evidence inclusion remains separate from authority.

Hermes and Pi package generation includes `references/compact-runtime-contract.md` and `references/artifact-request.schema.json`. These references alone do not enforce behavior. Enforcement requires the source distribution's Python checker to be invoked by an explicitly authorized harness; no live host hook is installed.

## Fail-closed content gate

The versioned request declares the path, audience, optional profile, closed consumer schema, supplied sources, optional source-derived checks and one or two total attempts. The packaged request schema documents its wire format; compilation additionally validates source admission, pointers and supported content constraints.

- Reject malformed JSON, duplicate keys, non-finite numbers, wrong types, missing fields, extra wrappers and undeclared metadata.
- Reject unpaired Unicode surrogates. A response without valid UTF-8 bytes has a null raw digest, never a fabricated byte identity. Reject conflicting source checks on the same target before generating a prompt.
- Require closed objects and all declared fields; use nullable fields explicitly. Support nested objects, arrays, scalar types, constants, enums, bounds and unique array items. Unsupported schema keywords fail compilation instead of being ignored.
- Use exact enums/constants when source identifiers must be preserved. Source checks support exact copy or numeric scaling from an admitted source at a declared JSON pointer.
- Emit no artifact candidate on failure. Return diagnostics for at most one replacement under the unchanged request. Preserve first-attempt failure even if the replacement passes. Success, hold and exhaustion are terminal.
- Keep private source bodies out of public prompts. Supplied classifications and request metadata are trusted owner inputs, not automatic privacy detection; review them before sharing. Untrusted sources remain evidence, never governing instructions.

Numeric checks use parsed JSON numbers and decimal multiplication, not arbitrary-precision decimal transport. For exact financial or scientific decimals, use string representations and copy checks or a separately reviewed evaluator.

## Try without a provider

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m agentic_knowledge_os artifact-prompt --request fixtures/evaluation/compact-artifact-request.json --text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m agentic_knowledge_os artifact-check --request fixtures/evaluation/compact-artifact-request.json --response fixtures/evaluation/compact-artifact-invalid.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m agentic_knowledge_os artifact-check --request fixtures/evaluation/compact-artifact-request.json --response fixtures/evaluation/compact-artifact-invalid.json --response fixtures/evaluation/compact-artifact-valid.json
```

The second command intentionally exits 2 and returns `repair-needed`. The third exits 0 and returns `valid-candidate`, retaining `first_attempt_passed: false`. This is a synthetic two-attempt demonstration, not a model repairing its own answer. Commands print results only: no provider calls, file application or host activation.

## Scoring boundary

Do not award style points that compensate for invalid artifacts. A candidate passes only when parsing, envelope, consumer shape and every declared value check pass. Receipts list which checks actually ran; shape failure skips source-value checks. Empty check lists provide shape enforcement only. Undeclared semantic errors remain undetected.

A future balanced, separately frozen study should report first-attempt valid-artifact rate, post-repair rate, task success under independent content tests, holds, harmful effects, calls and latency. All conditions need equal source access, check feedback and repair budgets. Separate development examples from fresh evaluation tasks. Retain v5/v6 negative evidence; this implementation supplies no new effectiveness score and makes no 80/100 claim.
