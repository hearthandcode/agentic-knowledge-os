# V6 remediation result

Status: review-required; verified: false. Date: 2026-09-05. Source: the frozen v6 run and raw model outputs. Audience: public candidate documentation; this record does not publish the result externally.

The 72-response MiniMax-M3 OAuth evaluation completed in approximately four minutes. Every scheduled row was present, with zero provider errors and zero reported cache reuse. Independent recomputation from the frozen scorer reproduced the observations and receipt exactly, apart from the execution-added runner exit code. Each raw prompt matched its frozen intervention.

## Primary result

| Condition | Successful trials | Governed success |
|---|---:|---:|
| Structured baseline | 10/24 | 41.67/100 |
| AGENTS.md only | 12/24 | 50.00/100 |
| Full AKOS | 13/24 | 54.17/100 |

AKOS uplift over the structured baseline was 12.5 percentage points, with a task-clustered 95 percent bootstrap interval of -20.83 to 45.83 points. Uplift over the constitution-only baseline was 4.17 points, with an interval of -12.5 to 20.83 points. Both intervals include zero.

The candidate passed the minimum-uplift and zero-hard-gates checks. It failed the 80-percent minimum and positive-interval checks. Qualification is **not-qualified**. No positive effectiveness claim is supported by this run.

V6 uses different tasks and scoring contracts from v5. The numerical difference from v5's 12.5/100 must not be presented as measured improvement on the same benchmark.

## Diagnostic check rates

| Check | Structured baseline | AGENTS.md only | Full AKOS |
|---|---:|---:|---:|
| Substantive artifact content | 45.83% | 62.50% | 62.50% |
| Primary role and necessary handoffs | 66.67% | 91.67% | 87.50% |
| Completion and human-decision state | 79.17% | 95.83% | 91.67% |
| Exact source dispositions | 83.33% | 83.33% | 79.17% |

Full AKOS had no detected hard gates and one malformed JSON response. The structured baseline had four output-contract failures. The constitution-only condition had one declared performed-effect hard gate. These are observed response properties; no live tool effects were exercised or inferred.

## Failure inspection

Full AKOS completed both repetitions of the coordination plan, conceptual relation proposal, patch proposal and retention plan. It passed one repetition each of the public context packet, receipt reconciliation, unit conversion, public card and archive review. Review findings, recovery cutover and ownership reporting passed neither repetition.

The dominant problem was expansion beyond the requested consumer shape. Responses wrapped a direct field mapping in an extra mappings object, turned pass/fail findings into evidence objects or arrays, added recovery prose and handoff fields inside a closed artifact, and replaced source-keyed ownership claims with a richer claim list. The reasoning often preserved relevant boundaries, but the artifact did not satisfy the explicit consumer contract. One enlarged recovery response was malformed JSON. Both review responses invented a fixture- prefix on source identifiers.

Full AKOS did not outperform the constitution-only condition on artifact content, routing, completion, or source-disposition rate. Its one extra end-to-end success reflects how failures overlap across checks. This study does not establish an incremental benefit from loading the complete profile registry.

Two measurement ambiguities remain for review. One public excerpt retained the PUBLIC: label while the expected excerpt omitted it; the instruction to return exact public sentences could be clearer about labels. Ownership responses classified a historical roster as rejected authority while still citing its evidentiary claim. Evidence admissibility and authority are distinct dimensions, so requiring one exclusive disposition loses that nuance. The frozen score is preserved; these observations inform a future protocol rather than post-hoc adjustments.

## Next intervention hypothesis

Prioritize consumer-shape precedence: reasoning and internal role metadata should not add undeclared fields to the user's artifact. Preserve exact source identifiers. Use separate evidence-admission and authority-disposition fields where both apply. A future study should compare a compact operational contract and selectively loaded role with the full registry, using fresh tasks after development on the now-exposed v6 cases.

The evidence favors testing a smaller instruction surface with strict output compilation. Adding further legislative prose has not shown a reliable benefit here. This is a design hypothesis, not an implemented v7 intervention or a promise of an 80-point result.

## Reproduction and limits

The machine-readable [receipt](../evals/results/v6/receipt.json) records results, thresholds and evidence digests. The [protocol](evaluation-v6.md) defines scoring and commands. Raw outputs, exact prompts, provider and executable scorer remain together in the isolated local run bundle; raw outputs are not included in this source result note.

- Plan: `sha256:41023d6e3f6a6c4a62c75a363e4a99a1c98fc7a5e6fc971e9f366b080e6f4e31`
- Configuration: `sha256:42e2468b03758fd4548096e30173d58bade0f70a08b59cbf77a324e02e732bdb`
- Frozen scorer: `sha256:2325b3a435a73d71816c7fb091d6207e8bb2f49ad06a45ff0376859d57e7c07c`
- Raw results: `sha256:f157832d991005c63f3ff041f4481dfea4967be40b2736f32ad28336fbfc078c`
- Promptfoo version: 0.122.2; mmx-cli version: 1.0.19.

Sampling used existing mmx provider defaults. Authors knew the protocol and expected artifacts; these are author-held-out cases, not independently sequestered tasks. The common output instructions helped define a stronger baseline, and exact JSON conformity is narrower than practical knowledge-work usefulness. No general intelligence, live-host, recovery-execution, human-correction or production-safety conclusion follows.
