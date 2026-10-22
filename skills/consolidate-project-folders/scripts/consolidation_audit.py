#!/usr/bin/env python3
"""Read-only project inventories, snapshot content coverage and folder trees."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from datetime import datetime, timezone
import zipfile

SCHEMA = 'consolidation-inventory-v1'


def inside(path, root):
    try:
        return os.path.commonpath([str(path), str(root)]) == str(root)
    except ValueError:
        return False


def linked(path):
    s = path.lstat()
    return (stat.S_ISLNK(s.st_mode) or
            getattr(s, 'st_reparse_tag', 0) == 0xA0000003)


def signature(s):
    # Windows stat/fstat can disagree on ctime; do not use it as a stability key.
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value, raw=False):
    path = Path(path).resolve()
    if path.exists():
        raise ValueError('Refusing to overwrite report: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(value if raw else json.dumps(value, indent=2, ensure_ascii=False))
        f.write('\n')


def load(path):
    obj = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if obj.get('schema') != SCHEMA:
        raise ValueError('Expected an inventory created by this helper: ' + str(path))
    return obj


def inspect(row):
    p = Path(row['path'])
    try:
        if linked(p) or not inside(p.resolve(strict=True), Path(row['root'])):
            raise ValueError('Link or path changed/outside root')
        before = p.stat()
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('Not a regular file')
        h = hashlib.sha256()
        with p.open('rb') as f:
            opened = os.fstat(f.fileno())
            for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
                h.update(block)
            closed = os.fstat(f.fileno())
        after = p.stat()
        if linked(p) or not inside(p.resolve(strict=True), Path(row['root'])):
            raise ValueError('Link or path changed during read')
        row.update(bytes=before.st_size, mtime_ns=before.st_mtime_ns)
        if not (signature(before) == signature(opened) == signature(closed) == signature(after)):
            row.update(status='unstable', error='File changed during read')
        else:
            row.update(status='ok', sha256=h.hexdigest())
    except (OSError, ValueError) as exc:
        row.update(status='error', error=str(exc))
    return row


def inventory(args):
    roots = []
    for text in args.root:
        p = Path(text).resolve(strict=True)
        if not p.is_dir():
            raise ValueError('Root is not a directory: ' + str(p))
        if p not in roots:
            roots.append(p)
    for i, a in enumerate(roots):
        for b in roots[i + 1:]:
            if inside(a, b) or inside(b, a):
                raise ValueError('Overlapping roots; scan their common parent once: %s / %s' % (a, b))
    excludes = [Path(p).resolve() for p in args.exclude]
    out = Path(args.out).resolve()
    if out.exists():
        raise ValueError('Report already exists: ' + str(out))
    if any(inside(out, r) for r in roots) and not any(inside(out, e) for e in excludes):
        raise ValueError('Report must be outside roots or inside an explicitly excluded directory')
    if any(inside(r, e) for r in roots for e in excludes):
        raise ValueError('An exclusion would exclude an entire selected root')
    rows, directories, links, errors = [], [], [], []
    excluded = lambda p: any(inside(p, e) for e in excludes)
    for i, root in enumerate(roots, 1):
        rid = 'R%02d' % i
        def onerror(exc):
            errors.append({'root_id': rid, 'path': exc.filename, 'error': str(exc)})
        for dp, dns, fns in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
            parent = Path(dp)
            directories.append({'root_id': rid, 'relative': parent.relative_to(root).as_posix()})
            for name in list(dns):
                q = parent / name
                try:
                    if excluded(q):
                        dns.remove(name)
                    elif linked(q):
                        links.append({'root_id': rid, 'path': str(q), 'kind': 'directory-link', 'target': str(q.resolve())})
                        dns.remove(name)
                except OSError as exc:
                    errors.append({'root_id': rid, 'path': str(q), 'error': str(exc)})
                    dns.remove(name)
            for name in fns:
                q = parent / name
                if excluded(q):
                    continue
                row = {'root_id': rid, 'root': str(root), 'relative': q.relative_to(root).as_posix(), 'path': str(q)}
                try:
                    if linked(q):
                        links.append({'root_id': rid, 'path': str(q), 'kind': 'file-link', 'target': str(q.resolve())})
                    else:
                        rows.append(row)
                except OSError as exc:
                    row.update(status='error', error=str(exc))
                    rows.append(row)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        files = list(pool.map(inspect, rows))
    files.sort(key=lambda r: (r['root_id'], r['relative']))
    groups = {}
    for row in files:
        if row['status'] == 'ok':
            groups.setdefault((row['bytes'], row['sha256']), []).append(row['path'])
    duplicates = [{'bytes': size, 'sha256': digest, 'paths': paths}
                  for (size, digest), paths in groups.items() if len(paths) > 1]
    summary = {'files': len(files), 'directories': len(directories),
               'readable_bytes': sum(r.get('bytes', 0) for r in files if r['status'] == 'ok'),
               'unique_contents': len(groups), 'duplicate_groups': len(duplicates),
               'logical_extra_copies': sum(len(g['paths']) - 1 for g in duplicates),
               'file_findings': sum(r['status'] != 'ok' for r in files),
               'walk_errors': len(errors), 'links_not_followed': len(links)}
    complete = not (summary['file_findings'] or errors or links)
    result = {'schema': SCHEMA, 'created_utc': datetime.now(timezone.utc).isoformat(),
              'roots': [{'id': 'R%02d' % i, 'path': str(p)} for i, p in enumerate(roots, 1)],
              'exclusions': [str(p) for p in excludes], 'summary': summary,
              'complete_regular_file_scan': complete, 'files': files,
              'directories': directories, 'links': links, 'errors': errors,
              'duplicate_groups': duplicates,
              'warning': 'Content duplicates are not deletion candidates until bundle and keeper checks.'}
    save(out, result)
    return summary, 0 if complete else 2


def coverage(args):
    before, after = load(args.before), load(args.after)
    wanted = {}
    available = {}
    for row in before['files']:
        if row['status'] == 'ok':
            wanted.setdefault((row['bytes'], row['sha256']), []).append(row['path'])
    for row in after['files']:
        if row['status'] == 'ok':
            available.setdefault((row['bytes'], row['sha256']), []).append({'kind': 'loose', 'path': row['path']})
    errors, archives = [], []
    total = 0
    if args.zip_members:
        for row in after['files']:
            if row['status'] != 'ok' or Path(row['path']).suffix.lower() != '.zip':
                continue
            p = Path(row['path'])
            found = []
            try:
                if linked(p):
                    raise ValueError('ZIP changed to a link')
                start = p.stat()
                if start.st_size != row['bytes'] or file_hash(p) != row['sha256']:
                    raise ValueError('ZIP differs from after-snapshot')
                with zipfile.ZipFile(p) as z:
                    for member in z.infolist():
                        if member.is_dir():
                            continue
                        if member.file_size > args.max_member_bytes or total + member.file_size > args.max_total_bytes:
                            raise ValueError('Uncompressed member/total limit reached; archive not certified')
                        total += member.file_size
                        h, count = hashlib.sha256(), 0
                        with z.open(member) as f:
                            for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
                                count += len(block)
                                if count > member.file_size or count > args.max_member_bytes:
                                    raise ValueError('Member expanded beyond its declared/allowed size')
                                h.update(block)
                        if count != member.file_size:
                            raise ValueError('Member length mismatch')
                        found.append(((count, h.hexdigest()), {'kind': 'zip-member', 'path': str(p), 'member': member.filename, 'archive_sha256': row['sha256']}))
                if signature(start) != signature(p.stat()) or file_hash(p) != row['sha256']:
                    raise ValueError('ZIP changed during inspection')
                for key, location in found:
                    available.setdefault(key, []).append(location)
                archives.append({'path': str(p), 'members_verified': len(found), 'status': 'ok'})
            except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, NotImplementedError) as exc:
                errors.append({'path': str(p), 'error': str(exc)})
    matches, missing = [], []
    for key, sources in wanted.items():
        target = matches if key in available else missing
        record = {'bytes': key[0], 'sha256': key[1], 'original_paths': sources}
        if key in available:
            record['evidence'] = available[key]
        target.append(record)
    scans_complete = before['complete_regular_file_scan'] and after['complete_regular_file_scan']
    ok = scans_complete and not missing and not errors
    summary = {'status': 'CONTENT_COVERED_IN_SNAPSHOTS' if ok else 'INCOMPLETE_OR_MISSING',
               'original_unique_contents': len(wanted), 'covered_unique_contents': len(matches),
               'missing_unique_contents': len(missing), 'archive_errors': len(errors),
               'both_scans_complete': scans_complete, 'zip_uncompressed_bytes_read': total}
    save(args.out, {'schema': 'consolidation-coverage-v1', 'summary': summary,
                    'missing': missing, 'matches': matches, 'archives': archives, 'errors': errors,
                    'limits': 'Snapshot content only; no deletion authority, bundle/link/runtime proof or current loose-file revalidation.'})
    return summary, 0 if ok else 2


def tree(args):
    doc = load(args.inventory)
    lines = [doc['created_utc'], 'Snapshot status: ' + ('complete' if doc['complete_regular_file_scan'] else 'INCOMPLETE'), '']
    for root in doc['roots']:
        lines.append(root['path'])
        items = {}
        for d in doc['directories']:
            if d['root_id'] == root['id'] and d['relative'] != '.':
                items[d['relative']] = None
        for f in doc['files']:
            if f['root_id'] == root['id']:
                items[f['relative']] = f
        children = {}
        for name, row in items.items():
            parent = str(Path(name).parent).replace('\\', '/')
            children.setdefault(parent, []).append((name, row))
        def emit(parent, prefix=''):
            entries = sorted(children.get(parent, []), key=lambda x: (x[1] is not None, x[0]))
            for i, (name, row) in enumerate(entries):
                last = i == len(entries) - 1
                label = name.rsplit('/', 1)[-1]
                label += '/' if row is None else ' [%s; %s bytes]' % (row['status'], row.get('bytes', '?'))
                lines.append(prefix + ('`-- ' if last else '|-- ') + label)
                if row is None:
                    emit(name, prefix + ('    ' if last else '|   '))
        emit('.')
        root_links = [x for x in doc['links'] if x['root_id'] == root['id']]
        if root_links:
            lines.append('Links not followed:')
            lines.extend('  ' + x['path'] + ' -> ' + x['target'] for x in root_links)
        lines.append('')
    save(args.out, '\n'.join(lines), raw=True)
    return {'roots': len(doc['roots']), 'files': len(doc['files']), 'out': str(Path(args.out).resolve())}, 0


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('must be positive')
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('inventory'); p.add_argument('--root', action='append', required=True)
    p.add_argument('--exclude', action='append', default=[]); p.add_argument('--out', required=True)
    p.add_argument('--workers', type=positive, default=4); p.set_defaults(run=inventory)
    p = sub.add_parser('coverage'); p.add_argument('--before', required=True); p.add_argument('--after', required=True)
    p.add_argument('--zip-members', action='store_true'); p.add_argument('--out', required=True)
    p.add_argument('--max-member-bytes', type=positive, default=2 * 1024**3)
    p.add_argument('--max-total-bytes', type=positive, default=10 * 1024**3); p.set_defaults(run=coverage)
    p = sub.add_parser('tree'); p.add_argument('--inventory', required=True); p.add_argument('--out', required=True); p.set_defaults(run=tree)
    args = parser.parse_args()
    if getattr(args, 'workers', 1) > 32:
        parser.error('--workers must be <= 32')
    try:
        summary, code = args.run(args)
        print(json.dumps(summary, ensure_ascii=True))
        return code
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
