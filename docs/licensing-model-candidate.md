# Licensing model decision record

## Status

- Artifact class: public-release decision record
- Decision owner: copyright holder
- Software license: PolyForm Noncommercial 1.0.0
- Documentation license: CC BY-NC-SA 4.0
- Marks: reserved
- Publication effect: held
- Legal review: recommended before release

This document records the selected source-available distribution. It is not legal advice. The controlling grants are the root `LICENSE`, `LICENSE-DOCUMENTATION.md`, and `LICENSE-POLICY.md`.

## Recommended model

For the stated goal—public source, noncommercial experimentation and modification, retained commercial rights—the selected distribution is:

| Material | Candidate license | Intended boundary |
| --- | --- | --- |
| Python, schemas, fixtures, registries, tests, CLI, workspace templates, generated `AGENTS.md`, and profile templates | PolyForm Noncommercial 1.0.0 | Use, change, and redistribute for permitted noncommercial purposes; commercial rights reserved |
| Original explanatory material in `docs/`, `README.md`, and public essays | CC BY-NC-SA 4.0 | Noncommercial sharing and adaptation with attribution and ShareAlike |
| Names, logos, marks, and trade dress | Reserved trademark policy | Truthful attribution allowed; endorsement and confusing branding prohibited |
| Private profiles, internal sources, personal context, unpublished research, and omitted implementation | No public grant | Protected primarily by not including them in the public repository |

Commercial licensing can remain available through a separate written agreement because the public grant is non-exclusive.

## Terminology consequence

A noncommercial restriction is incompatible with the Open Source Definition's prohibition on discrimination by field of endeavor. If this model is selected, public language should say `source-available`, `public-source`, or `noncommercial source release`, not `open-source`.

If an OSI-compliant open-source identity is more important than preventing commercial use, an alternative would be a strong copyleft license such as AGPL-3.0-only. That would require source-sharing in covered circumstances, but it would still permit commercial use and therefore does not meet the stated commercial restriction.

## Why not put Creative Commons on the software

Creative Commons advises against applying CC licenses to software because they do not address source-code distribution and software patent concerns in the same way software licenses do. CC BY-NC-SA is proposed only for separable narrative documentation.

## What licensing can and cannot protect

The licenses can govern copyrighted expression actually included in the release: code, prose, schemas where copyright applies, and authored templates. Copyright does not protect the underlying idea, system, method of operation, or algorithm merely because it is described publicly.

The strongest protection for the deeper private system is therefore architectural separation:

- publish only the original Core8 functional compression;
- omit private profile bodies and personal context;
- avoid internal identifiers, source paths, receipts, and unpublished research excerpts;
- expose interoperability contracts rather than private implementation detail;
- obtain legal advice before disclosure if patent or trade-secret value may be material.

## Contributor boundary

Do not merge outside code or documentation contributions until contributor terms are selected. If the copyright holder wants to preserve the ability to offer commercial licenses, a simple inbound-equals-outbound contribution model may be insufficient. A lawyer-reviewed contributor agreement or explicit copyright assignment/relicensing grant may be needed.

## Applied decision

The copyright holder selected the PolyForm/CC split with reserved marks for the initial source-available release. Before public publication:

1. confirm the copyright and contribution ownership chain;
2. obtain qualified review if patent or trade-secret value may be material;
3. audit the exact public file inventory;
4. confirm GitHub recognizes or clearly displays the nonstandard source-available license.

Accepting contributor terms, publishing a repository, and issuing a release remain separate actions.
