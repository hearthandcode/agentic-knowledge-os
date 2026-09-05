# V7 compact-contract development result

Status: completed development comparison; context profile: artifact-write; audience: public; verified: false.

The frozen [v7 protocol](evaluation-v7.md) completed all 36 matched trials using 38 MiniMax-M3 OAuth invocations, below the authorized maximum of 72. No provider errors occurred. The model received no tools and no hidden expected artifacts. Raw outputs were retained without stripping fences or normalizing content. Two trials received the permitted repair; both succeeded on their second attempt.

| Condition | First-attempt task success | Post-repair task success | Calls | Terminal holds |
| --- | --- | --- | --- | --- |
| Structured baseline | 6/12 (50.0%) | 6/12 (50.0%) | 12 | 3 |
| Constitution only | 10/12 (83.3%) | 11/12 (91.7%) | 13 | 1 |
| Compact AKOS | 10/12 (83.3%) | 11/12 (91.7%) | 13 | 0 |

The compact-minus-baseline post-repair difference was 41.7 percentage points, with a descriptive paired task-bootstrap 95% interval of +16.7 to +66.7 points. The first-attempt difference was 33.3 points, with interval 0 to +66.7. All four frozen exploratory target predicates were met: compact post-repair success >=80%, uplift >=10 points, a positive post-repair interval lower bound, and zero detected compact output-contamination markers. These predicates are not release approval, production certification or evidence of general intelligence.

## What this supports

The compact condition matched constitution-only task success on these twelve tasks with a substantially smaller prompt. Mean initial prompt length was approximately 3,992 characters for compact AKOS, 16,137 for constitution only and 1,172 for the structured baseline. Compact was about 75% smaller than constitution only by character count; this is not a token, billed-cost or context-retention estimate. Observed summed provider invocation times were 16.28, 17.24 and 14.71 seconds respectively; those single-run times do not establish latency superiority.

The local gate and independent content check remained meaningfully separate: all 12 compact final artifacts passed the local gate, but only 11 passed exact task content. A passing validator therefore was not counted automatically as task success.

## Failures and limitations

- Both successful repairs removed Markdown code fences: constitution-only on relation mapping, compact AKOS on conflict review. This demonstrates format repair, not improved reasoning through repair.
- The compact intake response used the enclosing evidence record's `input-intake` ID instead of the nested source's `note-B17` ID expected by the frozen scorer. The task has two source-ID levels, making this an ambiguity worth addressing in a future protocol. Its failure remains counted; no scoring rule or prompt was changed after observation.
- The baseline also missed the intake ID, expanded an explicitly requested assessment label into prose, selected the enclosing rather than nested source ID on attribution, and held three answerable preparation tasks. The attribution case shares the dual-ID ambiguity noted above. Constitution-only held the intake task. These are failures under the frozen exact-content rubric, not comprehensive judgments of practical usefulness.
- The conditions tied on post-repair success for constitution-only versus compact AKOS. This run supplies no evidence of added task-success benefit from the compact layer over the constitution alone.
- Twelve author-known synthetic tasks, one repetition, supplied roles and prefiltered sources limit generalization. Condition order rotated but was not fully randomized. Provider seed and temperature were not explicitly controlled. No independently sequestered evaluation, live-host test, routing test or tool-effect trace was collected.
- Zero detected contamination is a bounded text check. It does not establish complete governance adherence, absence of unauthorized actions in a real host, semantic acceptance or security.

## Evidence and reproducibility

Frozen run identity: `akos-v7-frozen-4W7tIH`.

- Freeze manifest SHA-256: `ccfc5d8c7ca0ad7914b0898b4bb28d0c7f4852a1da0aea6aedbbc8cd6f6d289e`.
- Plan SHA-256: `b512265e74936dd127e3f7bd3a69aeed14694d652d2d6b5a3feedf963b9513c6`.
- The [public evidence projection](../evals/results/v7/README.md) includes the exact frozen code/data, prompts, raw responses, transport metadata, assessments and results in a digest-indexed archive. Authentication state, caches and machine logs are excluded. Run `python scripts/verify_public_v7.py` to replay it without provider calls.
- Provider-free replay rebuilt scoring from the raw responses and verified frozen inputs, sent prompts, response digests and terminal rules. The replayed and original result JSON values match; their text files differ only by the CLI's trailing newline.
- At benchmark completion, all 97 repository tests, repository validation, Python compilation and whitespace checks passed. Existing v5/v6 evidence was not modified. The subsequent evidence-publication update adds offline replay and tamper-rejection tests; it does not rerun the provider or install a live host.

Next research step: independently reviewed, less ambiguous task contracts; larger and more diverse task samples; independent content tests that cover more than exact JSON; and repeated matched trials. Do not retune these exposed cases and relabel them as fresh held-out evidence.
