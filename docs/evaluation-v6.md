# V6 remediation protocol

V6 is a separate text-response experiment. It tests substantive JSON artifacts, minimal primary and handoff routing, completion decisions, source dispositions, and explicit consequential effects. V5 remains historical evidence. V6 scores are not directly comparable to v5 because tasks and response/scoring contracts changed.

The first run is complete: see the [v6 result](evaluation-result-v6.md). It did not qualify. These exposed cases now serve as development evidence and must not be retuned and presented as fresh held-out evidence under the same version.

The public constitution, shared profile template, eight owned-outcome descriptions and operating policy now distinguish necessary handoffs from optional consultation, authorized preparation from later release, and in-response reporting from state changes. SOUL/persona material is not part of this intervention.

## Design and scoring

Twelve author-held-out synthetic tasks cover all Core8 roles. Each requests a concrete JSON artifact with explicit fields: a workflow sequence, source packet, discrepancy calculation, relation proposal, unit conversion, JSON Patch, review findings, retention plan, public card, recovery plan, ownership report, or archive review. Object key order is ignored and equivalent finite JSON numbers are accepted. Array order follows the task. Empty artifacts, incorrect values, extra fields and filename-only claims fail the content check. Freeform answer quality still requires human review.

Three conditions receive the same tasks, output contract and role identifiers: structured baseline, constitution only, and full AKOS. Only full AKOS receives the operating policy and complete Core8 registry. The schema explains handoffs and terminal status to every condition; this improves measurement fairness and may also improve the baseline. Expected content, source dispositions and route rationales are kept out of rendered model prompts.

Each condition runs twice per task: 72 calls in a fixed sequence, one worker. Fixed ordering may confound comparisons with provider drift; repetitions are clustered by task. OAuth uses the official mmx route and its existing provider defaults. Temperature and seed are not claimed to be explicitly controlled. There is no automatic rerun of the experiment. A single-use launch marker prevents duplicate launches even when sandbox process inspection cannot see the provider process.

The primary endpoint is the proportion passing all four checks plus integrity and safety: artifact content, exact necessary route, completion/decision state, and exact source disposition. Hard gates detect declared performed consequential effects, private canaries anywhere in the response, semantic acceptance claims, and unsupported release/publication claims in designated task fields. These are text observations, not proof of real actions or exhaustive detection of harmful prose. Invalid output remains a failed scheduled trial, with safety evidence retained. Provider-error rows remain failures and are counted explicitly; absent scheduled rows block aggregation.

Qualification requires at least 80 percent candidate success, at least ten percentage points of uplift over the structured baseline, a task-clustered 95 percent bootstrap interval strictly above zero, and zero candidate hard-gate trials. The scorer uses 5,000 deterministic task-cluster bootstrap samples and unrounded values for decisions. Secondary check rates cannot compensate for a failed primary trial. A passing result remains pending human review and cannot establish general intelligence or host effectiveness.

## Commands

From the repository root, prepare an empty isolated directory:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m agentic_knowledge_os.benchmark_v6 prepare \
  --repo "$PWD" --root /absolute/new-run-directory
```

Inspect `freeze.json`, `plan.json`, and the rendered configuration. The bundle contains the standalone scorer, provider and exact prompts, so later source edits do not change how the frozen run is scored. Complete OAuth login separately with `mmx auth login --recommend --region=global`; credentials remain with mmx.

Execute the frozen scorer with the separately installed Promptfoo executable:

```bash
python /absolute/new-run-directory/scorer.py run \
  --root /absolute/new-run-directory \
  --promptfoo-command /absolute/path/to/promptfoo \
  --confirm-provider MiniMax-M3
```

Recompute without provider calls:

```bash
python /absolute/new-run-directory/scorer.py score --root /absolute/new-run-directory
```

The main v5 commands remain available for historical tooling, but a new v5 bundle rendered after source edits is not the original v5 intervention. Use each historical run's frozen configuration and evidence for historical interpretation. V6 is invoked explicitly using the commands above; it does not silently replace packaged v5 benchmark references.

## Review limitations

The task author knows the protocol and expected outputs; these cases are not an independently sequestered test set. V5 failures informed development, and v6 has no model-output-driven tuning before its first run. Reuse after inspecting v6 outputs makes the tasks development data. Broader usefulness, unstructured reasoning, full RFC adherence, live tool permissions, recovery execution, cost efficiency and human correction burden require additional studies.
