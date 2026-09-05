# Compact artifact contract implementation plan

Status: source candidate; owner: Agentic Knowledge OS; context profile: artifact-write; audience: public; verified: false.

Source: user instruction to define a smaller operational contract and enforce better artifact content, informed by the frozen v6 analysis. Scope is a compact prompt contract, a standard-library content gate, CLI commands, public synthetic fixtures, regression checks and documentation. Existing v5/v6 plans, scorers, raw observations and scores remain historical evidence.

1. Define a short operational kernel and selectively include at most one requested profile's owned outcome. Keep metadata outside consumer artifacts.
2. Add a closed, versioned artifact request: consumer path and supported schema, source IDs and access/authority metadata, optional copy/scale checks grounded in provided sources, and a maximum of two total attempts.
3. Test before implementation: unwanted wrappers and evidence fields, wrong types, missing content, malformed JSON, duplicate keys, source-ID substitutions, unavailable/private check dependencies, incorrect source-derived values, and attempt exhaustion.
4. Compile a prompt and output schema without hidden benchmark expected answers. Reject unsupported schema features instead of silently ignoring them. Model outputs cannot broaden effects, alter request constraints or claim accepted meaning.
5. Return a candidate only after parsing, schema and declared value checks pass. Preserve raw-byte digests, per-attempt outcomes and exact diagnostics. A repair request carries the same contract and diagnostics; no automatic provider call or output rewriting occurs.
6. Expose prompt, check and repair commands, demonstrate on fixtures, ship the compact contract as an optional host-package reference, and run the repository's required checks.

Success means invalid consumer content is blocked and valid source-bound examples pass. This is an enforcement check, not evidence of higher model scores. The next behavioral study must separately freeze fresh tasks and compare first-attempt and repaired outcomes, with equal repair budgets across conditions. No new model run, host activation, Git or publication is included in this implementation.

Repair follow-up: reject unpaired Unicode surrogates without fabricating a byte digest, reject mutually contradictory checks for the same target before prompting, add failing regressions before fixes, and generate disposable provider-free repair receipts. Preserve the frozen benchmarks and unrelated changes.
