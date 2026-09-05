# Phase 2 installation lifecycle

## Product orientation

Agentic Knowledge OS constructs a user-owned extended mind: an inspectable knowledge workspace whose specialized Core8 fleet operates under a shared RFC-style constitution. The constitution behaves like local legislation for agents. It defines normative terms, precedence, delegation, knowledge provenance, effect gates, privacy, amendment, and completion without pretending to grant host capabilities.

## Plan-to-effect sequence

```text
orientation
  -> deterministic plan
  -> rendered-byte inspection
  -> exact plan-ID confirmation
  -> clean-target preflight
  -> atomic generated-file writes
  -> ownership manifest written last
  -> digest verification
  -> bounded operation receipt
```

The plan lists generated content files separately from the installer control manifest. Exact confirmation authorizes only the planned local workspace write. It does not authorize host activation, profile installation, provider configuration, network access, Git publication, or public release.

## Ownership manifest

`.akos/install-manifest.json` records the plan identity, canonical workspace root, host projection, exact generated file paths and digests, installer-created directories, review state, and explicit absence of live-host activation. The manifest is closed and self-digested before it is trusted.

The manifest owns the generated constitutional and fleet files:

- `AGENTS.md`;
- `brain.json`;
- `.akos/core8.json`;
- `.akos/type-kernel.json`;
- `.akos/operating-policy.json`;
- `.akos/ORIENTATION.md`;
- one `.akos/host/<host>.json` projection.
- one `.akos/profiles/<role>.md` instruction file for every selected Core8 role.

It does not own content placed inside `sources/`, `knowledge/`, `projects/`, `workflows/`, `decisions/`, `evidence/`, `receipts/`, or `archive/`.

## Verification

`verify` checks manifest identity, workspace identity, symbolic-link exclusions, file presence, regular-file type, and UTF-8 byte digests. A `clear` receipt means only that these exact predicates passed. It does not seal the workspace as semantically correct, useful, secure in every environment, accepted, or compatible with a live host.

## Rollback and uninstall

Both operations require the exact manifest digest. They refuse changed owned files by default so a person's edits are not silently destroyed. `--force-owned-changes` is an explicit narrow override for manifest-owned generated files; it still cannot remove user-created files or non-empty directories. The workspace root is always preserved.

Phase 2 rollback removes the current clean install. Version-to-version upgrade transactions, live profile removal, and host configuration restoration remain future contracts.

## Held downstream effects

- installation into a real person's active knowledge workspace;
- Hermes profile or plugin installation and enablement;
- Pi extension registration;
- Exocore bridge activation;
- provider-backed evaluation;
- package-index publication and production release claims.
