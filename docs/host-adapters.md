# Host adapters

## Neutral contract

The neutral bundle contains `brain.json`, `AGENTS.md`, the selected Core8 records, and adapter metadata. This is the cross-host source for generated projections.

## Hermes

Hermes can load a root-to-working-directory `AGENTS.md` chain. Its project context discovery gives `.hermes.md` or `HERMES.md` priority over the `AGENTS.md` family, so the default adapter emits only `AGENTS.md`.

The host-package compiler emits a portable Agent Plugins v1 directory rooted at `plugin.json`. The package exposes `skills/agentic-knowledge-os/SKILL.md`; its referenced constitution, orientation, Core8 profiles, type kernel, operating policy, governance suite, behavioral experiment and rubric, and host contract live under that skill's `references/` directory. No MCP server, executable, tool, or hook is registered.

Hermes Agent v0.21.0's real `plugins doctor --ci` accepted the generated package and discovered its skill. This establishes compatibility with that observed parser and discovery path only. Generate and inspect the package before any installation:

```bash
PYTHONPATH=src python scripts/generate_host_packages.py --output-root /absolute/empty/directory
hermes plugins doctor /absolute/empty/directory/hermes-agentic-knowledge-os --ci
```

Hermes Git installation expects the package directory to be a repository root. Install it disabled with `hermes plugins install owner/repository --no-enable`, inspect the installed entry, and enable it only as a separate human action. Local placement under the active profile's `plugins/agentic-knowledge-os/` directory is also a host mutation and is not performed by the generator.

## Pi

The host-package compiler emits a Pi package rooted at `package.json`. It explicitly declares `./skills` and `./prompts`, provides the same portable Agent Skill as Hermes, and adds `/orient-extended-mind` as a Pi prompt template.

Pi v0.83.0 successfully installed the generated package from an absolute local path into an isolated temporary Pi configuration and reported it in `pi list`. This establishes package-manifest acceptance in that isolated test only; no model session or live user configuration was exercised.

```bash
pi install /absolute/path/to/pi-agentic-knowledge-os
```

Use `-l` only when deliberately authorizing a project-local `.pi/settings.json` change. The generator itself does not call `pi install` or change settings.

## Exocore

The Exocore adapter is intentionally held. It may project the neutral manifest into an accepted Exocore profile or workflow contract only after Exocore owns and releases the interface. No private profile source may cross that boundary.

## Shared adapter rule

All adapters consume the same stable brain and profile identities. A host-specific file is a projection with declared loss and status; it never becomes the canonical user brain by convenience. `.akos` remains the portable workspace/control representation; host packages expose equivalent governed material through host-native manifests, skill references, and prompt paths rather than copying the `.akos` directory.
