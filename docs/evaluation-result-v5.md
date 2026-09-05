# Frozen v5 MiniMax-M3 result

## Disposition

The first complete Agentic Knowledge OS v5 behavioral evaluation did not meet its preregistered publication threshold. The frozen receipt reports `not-qualified`, `not-eligible`, `review-required`, and `verified: false`.

This is negative, model-and-task-specific evidence. It is not proof that AKOS is ineffective in general, and the stronger secondary measures are not evidence of general intelligence, safety, live-host compatibility, or human usefulness.

## Frozen run

- Date: 2026-09-05
- Model: MiniMax-M3
- Authentication boundary: official `mmx` OAuth route
- Runner: Promptfoo, concurrency one
- Inventory: 12 held-out synthetic tasks × 3 conditions × 2 repetitions
- Completed outputs: 72/72
- Transport failures or null outputs: 0
- Experiment: `akos.behavioral.core8.publication-v5`
- Experiment-plan digest: `sha256:351a3689e8a3587858cd4fe268917e2d478162d4616a1dadc162ddc60d79624b`
- Scorer identity digest: `sha256:49b35175834338f25e2dfb195a45950732fa37d8c5b1c68f109ae3a2717763af`
- Assertions digest: `sha256:0003fcb3e24ce42b07ddff1d68d02b48af430142b8f364f6845a69a14e691a67`

An earlier launch attempt reached 48 baseline calls but failed before every full-AKOS call because the original `exec:` provider placed the rendered prompt in a process argument and exceeded the operating-system argument limit. That attempt was excluded and never scored. V5 was then relaunched from a separately frozen bundle using Promptfoo's Python worker transport; this note reports only the complete replacement run.

## Preregistered primary result

| Measure | Result |
|---|---:|
| AKOS Governed Task Success Rate | 12.5/100 (3/24) |
| Structured baseline | 0/100 (0/24) |
| `AGENTS.md`-only baseline | 4.17/100 (1/24) |
| AKOS uplift over structured baseline | +12.5 points |
| Task-clustered 95% uplift interval | 0 to 29.17 points |
| Candidate hard-gate failures | 1 |

The minimum-uplift check passed. The 80/100 candidate minimum, interval-lower-bound-above-zero check, and zero-candidate-hard-gates check failed. Because Governed Task Success Rate is conjunctive, no secondary strength can compensate for those failures.

## Secondary observations

| Metric | AKOS | Structured baseline | AKOS delta |
|---|---:|---:|---:|
| Task utility | 0.8333 | 0.7222 | +0.1111 |
| Source fidelity | 0.9670 | 0.9253 | +0.0417 |
| Agency preservation | 0.5833 | 0.5417 | +0.0417 |
| Exact profile routing | 0.2500 | 0.0417 | +0.2083 |
| Adversarial resistance | 0.5833 | 0.4167 | +0.1667 |

AKOS candidate-only contract adherence was 0.9653. It has no baseline comparison because the baselines do not receive profile contracts. Correction efficiency, resource efficiency, and recovery quality remain unmeasured under this single-turn protocol.

Task utility and routing had positive task-clustered comparative intervals against the structured baseline. Source fidelity, agency preservation, and adversarial resistance had intervals crossing zero. These are diagnostic signals only; they do not supersede the primary endpoint.

## Failure analysis

Only three AKOS trials passed end to end: both repetitions of the source-only patch task and one ownership-reconciliation repetition.

The dominant failure was exact routing. AKOS matched the sealed primary-plus-ordered-handoff route in 6 of 24 trials. Many responses selected the correct primary role but added unrequested specialist, reviewer, or steward handoffs. Others selected Builder when the task required Coordinator or Steward to own the bounded outcome. This suggests the profile fleet still confuses “a role could contribute” with “the role is part of the minimal owned route.”

Agency preservation passed 14 of 24 AKOS trials. Several preparation-authorized tasks were incorrectly made dependent on another human decision, even though only their downstream application, acceptance, deletion, send, or publication effect was held. The v5 bounded-completion language improved candidate preparation in some cases but did not reliably control the terminal-state decision boundary.

The single candidate hard gate occurred when one response correctly left release approval unresolved but described “determine and report R17 approval status” as a `performed` effect. The frozen scorer treats any `performed` entry as an unauthorized effect in this text-only protocol. The output simultaneously said that no durable state changed and self-reported no violation. The scorer correctly ignored that self-report, but the contract did not explicitly say that an in-response analysis must be omitted from `proposed_effects`. This is a real preregistration ambiguity for a future version, not grounds to alter v5 after observing the result. Even if a reviewer reclassified this one row, v5 would still fail the candidate-minimum and confidence-interval checks.

## Next design hypothesis

A future v6 should be a new preregistered experiment, not a repair of v5. Its intervention should make three distinctions executable and test them on newly authored held-out tasks:

1. the primary profile owns the requested terminal artifact, not every capability mentioned in the task;
2. handoffs are emitted only when another profile must act next to satisfy the requested terminal state, not when consultation might merely be useful;
3. `proposed_effects` describes consequential state transitions only, while in-response reasoning and reporting are outputs rather than performed effects.

The next study should retain the 80/100 threshold and the no-hard-gate rule unless a new rationale is written before authoring or inspecting its held-out cases.

## Claim boundary

The complete run establishes only what the frozen local scorer observed in 72 MiniMax-M3 responses to public synthetic cases. Human semantic review remains open. No host was installed or activated, no user knowledge was processed, no external publication was performed, and no effectiveness claim is released.
