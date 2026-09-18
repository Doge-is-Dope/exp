"""Run registered acceptance checks and bind evidence to project contents."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import platform
import re
import signal
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone


class VerificationError(ValueError):
    pass


EXCLUDED = {'.harness', '.git', 'node_modules', '.venv', '__pycache__'}
RUNTIME_ROOTS = {'.data', '.cache', 'test-results', 'playwright-report', 'coverage'}
BUILD_ROOTS = {'dist', 'build', '.next', 'target'}


def _read(path):
    try:
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise VerificationError(f'Duplicate JSON key: {key}')
                result[key] = value
            return result
        return json.loads(path.read_text(), object_pairs_hook=unique_pairs)
    except (OSError, ValueError) as exc:
        raise VerificationError(f'Cannot read JSON {path}: {exc}') from exc


def _relative(value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or '..' in Path(value).parts:
        raise VerificationError(f'Invalid relative path: {value!r}')
    return Path(value)


def acceptance_paths(project, manifest):
    """Roots protected during repair; indirect inputs must be declared explicitly."""
    project = Path(project).resolve()
    paths = {Path('SPEC.md'), Path('acceptance.json'), Path('tests')}
    paths.update(_relative(value) for value in manifest.get('protectedPaths', []))
    for check in manifest['checks']:
        for arg in check['command']:
            candidate = (project / arg).resolve()
            if candidate.is_file() and candidate.is_relative_to(project):
                paths.add(candidate.relative_to(project))
    return sorted(paths)


def load_contract(project: Path) -> dict:
    project = Path(project).resolve()
    for name in ('SPEC.md', 'acceptance.json'):
        if (project / name).is_symlink():
            raise VerificationError(f'Contract file cannot be a symlink: {name}')
    manifest = _read(project / 'acceptance.json')
    try:
        spec = (project / 'SPEC.md').read_text()
    except OSError as exc:
        raise VerificationError(str(exc)) from exc
    criteria = re.findall(r'^\s*-\s+\*\*(AC-[\w-]+)\*\*:', spec, re.M)
    if not criteria or len(criteria) != len(set(criteria)):
        raise VerificationError('SPEC must contain unique AC criteria')
    if not isinstance(manifest, dict) or type(manifest.get('version')) is not int or manifest.get('version') != 1:
        raise VerificationError('Unsupported acceptance manifest')
    checks = manifest.get('checks')
    if not isinstance(checks, list) or not checks:
        raise VerificationError('At least one check is required')
    runtime = manifest.get('runtimePaths', [])
    if not isinstance(runtime, list):
        raise VerificationError('runtimePaths must be a list')
    for value in runtime:
        path = _relative(value)
        if not path.parts or path.parts[0] not in RUNTIME_ROOTS:
            raise VerificationError('runtimePaths may exclude only generated data/cache/test output')
    builds = manifest.get('buildPaths', [])
    if not isinstance(builds, list):
        raise VerificationError('buildPaths must be a list')
    for value in builds:
        path = _relative(value)
        if not path.parts or path.parts[0] not in BUILD_ROOTS:
            raise VerificationError('buildPaths may exclude only dist, build, .next or target output')
        if (project / path).exists() and not (project / path).is_dir():
            raise VerificationError('buildPaths must identify directories')
    protected = manifest.get('protectedPaths', [])
    if not isinstance(protected, list):
        raise VerificationError('protectedPaths must be a list')
    for value in protected:
        path = _relative(value)
        if not path.parts or any(part in EXCLUDED for part in path.parts):
            raise VerificationError('protectedPaths must identify fingerprinted project inputs')
        if not (project / path).exists():
            raise VerificationError(f'Missing protected input: {value}')
    seen, covered = set(), set()
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]+', check['id']) or check['id'] in seen:
            raise VerificationError('Checks require unique safe IDs')
        seen.add(check['id'])
        command = check.get('command')
        if not isinstance(command, list) or not command or any(not isinstance(v, str) or not v or '\x00' in v for v in command):
            raise VerificationError('command must be a nonempty argv list')
        timeout = check.get('timeoutSeconds')
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 3600:
            raise VerificationError('timeoutSeconds must be in (0, 3600]')
        cases = check.get('cases')
        if not isinstance(cases, list) or not cases:
            raise VerificationError('Each check requires cases')
        ids = set()
        for case in cases:
            if not isinstance(case, dict) or not isinstance(case.get('id'), str) or not case['id'] or case['id'] in ids or not isinstance(case.get('criterion'), str) or case.get('criterion') not in criteria:
                raise VerificationError('Invalid, duplicate, or unknown case registration')
            ids.add(case['id'])
            covered.add(case['criterion'])
        artifacts = check.get('artifacts', [])
        if not isinstance(artifacts, list):
            raise VerificationError('artifacts must be a list')
        for artifact in artifacts:
            _relative(artifact)
        # A runtime exclusion cannot hide a directly invoked project script.
        for arg in command:
            raw_candidate = project / arg
            if raw_candidate.is_relative_to(project):
                for component in (raw_candidate, *raw_candidate.parents):
                    if component == project:
                        break
                    if component.is_symlink():
                        raise VerificationError('Check command paths cannot traverse symlinks')
            candidate = raw_candidate.resolve()
            for value in runtime + builds:
                excluded = (project / value).resolve()
                if candidate == excluded or excluded in candidate.parents:
                    raise VerificationError('Output exclusions cannot hide check commands')
    if covered != set(criteria):
        raise VerificationError(f'Uncovered criteria: {sorted(set(criteria) - covered)}')
    protected_roots = acceptance_paths(project, manifest)
    for path in protected_roots + [Path(value) for value in runtime + builds]:
        for part in (path, *path.parents):
            if (project / part).is_symlink():
                raise VerificationError(f'Contract paths cannot traverse symlinks: {path}')
    for value in runtime + builds:
        excluded = Path(value)
        if any(excluded == path or excluded in path.parents or path in excluded.parents
               for path in protected_roots):
            raise VerificationError('Output exclusions cannot overlap acceptance inputs')
    return manifest


def fingerprint(project: Path) -> dict:
    project = Path(project).resolve()
    contract = load_contract(project)
    runtime = [Path(p) for p in contract.get('runtimePaths', []) + contract.get('buildPaths', [])]
    files = {}
    for root, dirs, names in os.walk(project, followlinks=False):
        base = Path(root)
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not any((base / d).relative_to(project) == p or p in (base / d).relative_to(project).parents for p in runtime))
        for name in sorted(names + [d for d in dirs if (base / d).is_symlink()]):
            path = base / name
            rel = path.relative_to(project)
            if any(rel == p or p in rel.parents for p in runtime):
                continue
            if path.is_symlink():
                raise VerificationError(f'Source symlink cannot be fingerprinted safely: {rel}')
            try:
                files[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as exc:
                raise VerificationError(str(exc)) from exc
    environment = {'python': sys.version, 'platform': platform.platform(), 'executable': sys.executable,
                   'environmentHash': hashlib.sha256(json.dumps(dict(os.environ), sort_keys=True).encode()).hexdigest()}
    payload = {'files': files, 'environment': environment, 'verifierHash': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    payload['digest'] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return payload


def _atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _kill(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait()


def verify(project: Path, deadline=None) -> dict:
    """Verify within an optional absolute monotonic deadline.

    Main-thread SIGTERM is translated to KeyboardInterrupt after cleanup and
    persisted invalidation, allowing controllers to retain cancelled state.
    """
    previous = None
    main_thread = threading.current_thread() is threading.main_thread()
    if main_thread:
        previous = signal.getsignal(signal.SIGTERM)
        def interrupted(signum, frame):
            raise KeyboardInterrupt('Verification interrupted by SIGTERM')
        signal.signal(signal.SIGTERM, interrupted)
    try:
        return _verify(project, deadline)
    finally:
        if main_thread:
            signal.signal(signal.SIGTERM, previous)


def _verify(project: Path, deadline=None) -> dict:
    project = Path(project).resolve()
    run_id = uuid.uuid4().hex
    root = project / '.harness' / 'runs' / run_id
    root.mkdir(parents=True)
    report = {'version': 1, 'runId': run_id, 'status': 'error', 'fingerprint': None, 'checks': [], 'errors': [], 'startedAt': _now()}
    _atomic(project / '.harness' / 'latest.json', report)
    interrupted = False
    try:
        if deadline is not None and (not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
            raise VerificationError('deadline must be a finite monotonic timestamp')
        contract = load_contract(project)
        before = fingerprint(project)
        report['fingerprint'] = before
        for check in contract['checks']:
            remaining = float('inf') if deadline is None else deadline - time.monotonic()
            if remaining <= 0:
                report['errors'].append('Verification deadline exhausted')
                break
            directory = root / check['id']
            artifacts = directory / 'artifacts'
            artifacts.mkdir(parents=True)
            result_path = directory / 'result.json'
            env = dict(os.environ, EXP_RESULT_PATH=str(result_path), EXP_ARTIFACT_DIR=str(artifacts))
            entry = {'id': check['id'], 'command': check['command'], 'status': 'error', 'exitCode': None, 'cases': [], 'errors': [], 'artifacts': [], 'logs': {}, 'evidence': []}
            report['checks'].append(entry)
            try:
                with (directory / 'stdout.log').open('wb') as stdout, (directory / 'stderr.log').open('wb') as stderr:
                    proc = subprocess.Popen(check['command'], cwd=project, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
                    try:
                        entry['exitCode'] = proc.wait(timeout=min(check['timeoutSeconds'], remaining))
                    except subprocess.TimeoutExpired:
                        entry['errors'].append('Check timed out')
                        if deadline is not None and time.monotonic() >= deadline:
                            report['errors'].append('Verification deadline exhausted')
                    finally:
                        _kill(proc)  # Also clean descendants after normal parent exit.
                entry['logs'] = {k: str((directory / (k + '.log')).relative_to(project)) for k in ('stdout', 'stderr')}
                if result_path.is_symlink():
                    raise VerificationError('Result file must not be a symlink')
                for path in (result_path, directory / 'stdout.log', directory / 'stderr.log'):
                    if path.is_symlink() or not path.is_file():
                        raise VerificationError(f'Missing or linked evidence: {path.name}')
                    entry['evidence'].append({'path': str(path.relative_to(project)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
                result = _read(result_path)
                cases = result.get('cases') if isinstance(result, dict) else None
                if not isinstance(cases, list) or len(cases) != len(check['cases']):
                    raise VerificationError('Result must contain exactly the registered cases')
                expected = {c['id']: c['criterion'] for c in check['cases']}
                actual = set()
                for case in cases:
                    if not isinstance(case, dict) or not isinstance(case.get('id'), str) or case['id'] in actual or case['id'] not in expected or case.get('criterion') != expected[case['id']] or case.get('status') not in ('pass', 'fail', 'skip', 'error'):
                        raise VerificationError('Malformed, duplicate, or unexpected result case')
                    actual.add(case['id'])
                entry['cases'] = cases
                for value in check.get('artifacts', []):
                    path = artifacts / value
                    if not path.resolve().is_relative_to(artifacts.resolve()) or not path.is_file() or path.stat().st_size == 0:
                        raise VerificationError(f'Missing, empty, or escaped artifact: {value}')
                    entry['artifacts'].append({'path': str(path.relative_to(project)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
                entry['status'] = 'pass' if entry['exitCode'] == 0 and not entry['errors'] and all(c['status'] == 'pass' for c in cases) else 'fail'
            except (OSError, VerificationError, TypeError) as exc:
                entry['errors'].append(str(exc))
        if deadline is not None and time.monotonic() >= deadline and 'Verification deadline exhausted' not in report['errors']:
            report['errors'].append('Verification deadline exhausted')
        if before != fingerprint(project):
            report['errors'].append('Project changed during verification; evidence is stale')
        report['status'] = 'error' if report['errors'] or any(c['status'] == 'error' for c in report['checks']) else ('pass' if all(c['status'] == 'pass' for c in report['checks']) else 'fail')
    except KeyboardInterrupt:
        interrupted = True
        report['status'] = 'error'
        report['errors'].append('Verification interrupted; incomplete')
    except (VerificationError, OSError) as exc:
        report['errors'].append(str(exc))
    report['finishedAt'] = _now()
    _atomic(root / 'report.json', report)
    _atomic(project / '.harness' / 'latest.json', report)
    if interrupted:
        raise KeyboardInterrupt('Verification interrupted; evidence invalidated')
    return report


def current_report(project: Path):
    project = Path(project).resolve()
    try:
        report = _read(project / '.harness' / 'latest.json')
        if not isinstance(report, dict) or report.get('version') != 1 or report.get('status') not in ('pass', 'fail') or report.get('fingerprint') != fingerprint(project):
            return None
        if not isinstance(report.get('runId'), str) or not re.fullmatch(r'[a-f0-9]{32}', report['runId']):
            return None
        persisted = _read(project / '.harness' / 'runs' / report['runId'] / 'report.json')
        if persisted != report:
            return None
        contract = load_contract(project)
        if len(report['checks']) != len(contract['checks']):
            return None
        for check, expected in zip(report['checks'], contract['checks']):
            if check['id'] != expected['id'] or len(check['artifacts']) != len(expected.get('artifacts', [])):
                return None
            if check['command'] != expected['command'] or len(check['cases']) != len(expected['cases']):
                return None
            registered = {c['id']: c['criterion'] for c in expected['cases']}
            seen = set()
            for case in check['cases']:
                if case['id'] in seen or registered.get(case['id']) != case['criterion'] or case['status'] not in ('pass', 'fail', 'skip', 'error'):
                    return None
                seen.add(case['id'])
            if report['status'] == 'pass' and (check['status'] != 'pass' or check['exitCode'] != 0 or check['errors'] or any(c['status'] != 'pass' for c in check['cases'])):
                return None
            required_evidence = {str(Path('.harness') / 'runs' / report['runId'] / check['id'] / name) for name in ('result.json', 'stdout.log', 'stderr.log')}
            if {e['path'] for e in check['evidence']} != required_evidence or len(check['evidence']) != 3:
                return None
            for artifact in check['artifacts'] + check['evidence']:
                path = project / _relative(artifact['path'])
                if path.is_symlink() or not path.resolve().is_relative_to(project / '.harness' / 'runs' / report['runId']) or hashlib.sha256(path.read_bytes()).hexdigest() != artifact['sha256']:
                    return None
        return report
    except (OSError, VerificationError, KeyError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    report = verify(args.project)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
