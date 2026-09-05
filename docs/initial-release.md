# Initial release — v0.3.0-alpha.1

Agentic Knowledge OS `v0.3.0-alpha.1` is the first public release candidate for a local-first, governed extended mind that can be projected into multiple agent harnesses without handing semantic authority to the agent.

## Why try it

The release packages an RFC-style operating constitution, a bounded Core8 fleet, provenance-aware knowledge routes, a closed type kernel, semantic-orientation rules, Operational Intelligence, and independent gates between planning and consequential effects. It is intended for vibe-coders, AI builders, and knowledge engineers who want useful structure without turning memory, permissions, and interpretation into one opaque system.

## Fast evaluation

Clone the repository, enter its root, and run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/evaluate_alpha.py
```

The evaluation is provider-free and temporary. It exercises deterministic planning, exact-confirmation workspace creation, byte-drift verification, manifest-owned removal, and preservation of a simulated user-owned knowledge file.

## Generate native packages

Choose a new or empty review directory and run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python scripts/generate_host_packages.py \
  --output-root /absolute/empty/review-directory
```

The generator creates:

- `hermes-agentic-knowledge-os/`, rooted at Agent Plugins v1 `plugin.json` and containing `skills/agentic-knowledge-os/SKILL.md`;
- `pi-agentic-knowledge-os/`, rooted at `package.json` and containing the same skill plus `prompts/orient-extended-mind.md`.

Neither package contains a `.akos` directory. The portable `.akos` representation remains available for workspace generation, while host packages surface equivalent governed material through ordinary skill and prompt paths.

## Observed compatibility

- Hermes Agent v0.21.0 accepted the generated Hermes package through `plugins doctor --ci` and discovered its skill. The package deliberately registers no executable, tool, or hook.
- Pi v0.83.0 accepted the generated Pi package from an absolute local path and listed it under an isolated temporary Pi profile.

These checks establish parser, discovery, and isolated package-install behavior for the observed versions only. They do not establish model-session behavior, production compatibility, usefulness, semantic correctness, or permission to alter a live profile.

## Release boundary

The source release does not install or enable a live Hermes plugin, change normal Pi settings, configure a provider, access credentials, use the network, accept a person's meaning, publish an artifact, or implement the held Exocore bridge. Installation and enablement remain explicit, separate user decisions.

## Release status

The repository and baseline `main` branch exist. The host-package changes and this documentation are a local release candidate until their reviewed commit is pushed and a GitHub prerelease or tag is separately published. Use the [public release checklist](public-release-checklist.md) before announcing availability.
