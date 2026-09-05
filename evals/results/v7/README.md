# Public v7 evidence projection

This is a reviewed publication projection of the completed development run, not a new benchmark execution. See the [result and limitations](../../../docs/evaluation-result-v7.md).

- `receipt.json`: readable result summary.
- `observations.json`: readable 36-trial inventory with per-condition outcomes.
- `manifest.json`: archive SHA-256, exact per-file hashes, transformation and omissions.
- `frozen-evidence.tar.gz`: 191 exact files under `v7/`, including frozen source/data, protocol, plan, original sent prompts, 38 raw responses, transport metadata, assessments and results. No credentials, authentication state, caches or machine logs are included. No raw evidence bytes were normalized.

From the repository root, use Python 3.11+ for provider-free replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/verify_public_v7.py
```

This checks the archive and entry hashes, extracts only regular safe paths to a disposable directory, and runs the archived scorer in `score` mode. It does not call MiniMax or install anything. The launch marker remains in the archive to prevent accidental reuse as a new experiment. As with any executable archive, inspect the source and verify the trusted repository revision before running it; co-located hashes prove consistency, not independent authenticity.

The twelve tasks are synthetic and author-known. Compact AKOS and constitution-only both achieved 11/12 post-repair task successes; there is no measured advantage of compact AKOS over the constitution on task success. Retain dual-ID ambiguity, format-only repair and small-sample limitations when sharing these results. License terms follow the repository's software/operational-artifact and documentation split; no new rights are granted by projection.
