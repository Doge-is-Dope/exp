import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from harness.controller import codex_agent, hook, project_lock, read_state, run, set_state, status
from harness.verify import VerificationError, verify


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name)
        (self.p / '.exp-project.json').write_text('{"kind":"exp-project","version":1}')
        (self.p / 'SPEC.md').write_text('- **AC-01**: Stored value is correct.\n')
        (self.p / 'app.txt').write_text('wrong')
        (self.p / 'tests').mkdir()
        (self.p / 'tests/check.py').write_text('''import json,os
from pathlib import Path
ok=Path("app.txt").read_text()=="correct"
Path(os.environ["EXP_RESULT_PATH"]).write_text(json.dumps({"cases":[{"id":"value","criterion":"AC-01","status":"pass" if ok else "fail"}]}))
raise SystemExit(0 if ok else 1)
''')
        (self.p / 'acceptance.json').write_text(json.dumps({'version':1,'checks':[{'id':'value','command':[sys.executable,'tests/check.py'],'timeoutSeconds':5,'cases':[{'id':'value','criterion':'AC-01'}]}]}))

    def test_actual_failure_repair_recheck(self):
        calls=[]
        def repair(project, report, output, timeout):
            self.assertEqual(report['status'],'fail')
            calls.append(report['runId'])
            (project/'app.txt').write_text('correct')
            return {'status':'repaired','message':'Fixed'}
        result=run(self.p,agent=repair)
        self.assertEqual(result['phase'],'complete')
        self.assertEqual(len(calls),1)
        history=json.loads((self.p/'.harness/controller'/result['controllerRunId']/'result.json').read_text())['history']
        self.assertEqual([x['status'] for x in history if x['event']=='verification'],['fail','pass'])
        self.assertTrue(status(self.p)['fresh'])

    def test_agent_success_text_cannot_complete(self):
        calls=[]
        def noop(*args):
            calls.append(1)
            return {'status':'repaired','message':'Everything passes'}
        result=run(self.p,agent=noop)
        self.assertEqual(result['phase'],'paused_incomplete')
        self.assertIn('No source progress',result['reason'])
        self.assertEqual(len(calls),1)

    def test_budget_zero_attempts_never_calls_agent(self):
        result=run(self.p,max_attempts=0,agent=lambda *a:self.fail('agent must not run'))
        self.assertEqual(result['phase'],'paused_incomplete')

    def test_invalid_time_limits_rejected_without_side_effects(self):
        for name in ('agent_timeout', 'budget_seconds'):
            for value in (float('nan'), float('inf'), float('-inf'), 0, -1):
                with self.subTest(name=name, value=value):
                    agent = Mock()
                    with patch('harness.controller.subprocess.Popen') as launch:
                        with self.assertRaisesRegex(VerificationError, 'finite and positive'):
                            run(self.p, agent=agent, **{name: value})
                    agent.assert_not_called()
                    launch.assert_not_called()
                    self.assertFalse((self.p / '.harness').exists())

    def test_finite_positive_time_limits_allow_repair(self):
        def repair(project, report, output, timeout):
            self.assertEqual(timeout, 0.5)
            (project / 'app.txt').write_text('correct')
            return {'status': 'repaired', 'message': 'Fixed'}
        result = run(self.p, agent_timeout=0.5, budget_seconds=5.5, agent=repair)
        self.assertEqual(result['phase'], 'complete')
        self.assertEqual(result['attempts'], 1)

    def test_wall_clock_budget_bounds_verification(self):
        import time
        script=self.p/'tests/check.py'
        script.write_text('import time\ntime.sleep(5)\n'+script.read_text())
        started=time.monotonic()
        result=run(self.p,budget_seconds=0.15,agent=lambda *a:self.fail('agent must not run'))
        self.assertEqual(result['phase'],'paused_incomplete')
        self.assertLess(time.monotonic()-started,2)

    def test_wait_and_external_block_preserve_incomplete(self):
        for output,phase in [('needs_input','waiting_input'),('blocked','blocked'),('error','blocked')]:
            with self.subTest(output=output):
                result=run(self.p,agent=lambda *a:{'status':output,'message':'Concrete missing input'})
                self.assertEqual(result['phase'],phase)
                self.assertFalse(result['active'])
                self.assertEqual(hook(self.p,{}),{})

    def test_changed_checks_require_review_even_if_app_fixed(self):
        def tamper(project,*args):
            (project/'app.txt').write_text('correct')
            with (project/'tests/check.py').open('a') as f:f.write('\n# Changed acceptance\n')
            return {'status':'repaired','message':'done'}
        self.assertEqual(run(self.p,agent=tamper)['phase'],'needs_review')

    def test_interruption_does_not_restart(self):
        def interrupt(*args): raise KeyboardInterrupt()
        self.assertEqual(run(self.p,agent=interrupt)['phase'],'cancelled')
        self.assertFalse(read_state(self.p)['active'])

    def test_root_check_change_requires_review(self):
        (self.p / 'tests/check.py').rename(self.p / 'check.py')
        path = self.p / 'acceptance.json'
        manifest = json.loads(path.read_text())
        manifest['checks'][0]['command'] = [sys.executable, 'check.py']
        path.write_text(json.dumps(manifest))
        def tamper(project, *args):
            script = project / 'check.py'
            script.write_text(script.read_text().replace('=="correct"', '=="wrong"'))
            return {'status': 'repaired', 'message': 'Changed root check'}
        result = run(self.p, agent=tamper)
        self.assertEqual(result['phase'], 'needs_review')
        self.assertEqual((self.p / 'app.txt').read_text(), 'wrong')

    def test_declared_acceptance_inputs_protected_against_mutations(self):
        config = self.p / 'test-config.json'
        fixtures = self.p / 'fixtures'
        fixtures.mkdir()
        path = self.p / 'acceptance.json'
        manifest = json.loads(path.read_text())
        manifest['protectedPaths'] = ['test-config.json', 'fixtures']
        original = json.dumps(manifest)
        for action in ('edit', 'delete', 'add', 'symlink', 'unregister'):
            with self.subTest(action=action):
                if config.is_symlink():
                    config.unlink()
                config.write_text('{}')
                path.write_text(original)
                def tamper(project, *args):
                    if action == 'edit':
                        config.write_text('{"weakened":true}')
                    elif action == 'delete':
                        config.unlink()
                    elif action == 'add':
                        (fixtures / 'extra.json').write_text('[]')
                    elif action == 'symlink':
                        config.unlink()
                        config.symlink_to(project / 'app.txt')
                    else:
                        path.write_text('{"version":1}')
                    return {'status': 'repaired', 'message': 'Changed acceptance'}
                self.assertEqual(run(self.p, agent=tamper)['phase'], 'needs_review')

    def test_declared_inputs_allow_application_only_repair(self):
        (self.p / 'test-config.json').write_text('{}')
        path = self.p / 'acceptance.json'
        manifest = json.loads(path.read_text())
        manifest['protectedPaths'] = ['test-config.json']
        path.write_text(json.dumps(manifest))
        def repair(project, *args):
            (project / 'app.txt').write_text('correct')
            return {'status': 'repaired', 'message': 'Fixed application'}
        self.assertEqual(run(self.p, agent=repair)['phase'], 'complete')

    def test_stale_completed_state_is_not_success(self):
        (self.p/'app.txt').write_text('correct')
        self.assertEqual(run(self.p)['phase'],'complete')
        (self.p/'untracked.py').write_text('print(1)')
        self.assertEqual(status(self.p)['phase'],'incomplete')

    def test_hook_continues_then_stops_incomplete_at_limit(self):
        set_state(self.p,'working',maxHookContinuations=1)
        self.assertEqual(hook(self.p,{})['decision'],'block')
        self.assertNotIn('decision',hook(self.p,{}))
        self.assertEqual(read_state(self.p)['phase'],'paused_incomplete')

    def test_hook_command_quotes_shell_metacharacters(self):
        other=tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        project=Path(other.name).resolve()/'my project; echo x'
        shutil.copytree(self.p,project)
        set_state(project,'working')
        reason=hook(project,{})['reason']
        command=reason[reason.index('python3 '):reason.index('. Do not weaken')]
        self.assertEqual(shlex.split(command)[-2:],['--project',str(project)])

    def test_hook_passes_only_fresh_verification(self):
        (self.p/'app.txt').write_text('correct')
        verify(self.p)
        set_state(self.p,'working')
        self.assertEqual(hook(self.p,{}),{})
        self.assertEqual(read_state(self.p)['phase'],'complete')

    def test_lock_blocks_overlapping_controller(self):
        with project_lock(self.p):
            with self.assertRaises(VerificationError):
                with project_lock(self.p):pass

    def test_agent_timeout_kills_process_and_logs_exit(self):
        fake=self.p/'fake-codex'
        fake.write_text('#!'+sys.executable+'\nimport time\ntime.sleep(30)\n')
        fake.chmod(0o755)
        out=self.p/'.harness/agent-timeout'
        result=codex_agent(self.p,{},out,0.1,str(fake))
        self.assertEqual(result['status'],'error')
        pid=json.loads((out/'process.json').read_text())['pid']
        with self.assertRaises(ProcessLookupError):os.kill(pid,0)
        self.assertTrue((out/'exit.json').exists())


if __name__=='__main__':unittest.main()
