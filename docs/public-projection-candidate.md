# Agentic Knowledge OS — initial public release candidate

Agentic Knowledge OS is an early, local-first design for constructing a user-owned extended mind inside an agent harness. Instead of treating memory as an unbounded autonomous database, it treats knowledge work as typed, reviewable transformations governed by human authority.

## What the initial design contains

- a first-run semantic-orientation docket;
- a Core8 fleet expressed as bounded transformations rather than autonomous personalities;
- an RFC-style `AGENTS.md` constitution;
- a closed type kernel for sources, evidence, decisions, projections, gates, effects, and returns;
- deterministic planning and rendering;
- reversible, manifest-owned local workspace installation;
- a host-native Hermes Agent Plugins v1 package;
- a host-native Pi skill and prompt package;
- a held interface description for a future Exocore bridge.

Core8 covers coordination, context selection, evidence analysis, knowledge architecture, knowledge engineering, bounded building, independent review, and lifecycle stewardship. Each role declares when it should be used, what it accepts, what it returns, what would falsify success, and which decisions it does not own.

## Design commitments

- Literal source remains distinct from proposed interpretation.
- Accepted meaning belongs to the person or named source owner.
- Capability does not imply permission.
- Source intake, semantic acceptance, artifact acceptance, local installation, host activation, and external effects remain separate gates.
- Projections retain source identity, transformation, loss, uncertainty, review state, and no-write-back.
- Unknown authority or sensitivity holds only the dependent effect.

## Try the release candidate

Run `scripts/evaluate_alpha.py` for the provider-free temporary-workspace lifecycle, then run `scripts/generate_host_packages.py` against a new or empty directory to produce separate Hermes and Pi packages. The generated host packages use native manifests and ordinary skill-reference paths; neither contains a `.akos` directory.

The Hermes package passed package-doctor discovery under the observed local Hermes Agent v0.21.0 installation. The Pi package installed and appeared in `pi list` under an isolated Pi v0.83.0 profile. These are bounded compatibility observations, not claims about every host version or a live model session.

## Present limits

This release candidate does not provide automatic memory acceptance, semantic-search infrastructure, provider configuration, credential handling, live-profile activation, or an Exocore runtime bridge. Its checks establish deterministic source behavior, disposable-workspace lifecycle predicates, host-package manifest discovery, and one isolated Pi installation only; they do not establish usefulness, safety, semantic correctness, or production compatibility.

## License posture

The selected release model is noncommercial source-available: PolyForm Noncommercial 1.0.0 for software and operational artifacts, CC BY-NC-SA 4.0 for separable narrative documentation, and reserved project marks. Commercial licensing remains separately available from the copyright holder.

## Invitation

The useful question for an initial design review is not whether an agent can remember everything. It is whether a portable agent harness can preserve enough ownership, provenance, disagreement, and reversibility to help a person think without quietly becoming the authority over their thinking.
