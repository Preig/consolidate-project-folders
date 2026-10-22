# Synthetic forward test: consolidate-project-folders

The skill successfully guided a real, isolated consolidation of two overlapping fixture projects. No real user project files or installed skills were changed. All generated files, migration work, evidence, test profiles and runtime copies are under `<LOCAL_TEST_WORKSPACE>`.

## Outcome

- Baseline: 43 files across two inputs plus a preexisting destination; 21 distinct byte contents; no unreadable/unstable files, links or scan errors.
- Final destination: 38 loose files including two primary HTML apps, two complete editable source trees, company/demo datasets, original metadata, distinct archive containers, all three same-name note variants, rollback routing and new current routing/help.
- All 43 original file paths have an exact keeper or exact ZIP-member map. Content coverage: 21/21 unique contents, zero missing, zero archive errors. Six historical-version members and one existing archive member were streamed and verified.
- Both input roots are now empty. 42 original input files were removed only after current source/keeper size and SHA-256 revalidation; the original destination note was retained in place. No blanket recursive deletion was used.
- Two redundant standalone brief copies were removed: 152 bytes of logical duplicate payload eliminated. Net destination payload is +659 bytes relative to the combined baseline because the tiny historical ZIP and new routing/help add overhead. Physical disk allocation, compression allocation, browser-profile size and cloud quota were not measured.
- Required duplicate dependencies remain: 10 same-hash groups among primary app/source families, including shared JS/CSS/SVG/config/data. Final whole-destination logical duplicate count: 16; it is not a deletion backlog.

## Selection and link criteria

VisitorDesk-2 is primary because it has the intended current interface, a distinct three-record dataset, and complete editable source; FieldGuide is a separate functional product and remains primary. VisitorDesk-1 has unique historical records/config/title and is archived intact. Dates and filenames were not used as proof of equivalence. Every same-name notes variant has different bytes and remains separately accessible. Company and demo data stay separate.

Original START-HERE had one preexisting missing help target. The new START-HERE repairs cross-folder routing, retains meaningful `#trails` fragments, and supplies a help target. Static checks found zero broken active HTML resource/navigation/fragment links. Original routing bytes remain under `rollback/`; its three obsolete relative references are deliberately recorded as provenance-only failures and are not counted as active navigation. Source trees retain their complete relative layout; no generator emitted the root START-HERE, so no generator changes were necessary.

## Verification

The staged helper's inventory, ZIP-member coverage and tree commands passed. Per-file map and append-only action log independently account for completed changes. Both original empty directories were re-created in the appropriate preserved app/source families. Hidden metadata content was inventoried and retained.

An isolated copy of the destination ran in headless Edge with its own fixture-local profile and a read-only loopback HTTP server. Both apps loaded local JSON and image/CSS/JS dependencies; VisitorDesk displayed 3 records then 2 after Active only; FieldGuide displayed 2 then 1. START-HERE exposed five expected routes. Runtime exception/loading-failure diagnostics were empty. Screenshots are retained; VisitorDesk screenshot was visually inspected. The protected destination was not used as a writable test workspace.

## Findings and limits

No material safety flaw in the skill was observed. Its explicit preservation of duplicate dependencies, destination inventory, per-file accounting, current-keeper revalidation, archive-member hashing and authorization reuse were useful and actionable. No skill change is required by this successful forward test.

Minor optional clarity improvements: distinguish removal of verified migrated originals from deletion of redundant standalone copies when reporting action counts; describe whether hidden-file preservation promises content only or also filesystem attributes. The test retained hidden-file content; ACLs, NTFS alternate streams, timestamps/attributes, symlinks, junctions, hardlinks, locked files, cloud placeholders, live writers/WAL databases, shortcuts and OOXML were outside this synthetic scope. Native script execution policy and sandbox loopback restrictions caused recorded environment failures, resolved without changing security controls. The intermediate report-key error was a test-harness mistake, not a skill defect.

No rebuild, deployment, live integrations, production data acceptance, physical-space measurement or complete browser acceptance suite is claimed. Archive member recovery bytes were verified without extraction; historical UI startup was not tested. Test-profile/cache files and runtime copies are non-authoritative test infrastructure, retained inside this fixture and excluded from destination savings. The harness closed its HTTP server and requested termination of its own Edge child; independent OS-level absence of every Edge descendant was not verified because the process-inventory CIM query was denied.

## Evidence routing

- `destination/START-HERE.html`: current collection entry point.
- `evidence/before.json`, `after.json`: complete baseline/final size/hash inventories.
- `evidence/coverage.json`: zero-missing content and verified ZIP members.
- `evidence/file-map.json`, `actions.jsonl`: all originals, keepers, archive members, reasons and completed cleanup.
- `evidence/retention-criteria.json`, `duplicate-exceptions.json`, `archive-restore-map.json`: selection, intentional duplicates and restoration mapping.
- `evidence/folder-tree.txt`: complete final destination tree.
- `evidence/links-before.json`, `links-after.json`, `browser-results.json`, `VisitorDesk.png`, `FieldGuide.png`: static/runtime evidence.
- `evidence/environment-failures.json`: preserved environment/harness failures and recovery.
- `evidence/audit-supplement.json`: size/hash list for evidence and test scripts; explicitly excludes its own self-reference. Browser profiles/runtime copies are excluded test infrastructure.

Action categories: `{"archived-distinct-version": 6, "consolidated": 34, "retained-preexisting": 1, "verified-redundant-standalone": 2}`.
