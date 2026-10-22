# Consolidate Project Folders

A reusable prompt, local agent skill, and read-only Python audit helper for consolidating overlapping folders while preserving working applications, data, sources, and distinct historical versions.

## Start here

- **Any assistant:** copy [the reusable prompt](prompts/Reusable-Consolidation-Prompt.txt), fill in the paths and options, and provide it with access to the selected folders.
- **Codex:** copy the complete [skill folder](skills/consolidate-project-folders) into `~/.codex/skills/`. It contains `SKILL.md`, metadata, references, an audit helper, and the prompt.
- **Portable package:** download [the skill ZIP](dist/consolidate-project-folders.zip) and extract its `consolidate-project-folders` folder into the skills directory.

Invoke the installed skill with:

```text
Use $consolidate-project-folders to consolidate these folders:
[absolute input paths]
Destination: [absolute destination path]
Preserve working bundles, data, sources, and unique versions.
Delete verified redundant copies: YES or NO.
Rebuild apps: NO, or YES in isolation.
```

The skill guides an assistant; it is not an unattended deletion tool. Deletion requires the user's authorization and a currently verified retained keeper. Matching filenames or dates are insufficient. Identical assets can remain necessary inside separate working bundles.

## What it covers

- Inventory hidden/config/source files and empty directories; qualify exact duplicates by size and SHA-256.
- Evaluate versions by unique content, functionality, provenance, source availability, and tests.
- Preserve complete bundles and distinct data states; archive older versions with restoration evidence.
- Copy, verify, then remove authorized redundant originals with a per-file action map.
- Repair affected links, launchers, configuration paths, and START-HERE routing.
- Recover missing sources within an authorized scope; optionally rebuild and test separate candidates.
- Deliver a final folder tree, file map, duplicate exceptions, verification evidence, and coverage limits.

## Read-only audit helper

Python 3.10+; standard library only. The helper inventories and compares content. It never moves or deletes source files. Keep reports outside scanned roots.

```powershell
python skills/consolidate-project-folders/scripts/consolidation_audit.py inventory --root "C:\Projects\Collection-A" --root "C:\Projects\Collection-B" --out "C:\Audit\run-01\before.json"
python skills/consolidate-project-folders/scripts/consolidation_audit.py inventory --root "C:\Projects\Consolidated" --out "C:\Audit\run-01\after.json"
python skills/consolidate-project-folders/scripts/consolidation_audit.py coverage --before "C:\Audit\run-01\before.json" --after "C:\Audit\run-01\after.json" --zip-members --out "C:\Audit\run-01\coverage.json"
python skills/consolidate-project-folders/scripts/consolidation_audit.py tree --inventory "C:\Audit\run-01\after.json" --out "C:\Audit\run-01\folders.txt"
```

Read [the audit contract](skills/consolidate-project-folders/references/audit-contract.md) before relying on a report. Content coverage does not prove bundle safety, working links, current loose-file hashes, or deletion authority. Exit code 2 reports incomplete coverage or errors.

## Verification

```powershell
python tests/test_audit.py
```

Ten helper contract tests passed, and a synthetic consolidation retained all 43 original files' content, with zero broken active links and two browser-tested apps. See [validation](docs/validation.txt) and [the synthetic forward test](docs/forward-test.md) for scope and limitations. These are historical test results; each new project requires its own checks. The test harness uses only temporary fixtures under its local `tests/test-tmp` folder.

## Privacy and reuse

This public repository contains generic instructions, audit source, synthetic tests, sanitized test reports, and a rebuilt skill package. It has no project datasets, account credentials, emails, or personal computer paths. See [publication review](docs/PUBLICATION-REVIEW.md). Never commit your own input datasets, secrets, runtime profiles, or private audit manifests. The included ignore rules reduce accidental inclusion but do not replace review.

MIT licensed; see [LICENSE](LICENSE).
