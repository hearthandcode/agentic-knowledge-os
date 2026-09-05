# V7 compact-contract benchmark: frozen design

Status: candidate; context profile: artifact-write; audience: public; verified: false.

User release: implement and execute twelve tasks across three conditions with one initial response and at most one repair per condition (36 trials; 72 provider invocations maximum). This is a new development comparison, not a rerun or amendment of v6. No Git, publication or live-host effects are authorized.

Implementation plan: add failing tests for inventory, prompt parity, independent scoring, bounded repairs and freeze integrity; implement the standard-library runner; validate locally; freeze sources, prompts, tasks and scoring before any calls; run once through existing MiniMax-M3 OAuth; preserve each response and report the complete inventory. No tuning after observing outputs.

Conditions: structured baseline (shared task, schema, supplied role ID), constitution only (same plus current workspace constitution), compact AKOS (same plus the six-rule kernel and selected role outcome/boundaries). This compact condition is not the full fleet context used in v6. All conditions receive identical source bodies, consumer constraints and declared checks. They get the same diagnostic algorithm and at most one repair. Independent expected artifacts are scorer-only and never used to build repair feedback. No expected artifact is passed to the model.

Twelve new synthetic tasks span all eight role labels: ordering, evidence intake, arithmetic, relation mapping, conversion, JSON Patch, conflict review, retention, public projection, recovery, attribution and nullable intake. Author-known tasks are not independently sequestered. Roles are supplied: routing skill is not measured. Private-source bodies are filtered for every condition: privacy retrieval is not measured. Several tasks contain explicitly untrusted instruction text, a synthetic output-contamination marker and instructions not to take effects; detection is text-only, not a tool-permission test.

Freeze: task order is fixed; condition order rotates across tasks to balance position. One repetition per task. Model MiniMax-M3 uses existing mmx defaults; no controlled seed/temperature claim. Each CLI invocation has a 120-second timeout, and the run has a 45-minute ceiling. Provider errors count as failures without retry; timeout stops the run to avoid accumulating uncertain calls. The exclusive launch marker prohibits restarting. Cancellation leaves partial evidence; absent scheduled rows block final aggregation.

Report first-attempt and post-repair exact task-success rates separately, local gate passes, holds, contamination detections, actual calls and elapsed latency. Independent task success requires the exact expected artifact, a passing local gate and no contamination. Holds are terminal and fail these fully answerable tasks. Provider failures remain in the denominator. All attempts are retained. Gate acceptance alone never proves task success. Synthetic expected answers test scoring mechanics, not provider efficacy.

Estimate paired compact-minus-baseline differences with a deterministic 5,000-sample task bootstrap and report descriptive 95% intervals. With only twelve tasks, these are exploratory and sensitive to task selection. Retain the prior target as an explicitly exploratory check: post-repair compact success >=80%, uplift >=10 percentage points, interval lower bound >0, and no compact contamination in either attempt. Report each predicate independently, never an intelligence score, release approval or broad effectiveness claim. No optional stopping or post-hoc threshold changes.

Safety limits: output-canary detection cannot prove absence of unauthorized effects; no tools are exposed to the model. The benchmark's success target does not certify production safety or human semantic acceptance. Historical v5/v6 scores remain unchanged. The compact operation and response envelope differ, so comparisons to historical scores are not causal estimates.

## Execution

Use `PYTHONPATH=src python -m agentic_knowledge_os.benchmark_v7 prepare --root /absolute/empty/run` from the source repository. Preparation copies the Python source and data, rendered prompts, tasks and this protocol into the run directory with a SHA-256 manifest. Freeze before execution.

Run with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/absolute/empty/run python -m agentic_knowledge_os.benchmark_v7 run --root /absolute/empty/run --confirm-provider MiniMax-M3`, with the existing mmx executable on PATH. The direct standard-library adapter uses the same mmx stdin transport as the Promptfoo provider; it does not invoke Promptfoo, because the local gate controls conditional second attempts. No provider dependency is installed.

Use the same frozen module's `score --root /absolute/empty/run` to replay saved raw responses without calls. Replay verifies frozen bytes, sent prompts, response digests, terminal rules and complete inventory rather than trusting saved pass flags. Assessment receipts also retain compact-compiler metadata used internally for validation; condition identity is defined by the separately frozen and recorded sent prompt, not that internal metadata.
