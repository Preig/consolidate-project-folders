---
name: consolidate-project-folders
description: Consolidate overlapping local folders or project versions with exact-hash deduplication, preserved working bundles and data, version archives, link repair, and a verified file map. Use for folder merges, duplicate cleanup, or final consolidation audits.
---

# Consolidate project folders

Produce one navigable collection whose retained files, runnable bundles, sources, data and history are accounted for. Adapt the layout to the project. An identical file inside two working bundles can be a required dependency in both.

## Scope and authority

Identify input roots, authoritative destination/primary version, protected references, deletion authority and requested verification depth. Reuse current instructions, relevant local guidance and earlier user decisions. Do not generalize one project's paths or counts to another.

Ask only for consequential missing choices; continue independent inspection while waiting. If deletion is already authorized for the named roots, proceed after evidence checks without repeating approvals. Evaluation/audit alone does not authorize deletion. Consolidation does not authorize deployment, replacing production binaries, resetting data or searching unrelated accounts.

Keep intermediate scripts, staging and baseline manifests outside input roots. Use a unique run ID/date. Do not operate on example paths when the user only asks for a prompt or skill.

## Inventory and decide

1. Resolve absolute roots; detect nesting, junctions/symlinks, cloud placeholders, access failures and active/writable data. Inventory the destination too. Preserve hidden files, version-control history, configuration, dependencies and empty directories unless exclusions are explicit and recorded.
2. Capture root/relative path, bytes, modification time, SHA-256 and read/stability status. Group duplicates by **size + SHA-256**, never name, date, similarity or appearance. A partial scan cannot establish complete preservation.
3. Classify complete bundles: websites with assets, apps with data/config/runtime, source/build trees, document packages and releases. Compare versions by unique content, functionality, provenance, source availability and test status; dates are secondary evidence.
4. Select primary bundles and source families using evidence and owner decisions. Archive distinct earlier versions intact. Preserve ambiguous variants. Do not mix incompatible revisions merely to reduce copies.

Use [scripts/consolidation_audit.py](scripts/consolidation_audit.py) for repeatable read-only inventory, content-coverage checks and folder trees. It never moves/deletes source files. Duplicate groups are evidence, **not a deletion plan**. Read [the audit contract](references/audit-contract.md) for commands and evidence requirements.

## Prepare the migration

Create a per-file map: original path/hash, action, final path or archive member, keeper, rationale and verification. Include intentional bundle-local duplicates and preexisting broken links. Keep name collisions as distinct variants; never overwrite different bytes silently.

Stage where practical. Preserve distinct live/company/demo data states. If concurrent writes prevent a consistent snapshot, use supported backup/quiescence or leave that migration pending.

A ZIP keeper counts only when the exact uncompressed member is readable and its size/hash match. An outer ZIP hash or member listing is insufficient. Preserve provenance and rollback bytes for deliberate edits such as repaired links.

## Execute authorized consolidation

- Copy/merge, verify destination content, then remove authorized redundant originals. Recheck current source **and** retained keeper immediately before deletion. Stop affected actions on drift or ambiguity; continue unaffected work.
- Remove standalone duplicates with verified retained keepers. Keep same-hash dependencies at paths required by separate runnable/source bundles; record exceptions. Retire an entire duplicate bundle only after checking the full tree and required state/configuration.
- Different-byte ZIPs/packages are distinct unless explicit retirement authority and full member comparison establish equivalence. Archive unique older work; do not call its disposal exact deduplication.
- On Windows use native PowerShell literal paths. Resolve/bound move/delete targets against approved roots. Avoid cross-shell destructive commands and blanket recursive deletion. Remove old directories only after accounting for their contents and confirming they are empty. Preserve protected mirrors/references.
- Log completed operations/evidence as they happen. Inspect partial state on retries. Do not silently change deletion methods after a permissions or safety rejection.

## Repair and verify

Rebase affected links, shortcuts, launchers, configs and START-HERE documentation. Preserve meaningful fragments. Separate preexisting failures from migration regressions; when repair is requested, fix both within scope and verify again. Update relevant generators/build inputs or document the rebuild limitation.

Validate at the claimed level: paths/anchors, ZIP members, document/package structure and meaningful app/browser/data workflows. Do not run the original writable app for preservation tests. Preserve document content/media during relationship-only edits and verify unchanged package parts where feasible.

For app/data checks, missing-source searches, source-to-binary comparison or requested rebuilds, read the relevant sections of [advanced verification](references/advanced-verification.md). These are conditional branches, not requirements for every folder cleanup.

Finish with a fresh inventory. Account for every original as retained loose, retained as an exact verified archive member, preserved as rollback bytes for a deliberate edit, verified redundant, or explicitly retired under a separate decision. Unexplained loss or untested areas are open findings, never PASS. A preservation-only phase must leave protected scopes matching baseline hashes.

## Deliver

Provide current START-HERE routing, full folder tree, size/hash inventory, file/action map, duplicate exceptions, version criteria, archive/restore map, verification/coverage limits and audit evidence. Report actual savings separately from intentional duplicate dependencies. Account for final audit files in the inventory or an explicit supplement.

Keep final chat concise: outcome, material exceptions, counts, criteria and clickable deliverables. Distinguish preserved, statically validated, runtime-tested, rebuilt and deployed. Replacement/deployment needs its own authorization.

For a reusable starting prompt, adapt [assets/consolidation-prompt.txt](assets/consolidation-prompt.txt).
