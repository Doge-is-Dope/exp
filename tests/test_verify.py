import json
import os
from pathlib import Path
import sys
import signal
import subprocess
import time
import tempfile
import unittest
from harness.verify import VerificationError, current_report, fingerprint, load_contract, verify


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        (self.project / 'SPEC.md').write_text('- **AC-01**: Works\n')
        self.manifest = {'version': 1, 'checks': [{'id': 'test', 'command': [sys.executable, 'check.py'], 'timeoutSeconds': 3, 'cases': [{'id': 'works', 'criterion': 'AC-01'}]}]}
        self.save()
        self.script()

    def save(self):
        (self.project / 'acceptance.json').write_text(json.dumps(self.manifest))

    def script(self, status='pass', prefix='', suffix=''):
        (self.project / 'check.py').write_text(prefix + '\nimport json, os\nfrom pathlib import Path\nPath(os.environ["EXP_RESULT_PATH"]).write_text(json.dumps({"cases": [{"id": "works", "criterion": "AC-01", "status": ' + repr(status) + '}]}))\n' + suffix)

    def test_pass_and_fresh_report(self):
        report = verify(self.project)
        self.assertEqual(report['status'], 'pass', report)
        self.assertEqual(current_report(self.project), report)
        self.assertTrue((self.project / report['checks'][0]['logs']['stdout']).is_file())

    def test_no_cases_and_missing_criterion_prevent_execution(self):
        for mutation in ('empty', 'missing'):
            with self.subTest(mutation=mutation):
                self.script(prefix='raise RuntimeError("should never execute")')
                if mutation == 'empty':
                    self.manifest['checks'][0]['cases'] = []
                    self.save()
                else:
                    self.manifest['checks'][0]['cases'] = [{'id': 'works', 'criterion': 'AC-01'}]
                    self.save()
                    (self.project / 'SPEC.md').write_text('- **AC-01**: Works\n- **AC-02**: Other\n')
                report = verify(self.project)
                self.assertEqual(report['status'], 'error')
                self.assertEqual(report['checks'], [])

    def test_skip_fail_error_never_pass(self):
        for status in ('skip', 'fail', 'error'):
            with self.subTest(status=status):
                self.script(status)
                self.assertNotEqual(verify(self.project)['status'], 'pass')

    def test_nonzero_exit_with_passing_json(self):
        self.script(suffix='raise SystemExit(2)')
        report = verify(self.project)
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['checks'][0]['exitCode'], 2)

    def test_corrupt_empty_extra_duplicate_results(self):
        payloads = ['not JSON', '{"cases": []}', json.dumps({'cases': [{'id': 'other', 'criterion': 'AC-01', 'status': 'pass'}]}), json.dumps({'cases': [{'id': 'works', 'criterion': 'AC-01', 'status': 'pass'}] * 2})]
        for payload in payloads:
            with self.subTest(payload=payload):
                self.script(suffix='Path(os.environ["EXP_RESULT_PATH"]).write_text(' + repr(payload) + ')')
                self.assertEqual(verify(self.project)['status'], 'error')

    def test_missing_and_escaped_artifact(self):
        self.manifest['checks'][0]['artifacts'] = ['proof.txt']
        self.save()
        self.assertEqual(verify(self.project)['status'], 'error')
        self.script(suffix='Path(os.environ["EXP_ARTIFACT_DIR"], "proof.txt").symlink_to(Path("SPEC.md").resolve())')
        self.assertEqual(verify(self.project)['status'], 'error')

    def test_artifact_integrity(self):
        self.manifest['checks'][0]['artifacts'] = ['proof.txt']
        self.save()
        self.script(suffix='Path(os.environ["EXP_ARTIFACT_DIR"], "proof.txt").write_text("evidence")')
        report = verify(self.project)
        self.assertEqual(report['status'], 'pass', report)
        artifact = self.project / report['checks'][0]['artifacts'][0]['path']
        self.assertIsNotNone(current_report(self.project))
        artifact.write_text('tampered')
        self.assertIsNone(current_report(self.project))

    def test_untracked_spec_and_check_changes_stale(self):
        for target in ('new-app.py', 'SPEC.md', 'check.py', 'acceptance.json'):
            with self.subTest(target=target):
                self.save()
                self.script()
                (self.project / 'SPEC.md').write_text('- **AC-01**: Works\n')
                report = verify(self.project)
                self.assertEqual(report['status'], 'pass', report)
                path = self.project / target
                path.write_text((path.read_text() if path.exists() else '') + '\n')
                self.assertIsNone(current_report(self.project))

    def test_concurrent_modification_rejects_evidence(self):
        self.script(suffix='Path("app.py").write_text("changed during check")')
        report = verify(self.project)
        self.assertEqual(report['status'], 'error')
        self.assertIn('changed during', report['errors'][0])

    def test_environment_change_invalidates(self):
        report = verify(self.project)
        self.assertEqual(report['status'], 'pass')
        os.environ['EXP_TEST_ENV_CHANGE'] = 'different'
        try:
            self.assertIsNone(current_report(self.project))
        finally:
            del os.environ['EXP_TEST_ENV_CHANGE']

    def test_runtime_paths_and_unsafe_exclusions(self):
        self.manifest['runtimePaths'] = ['.data']
        self.save()
        before = fingerprint(self.project)
        (self.project / '.data').mkdir()
        (self.project / '.data' / 'tasks.json').write_text('[]')
        self.assertEqual(before, fingerprint(self.project))
        for value in ('check.py', '.', '../escape', '/tmp', 'src'):
            self.manifest['runtimePaths'] = [value]
            self.save()
            with self.assertRaises(VerificationError):
                load_contract(self.project)

    def test_timeout_cleans_descendant(self):
        self.manifest['checks'][0]['timeoutSeconds'] = 0.2
        self.save()
        late = self.project / '.harness' / 'late.txt'
        child = 'import time; from pathlib import Path; time.sleep(0.6); Path(' + repr(str(late)) + ').write_text("escaped")'
        self.script(prefix='import subprocess, sys, time\nsubprocess.Popen([sys.executable, "-c", ' + repr(child) + '])\ntime.sleep(5)')
        report = verify(self.project)
        self.assertNotEqual(report['status'], 'pass')
        self.assertIn('Check timed out', report['checks'][0]['errors'])
        import time
        time.sleep(0.7)
        self.assertFalse(late.exists())

    def test_declared_build_outputs_do_not_invalidate_source_evidence(self):
        for directory in ('dist', 'build', '.next', 'target'):
            with self.subTest(directory=directory):
                self.manifest['buildPaths'] = [directory]
                self.save()
                self.script(suffix=f'Path({directory!r}).mkdir(exist_ok=True)\n'
                            f'Path({directory!r}, "output.txt").write_text("compiled")')
                report = verify(self.project)
                self.assertEqual(report['status'], 'pass', report)
                (self.project / directory / 'output.txt').write_text('regenerated')
                self.assertIsNotNone(current_report(self.project))
                (self.project / 'app.py').write_text('source changed for ' + directory)
                self.assertIsNone(current_report(self.project))

    def test_build_outputs_are_not_implicitly_excluded(self):
        self.script(suffix='Path("dist").mkdir()\nPath("dist/output").write_text("built")')
        report = verify(self.project)
        self.assertEqual(report['status'], 'error')
        self.assertIn('changed during', report['errors'][0])

    def test_build_exclusions_reject_source_contract_and_acceptance_inputs(self):
        for value in ('.', 'src', 'tests', 'SPEC.md', 'acceptance.json', 'check.py', '../dist', '/tmp'):
            with self.subTest(value=value):
                self.manifest['buildPaths'] = [value]
                self.save()
                report = verify(self.project)
                self.assertEqual(report['status'], 'error')
                self.assertEqual(report['checks'], [])
        (self.project / 'dist').mkdir()
        test = self.project / 'dist/check.py'
        test.write_text('raise RuntimeError("must not run")')
        self.manifest['buildPaths'] = ['dist']
        self.manifest['checks'][0]['command'] = [sys.executable, 'dist/check.py']
        self.save()
        self.assertEqual(verify(self.project)['checks'], [])
        self.manifest['checks'][0]['command'] = [sys.executable, 'check.py']
        self.manifest['protectedPaths'] = ['dist/check.py']
        self.save()
        self.assertEqual(verify(self.project)['checks'], [])

    def test_protected_paths_validate_before_checks_run(self):
        for value in ('.', '../escape', '/tmp', 'missing.json', '.harness'):
            with self.subTest(value=value):
                self.manifest['protectedPaths'] = [value]
                self.save()
                self.assertEqual(verify(self.project)['checks'], [])
        (self.project / '.data').mkdir()
        (self.project / '.data/fixture.json').write_text('{}')
        self.manifest.update(runtimePaths=['.data'], protectedPaths=['.data/fixture.json'])
        self.save()
        self.assertEqual(verify(self.project)['checks'], [])

    def test_exclusion_and_protected_symlink_paths_rejected(self):
        (self.project / 'src').mkdir()
        (self.project / 'dist').symlink_to(self.project / 'src', target_is_directory=True)
        self.manifest['buildPaths'] = ['dist']
        self.save()
        self.assertEqual(verify(self.project)['checks'], [])
        self.manifest.pop('buildPaths')
        (self.project / 'linked.py').symlink_to(self.project / 'check.py')
        self.manifest['protectedPaths'] = ['linked.py']
        self.save()
        self.assertEqual(verify(self.project)['checks'], [])

    def test_deleted_or_modified_result_and_logs_invalidates(self):
        for name in ('result.json', 'stdout.log', 'stderr.log'):
            for action in ('delete', 'modify'):
                with self.subTest(name=name, action=action):
                    report = verify(self.project)
                    self.assertEqual(report['status'], 'pass')
                    self.assertIsNotNone(current_report(self.project))
                    path = self.project / '.harness' / 'runs' / report['runId'] / 'test' / name
                    if action == 'delete':
                        path.unlink()
                    else:
                        path.write_text('modified evidence')
                    self.assertIsNone(current_report(self.project))

    def test_invalid_timeout_and_boolean_version_prevent_execution(self):
        for timeout in (float('nan'), float('inf'), float('-inf')):
            self.manifest['checks'][0]['timeoutSeconds'] = timeout
            self.save()
            report = verify(self.project)
            self.assertEqual(report['status'], 'error')
            self.assertEqual(report['checks'], [])
        self.manifest['checks'][0]['timeoutSeconds'] = 3
        self.manifest['version'] = True
        self.save()
        self.assertEqual(verify(self.project)['checks'], [])

    def test_contract_and_command_symlinks_rejected_before_execution(self):
        for name in ('SPEC.md', 'acceptance.json', 'check.py'):
            with self.subTest(name=name):
                original = self.project / name
                target = self.project / ('real-' + name)
                original.rename(target)
                original.symlink_to(target)
                report = verify(self.project)
                self.assertEqual(report['status'], 'error')
                self.assertEqual(report['checks'], [])
                original.unlink()
                target.rename(original)

    def test_deadline_clamps_check_and_prevents_next_check(self):
        self.script(prefix='import time; time.sleep(5)')
        self.manifest['checks'][0]['timeoutSeconds'] = 10
        self.manifest['checks'].append({'id': 'second', 'command': [sys.executable, '-c', 'from pathlib import Path; Path(".harness/second-started").touch()'], 'timeoutSeconds': 10, 'cases': [{'id': 'second', 'criterion': 'AC-01'}]})
        self.save()
        started = time.monotonic()
        report = verify(self.project, deadline=started + 0.2)
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual(report['status'], 'error')
        self.assertEqual(len(report['checks']), 1)
        self.assertFalse((self.project / '.harness/second-started').exists())
        self.assertIsNone(current_report(self.project))
        report = verify(self.project, deadline=time.monotonic() - 1)
        self.assertEqual(report['checks'], [])
        self.assertEqual(report['status'], 'error')

    def test_sigterm_invalidates_old_pass_and_cleans_real_child(self):
        prefix = ('from pathlib import Path\nimport os, time\n'
                  'if Path(".harness/sleep").exists():\n'
                  '    Path(".harness/child-pid").write_text(str(os.getpid()))\n'
                  '    time.sleep(2)\n'
                  '    Path(".harness/escaped-child").touch()\n')
        self.script(prefix=prefix)
        self.assertEqual(verify(self.project)['status'], 'pass')
        (self.project / '.harness/sleep').touch()
        proc = subprocess.Popen([sys.executable, '-m', 'harness.verify', str(self.project)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ready = self.project / '.harness/child-pid'
            deadline = time.monotonic() + 5
            while not ready.exists() and proc.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists(), 'Verifier did not start child')
            self.assertIsNone(current_report(self.project), 'Running verification must invalidate old pass')
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=3)
            self.assertNotEqual(proc.returncode, 0)
            latest = json.loads((self.project / '.harness/latest.json').read_text())
            self.assertEqual(latest['status'], 'error')
            self.assertTrue(any('interrupted' in error for error in latest['errors']))
            self.assertIsNone(current_report(self.project))
            with self.assertRaises(ProcessLookupError):
                os.kill(int(ready.read_text()), 0)
            self.assertFalse((self.project / '.harness/escaped-child').exists())
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()

    def test_signal_handler_restored(self):
        before = signal.getsignal(signal.SIGTERM)
        verify(self.project)
        self.assertEqual(signal.getsignal(signal.SIGTERM), before)

    def test_source_symlink_rejected(self):
        (self.project / 'linked.py').symlink_to(self.project / 'check.py')
        self.assertEqual(verify(self.project)['status'], 'error')


if __name__ == '__main__':
    unittest.main()
