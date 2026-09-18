"""Exercise the documented CLI contract from a fresh scaffold copy."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicWorkflowTests(unittest.TestCase):
    def test_scaffold_verify_run_status_and_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            shutil.copy2(ROOT / '.exp-workbench.json', workspace)
            project = workspace / '2026-09-16-smoke'
            shutil.copytree(ROOT / 'scaffold', project)
            (project / 'SPEC.md').write_text('- **AC-01**: The saved value is readable.\n')
            (project / 'value.txt').write_text('saved')
            (project / 'check.py').write_text('''import json, os
from pathlib import Path
assert Path('value.txt').read_text() == 'saved'
Path(os.environ['EXP_ARTIFACT_DIR'], 'value.txt').write_text('saved')
Path(os.environ['EXP_RESULT_PATH']).write_text(json.dumps({'cases': [
    {'id': 'read', 'criterion': 'AC-01', 'status': 'pass'}]}))
''')
            (project / 'acceptance.json').write_text(json.dumps({'version': 1, 'checks': [{
                'id': 'value', 'command': [sys.executable, 'check.py'],
                'timeoutSeconds': 10, 'cases': [{'id': 'read', 'criterion': 'AC-01'}],
                'artifacts': ['value.txt']}]}))

            def cli(command, expected=0):
                result = subprocess.run([sys.executable, str(ROOT / 'harness/cli.py'),
                                         command, '--project', str(project)],
                                        cwd=workspace, capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return json.loads(result.stdout)

            self.assertFalse(cli('status', 1)['fresh'])
            self.assertEqual(cli('verify')['status'], 'pass')
            status = cli('status')
            self.assertEqual(status['verificationStatus'], 'pass')
            self.assertEqual(status['controllerPhase'], 'inactive')
            (project / '.harness/state.json').write_text(json.dumps({
                'phase': 'blocked', 'active': False, 'reason': 'Previous repair stopped'}))
            self.assertEqual(cli('status')['controllerPhase'], 'blocked')
            self.assertEqual(cli('run')['phase'], 'complete')
            self.assertTrue(cli('status')['fresh'])
            (project / 'value.txt').write_text('changed')
            self.assertFalse(cli('status', 1)['fresh'])
            self.assertEqual(cli('verify', 1)['status'], 'error')
            self.assertIsNone(cli('status', 1)['verificationStatus'])
            check = project / 'check.py'
            check.write_text(check.read_text().replace(
                "assert Path('value.txt').read_text() == 'saved'",
                "ok = Path('value.txt').read_text() == 'saved'").replace(
                "'status': 'pass'", "'status': 'pass' if ok else 'fail'"))
            self.assertEqual(cli('verify', 1)['status'], 'fail')
            failure = cli('status', 1)
            self.assertTrue(failure['fresh'])
            self.assertEqual(failure['verificationStatus'], 'fail')
            self.assertEqual(failure['controllerPhase'], 'complete')

            # Run the real reset CLI at its documented relative installation path.
            scripts = workspace / '.agents/skills/exp-reset/scripts'
            scripts.mkdir(parents=True)
            shutil.copy2(ROOT / '.agents/skills/exp-reset/scripts/reset.py', scripts)
            command = [sys.executable, str(scripts / 'reset.py')]
            preview = json.loads(subprocess.check_output(command, cwd=directory, text=True))
            self.assertEqual(preview['available'], [project.name])
            archived = json.loads(subprocess.check_output(
                command + ['--project', project.name, '--apply'], cwd=directory, text=True))
            self.assertTrue(archived['applied'])
            self.assertFalse(project.exists())
            self.assertTrue((Path(archived['backup']) / project.name / 'value.txt').is_file())


if __name__ == '__main__':
    unittest.main()
