# Audit contract and helper

## Read-only helper

Python 3.10+; standard library only. Run the installed skill's absolute script path. Examples assume the shell is in the skill folder. Keep reports outside input roots, or inside a directory explicitly excluded from the scan. Reports refuse to overwrite existing files.

```powershell
python scripts/consolidation_audit.py inventory --root "C:\Projects\Collection-A" --root "C:\Projects\Collection-B" --out "C:\Audit\run-01\before.json"
python scripts/consolidation_audit.py inventory --root "C:\Projects\Consolidated" --out "C:\Audit\run-01\after.json"
python scripts/consolidation_audit.py coverage --before "C:\Audit\run-01\before.json" --after "C:\Audit\run-01\after.json" --out "C:\Audit\run-01\coverage.json"
python scripts/consolidation_audit.py tree --inventory "C:\Audit\run-01\after.json" --out "C:\Audit\run-01\folders.txt"
```

`inventory` hashes all regular files, including hidden/dependency files, and records empty directories. Repeat `--root`/`--exclude` as needed. Overlapping roots are rejected to prevent double counting. Symlinks/junctions are recorded without traversal. Denied, unstable and unreadable files remain findings. Exit 2 means incomplete coverage; default workers: four.

`coverage` proves original byte-content presence in supplied snapshots, independent of layout. It does not rehash current loose files, infer bundle safety, authorize deletion, reconcile intentional edits or prove action counts. Use fresh inventories and the migration map; rehash actual keepers before deletion. Inspect exact archive members with:

```powershell
python scripts/consolidation_audit.py coverage --before "C:\Audit\run-01\before.json" --after "C:\Audit\run-01\after.json" --zip-members --out "C:\Audit\run-01\coverage-with-archives.json"
```

This rehashes each current ZIP against its after-snapshot, streams members through CRC/SHA-256 and checks outer-file stability. No extraction. Default limits: 2 GiB/member, 10 GiB total uncompressed bytes; raise `--max-member-bytes`/`--max-total-bytes` explicitly for larger authorized archives. Encryption, limit hits and CRC errors are findings. Nested ZIP payloads count as bytes; their contents are not recursively inspected.

Preserve originals/rollback bytes for intentional edits, or record approved transformations separately. Do not conceal missing hashes by removing baseline rows. Deliberately retired unique containers require explicit accounting beyond this content-only helper.

## Before destruction

Resolve the file/target and approved scopes. Verify current regular-file/link status, size/hash and retained destination or exact archive member. A keeper must not be the same physical file, a hard-link alias mistaken for another backup, another deletion candidate, or a ZIP slated for retirement. Every removal chain must terminate at a retained accessible survivor. Revalidate after earlier operations that could change that survivor.

Use allowlisted fully resolved paths and `-LiteralPath` on Windows. Do not enumerate in one shell and delete/move in another. Guard parent/child destinations against recursively copying newly generated outputs into themselves.

## Evidence

| Artifact | Required fields/evidence |
|---|---|
| Inventory | Run/time, roots, exclusions, root/relative/absolute path, bytes, hash, stability/read status, directories, links, scan errors |
| File map | Original path/hash, action, destination or keeper/archive/member/hash, bundle/version, rationale, verification |
| Action log | Time, operation, exact source/target, expected/observed hashes, result/error; append after mutations |
| Retention decisions | Primary/archive/source/retirement role, unique content/functionality, provenance, tests, owner decision/authority |
| Duplicate exceptions | Same-hash group, retained paths, bundle/dependency reason |
| Verification | Fresh inventories, content/accounting coverage, archive checks, link baseline/final, data/app checks, unresolved findings |

Do not put credentials, personal records or operational database copies into general audit deliverables. Hashes, aggregate counts and schema summaries usually suffice.

## Claims

- Names/dates do not prove duplication or precedence.
- ZIP listings do not prove recoverable bytes.
- Same EXEs do not prove identical data/configuration.
- A repaired output may deliberately differ: preserve the original or record the authorized transformation and verify the edit.
- Separate logical duplicate bytes, actual physical savings, compression/hard links and cloud quota. Local reads do not establish cloud synchronization.
- A staged plan, completed copy, verified deletion and tested app are separate statuses.
