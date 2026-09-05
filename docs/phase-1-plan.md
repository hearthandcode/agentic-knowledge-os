# Phase 1 implementation record

This records the completed no-write foundation. Phase 2 subsequently added the separately gated, manifest-owned local installation lifecycle described in `phase-2-lifecycle.md`; it did not retroactively change what Phase 1 established.

## Achieved state

A reviewer can inspect one independent repository containing a public-safe Core8 distribution, closed portable contracts, a deterministic no-write bootstrap compiler, host adapter descriptors, synthetic fixtures, and direct validation evidence.

## Source and ownership

- This repository owns the portable distribution and bootstrap semantics.
- Users own their sources, workspace, decisions, and accepted memory.
- Hermes, Pi, and Exocore own their native runtime and loading behavior.
- The HKE Suite remains a sibling implementation dependency and is not copied into this repository.
- Private Core32 sources remain outside this repository. Only abstract capability relationships inform the new public templates.

## Work packages

1. Establish the independent repository boundary and local `AGENTS.md`.
2. Define the Core8 public profile contract and exact eight-role registry.
3. Define the portable brain manifest and bootstrap-plan contracts.
4. Implement deterministic plan and render operations without filesystem mutation.
5. Define neutral, Hermes, Pi, and held Exocore adapter descriptors.
6. Add a public-safe workspace `AGENTS.md` template.
7. Add valid and invalid fixtures plus unit tests.
8. Run source, privacy, determinism, and syntax checks.

## Exit evidence

- exactly eight unique public profiles;
- all profiles default disabled and prohibit authority expansion;
- identical inputs produce identical plan IDs and rendered bytes;
- Hermes projections contain `AGENTS.md` and omit `.hermes.md`;
- Exocore runtime status remains held;
- no repository source contains a private absolute path, credential, private Core32 body, or positive verification seal;
- all source-only tests and validators pass.

## Effects held at the Phase 1 boundary

At this boundary, live workspace creation, plugin installation, profile creation, configuration, provider-backed evaluation, Git commit, remote creation, push, publication, package release, and Exocore bridge implementation required later independent decisions. Phase 2 subsequently released source implementation and disposable-workspace testing of local manifest-owned creation and removal. The initial repository commit and push were later released independently; live workspace, host activation, provider, package-index, and Exocore effects remain held.
