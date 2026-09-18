import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('reset', Path(__file__).with_name('reset.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ResetTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        (self.root / '.exp-workbench.json').write_text(json.dumps(module.WORKBENCH))
        (self.root / 'AGENTS.md').write_text('keep')
        self.names = ['2026-09-17-alpha', '2026-09-17-beta', '2026-09-18-\u4e2d\u6587']
        for name in self.names:
            folder = self.root / name
            folder.mkdir()
            (folder / '.exp-project.json').write_text(json.dumps(module.PROJECT))
            (folder / '.env').write_text('example local data')

    def test_list_and_preview_do_not_mutate(self):
        self.assertEqual(module.reset(self.root)['available'], self.names)
        self.assertFalse(module.reset(self.root, self.names[:2])['applied'])
        self.assertFalse((self.root / '.practice-backups').exists())
        self.assertTrue(all((self.root / n).exists() for n in self.names))

    def test_single_and_multi_selection_preserve_unselected_and_toolkit(self):
        for selected in ([self.names[0]], self.names[1:]):
            result = module.reset(self.root, selected, True)
            for name in selected:
                self.assertFalse((self.root / name).exists())
                self.assertEqual((Path(result['backup']) / name / '.env').read_text(), 'example local data')
            self.assertEqual((self.root / 'AGENTS.md').read_text(), 'keep')
            if len(selected) == 1:
                self.assertTrue((self.root / self.names[1]).exists())

    def test_invalid_selection_rejects_entire_batch(self):
        for bad in ('../outside', 'AGENTS.md', 'scaffold', '2026-09-17-missing'):
            with self.assertRaises(ValueError):
                module.reset(self.root, [self.names[0], bad], True)
            self.assertTrue((self.root / self.names[0]).exists())
        with self.assertRaises(ValueError):
            module.reset(self.root, apply=True)

    def test_symlink_targets_and_backup_are_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            link = self.root / '2026-09-17-link'
            link.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                module.reset(self.root, [link.name], True)
            (self.root / '.practice-backups').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                module.reset(self.root, [self.names[0]], True)

    def test_nested_symlink_is_archived_without_following(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'keep'
            target.write_text('untouched')
            (self.root / self.names[0] / 'link').symlink_to(target)
            result = module.reset(self.root, [self.names[0]], True)
            self.assertTrue((Path(result['backup']) / self.names[0] / 'link').is_symlink())
            self.assertEqual(target.read_text(), 'untouched')

    def test_move_failure_rolls_back_completed_moves(self):
        original = Path.rename
        def failing(path, target):
            if path == self.root / self.names[1]:
                raise OSError('simulated failure')
            return original(path, target)
        with patch.object(Path, 'rename', failing):
            with self.assertRaises(OSError):
                module.reset(self.root, self.names[:2], True)
        self.assertTrue(all((self.root / name / '.env').exists() for name in self.names))

    def test_unmarked_and_missing_workbench_rejected(self):
        (self.root / self.names[0] / '.exp-project.json').unlink()
        self.assertNotIn(self.names[0], module.reset(self.root)['available'])
        (self.root / '.exp-workbench.json').unlink()
        with self.assertRaises(ValueError):
            module.reset(self.root)


if __name__ == '__main__':
    unittest.main()
