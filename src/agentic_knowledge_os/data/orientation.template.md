# First-run orientation: {{BRAIN_NAME}}

## Status

- Contract: `akos.orientation-docket.v1`
- Bootstrap plan: `{{PLAN_ID}}`
- Host projection: `{{HOST}}`
- Default semantic mode: `minimal`
- Review state: review-required
- Verified: false

This docket orients a person and an agent before durable knowledge work. It is a conversation guide, not permission to inspect files, infer identity, accept meaning, activate a role, or write memory.

## Orientation questions

Ask only what is needed for the present use. Preserve the person's literal answer separately from any proposed normalized terms.

1. Purpose: What should this extended mind help you do now, and what is explicitly outside scope?
2. Sources: Which exact sources may it read, which source is authoritative for each subject, and which sources must remain untouched?
3. Meaning: What wording must remain literal? Where may the agent suggest interpretations, and which meanings have you already accepted?
4. Semantic mode: Should this task use `literal`, `minimal`, `balanced`, `contrastive`, `expansive`, or `no-expansion` orientation?
5. Audience and sensitivity: Is the result private, mixed, or public? What must never be projected outside its source boundary?
6. Effects: Which effects, if any, are allowed now? The default is no filesystem write, provider call, configuration, Git action, publication, or external message.
7. Lead role: Which Core8 transformation should lead? The agent MAY recommend one with a reason but MUST NOT activate it by implication.
8. Return: What observable result, evidence, stop condition, and next human decision define completion?

## Required orientation return

Return a candidate `OrientationRecord` containing:

- literal answers with source ownership;
- proposed normalized vocabulary, separately labeled;
- semantic mode and omitted dimensions;
- sources, exclusions, freshness, and sensitivity;
- accepted meanings, if any, tied to an explicit human decision;
- unresolved hypotheses and declined inferences;
- selected lead role and admission-test result;
- allowed paths, no-touch paths, effect ceiling, checks, stop, and return condition.

If a required answer is unknown, mark it `UNKNOWN` and place only the dependent transition on `HOLD`. Do not fill the gap with a personality inference, diagnosis, adjacent source, or convenient default.
