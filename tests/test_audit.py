"""Contract tests on temporary fixtures; never operates on user projects."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/consolidate-project-folders/scripts/consolidation_audit.py'


class AuditTests(unittest.TestCase):
    def setUp(self):
        fixture_parent = Path(__file__).parent.resolve() / 'test-tmp'
        fixture_parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='consolidation-skill-', dir=fixture_parent)
        assert Path(self.temp.name).resolve().parent == fixture_parent
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.src = self.base / 'input'
        self.src.mkdir()
        (self.src / 'bundle').mkdir()
        (self.src / 'empty').mkdir()
        (self.src / 'bundle/logo.txt').write_bytes(b'needed shared asset')
        (self.src / 'duplicate.txt').write_bytes(b'needed shared asset')
        (self.src / 'source.py').write_bytes(b'print("unique source")\n')
        (self.src / '.config').write_bytes(b'demo=true')
        self.baseline = self.hashes()

    def hashes(self):
        return {str(p.relative_to(self.src)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.src.rglob('*') if p.is_file()}

    def run_cli(self, *args, code=0):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def inv(self, root, name='before.json', code=0):
        path = self.base / name
        self.run_cli('inventory', '--root', root, '--out', path, code=code)
        return path

    def archive(self, *, corrupt=False, wrong=False):
        dest = self.base / 'output'
        dest.mkdir()
        archive = dest / 'older.zip'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_STORED) as z:
            for p in self.src.rglob('*'):
                if p.is_file():
                    data = p.read_bytes()
                    if wrong and p.name == 'source.py':
                        data = b'different version'
                    z.writestr('older/' + p.relative_to(self.src).as_posix(), data)
        if corrupt:
            data = archive.read_bytes()
            self.assertIn(b'needed shared asset', data)
            archive.write_bytes(data.replace(b'needed shared asset', b'NEEDED shared asset', 1))
        return dest, archive

    def test_inventory_groups_hidden_empty_and_tree(self):
        report = self.inv(self.src)
        doc = json.loads(report.read_text())
        self.assertEqual(doc['summary']['files'], 4)
        self.assertEqual(doc['summary']['duplicate_groups'], 1)
        self.assertEqual(doc['summary']['unique_contents'], 3)
        self.assertTrue(any(r['relative'] == '.config' for r in doc['files']))
        tree = self.base / 'tree.txt'
        self.run_cli('tree', '--inventory', report, '--out', tree)
        self.assertIn('empty/', tree.read_text())
        self.assertEqual(self.hashes(), self.baseline)

    def test_refuses_report_overwrite_and_recursive_output(self):
        report = self.inv(self.src)
        contents = report.read_bytes()
        self.run_cli('inventory', '--root', self.src, '--out', report, code=2)
        self.assertEqual(contents, report.read_bytes())
        bad = self.src / 'report.json'
        self.run_cli('inventory', '--root', self.src, '--out', bad, code=2)
        self.assertFalse(bad.exists())
        self.assertEqual(self.hashes(), self.baseline)

    def test_overlapping_roots_rejected(self):
        report = self.base / 'bad.json'
        self.run_cli('inventory', '--root', self.src, '--root', self.src / 'bundle',
                     '--out', report, code=2)
        self.assertFalse(report.exists())

    def test_coverage_after_rename_and_same_name_collision(self):
        before = self.inv(self.src)
        dest = self.base / 'output'
        dest.mkdir()
        for i, p in enumerate(self.src.rglob('*')):
            if p.is_file():
                (dest / ('renamed-%d.bin' % i)).write_bytes(p.read_bytes())
        (dest / 'source.py').write_bytes(b'different version')
        after = self.inv(dest, 'after.json')
        report = self.base / 'coverage.json'
        self.run_cli('coverage', '--before', before, '--after', after, '--out', report)
        self.assertEqual(json.loads(report.read_text())['summary']['missing_unique_contents'], 0)
        self.assertEqual(self.hashes(), self.baseline)

    def test_missing_unique_fails(self):
        before = self.inv(self.src)
        dest = self.base / 'output'
        dest.mkdir()
        (dest / 'source.py').write_bytes(b'different version')
        after = self.inv(dest, 'after.json')
        report = self.base / 'coverage.json'
        self.run_cli('coverage', '--before', before, '--after', after, '--out', report, code=2)
        self.assertGreater(json.loads(report.read_text())['summary']['missing_unique_contents'], 0)

    def test_exact_zip_member_coverage(self):
        before = self.inv(self.src)
        dest, archive = self.archive()
        after = self.inv(dest, 'after.json')
        report = self.base / 'coverage.json'
        self.run_cli('coverage', '--before', before, '--after', after,
                     '--zip-members', '--out', report)
        doc = json.loads(report.read_text())
        self.assertEqual(doc['summary']['missing_unique_contents'], 0)
        self.assertEqual(len(doc['archives']), 1)
        self.assertTrue(all(m['evidence'][0]['kind'] == 'zip-member' for m in doc['matches']))
        self.assertEqual(self.hashes(), self.baseline)

    def test_same_zip_member_name_different_bytes_fails(self):
        before = self.inv(self.src)
        dest, archive = self.archive(wrong=True)
        after = self.inv(dest, 'after.json')
        report = self.base / 'coverage.json'
        self.run_cli('coverage', '--before', before, '--after', after,
                     '--zip-members', '--out', report, code=2)
        self.assertEqual(json.loads(report.read_text())['summary']['missing_unique_contents'], 1)

    def test_corrupt_archive_fails(self):
        before = self.inv(self.src)
        dest, archive = self.archive(corrupt=True)
        after = self.inv(dest, 'after.json')
        report = self.base / 'coverage.json'
        self.run_cli('coverage', '--before', before, '--after', after,
                     '--zip-members', '--out', report, code=2)
        self.assertEqual(json.loads(report.read_text())['summary']['archive_errors'], 1)

    def test_archive_limits_fail_without_extraction(self):
        before = self.inv(self.src)
        dest, archive = self.archive()
        after = self.inv(dest, 'after.json')
        report = self.base / 'coverage.json'
        self.run_cli('coverage', '--before', before, '--after', after, '--zip-members',
                     '--max-member-bytes', 1, '--out', report, code=2)
        self.assertEqual(json.loads(report.read_text())['summary']['archive_errors'], 1)
        self.assertEqual([p.name for p in dest.iterdir()], ['older.zip'])

    def test_changed_archive_since_snapshot_fails(self):
        before = self.inv(self.src)
        dest, archive = self.archive()
        after = self.inv(dest, 'after.json')
        archive.write_bytes(archive.read_bytes() + b'changed')
        report = self.base / 'coverage.json'
        self.run_cli('coverage', '--before', before, '--after', after,
                     '--zip-members', '--out', report, code=2)
        self.assertEqual(json.loads(report.read_text())['summary']['archive_errors'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
