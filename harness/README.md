# exp harness

Optional acceptance verification and bounded repair for MVP projects. Native tests are the default; use the harness when requested or already established. Repair broken contracts rather than bypassing them.

Requires Python 3.10+ on macOS/Linux; no Python packages needed. Run commands from any directory using absolute paths.

## Trust model

Run the harness only on projects you trust. `verify` executes the commands registered in the project's `acceptance.json` with your user permissions and environment, like running that project's test script. `run` additionally passes check output to a Codex CLI process that can write inside the project. See [SECURITY.md](../SECURITY.md).

## Commands

```sh
python3 /path/to/exp/harness/cli.py verify --project /path/to/project
python3 /path/to/exp/harness/cli.py status --project /path/to/project
python3 /path/to/exp/harness/cli.py run --project /path/to/project --max-attempts 3 --agent-timeout 300 --budget-seconds 1200
```

| Command | Behavior |
| --- | --- |
| `verify` | Run registered checks and save evidence. Exit 0 means all checks passed. |
| `status` | Exit 0 only for a fresh passing report. `controllerPhase` separately reports repair state; `phase` can become `incomplete` when a completed controller loses passing evidence. |
| `run` | Verify, call an authenticated Codex CLI on failure, then recheck. Exit 0 means completed acceptance. Uses the existing model/configuration and workspace-write sandbox. |

Use `run` for requested repairs against fixed acceptance. Attempt, per-agent and total-time limits bound execution; time limits must be finite positive numbers, and cleanup may take slightly longer. No progress after rechecking, exhausted limits, missing input or external blockers stop incomplete. Changed acceptance inputs cause `needs_review`. Review those changes before starting another run. Interruption stops child processes without restarting them. Avoid repeating identical checks without a new change or verification need.

## Register checks

Projects need `.exp-project.json` from the workbench scaffold. Define unique criteria in `SPEC.md`:

```markdown
- **AC-01**: Added tasks survive reopening the application.
```

Map every criterion to executable cases in `acceptance.json`:

```json
{
  "version": 1,
  "checks": [{
    "id": "acceptance",
    "command": ["python3", "tests/acceptance.py"],
    "timeoutSeconds": 60,
    "cases": [{"id": "reopen", "criterion": "AC-01"}],
    "artifacts": ["reopen.json"]
  }]
}
```

Tests run inside the project. Write results to the supplied absolute `EXP_RESULT_PATH` and declared artifacts under `EXP_ARTIFACT_DIR`:

```json
{"cases": [{"id": "reopen", "criterion": "AC-01", "status": "pass", "message": "Task returned after server restart"}]}
```

Each registered case must appear exactly once with matching IDs and criterion, after executing its assertion. All must pass with exit code 0. Missing, malformed, skipped, failed or timed-out checks, and missing/empty artifacts prevent success. stdout/stderr are saved. Existing suites need a reporter or adapter for this format; registration does not generate tests. Browser checks should exercise behavior and assert outcomes.

Optional manifest fields:

| Field | Purpose |
| --- | --- |
| `runtimePaths` | Exclude generated data under `.data`, `.cache`, `test-results`, `playwright-report` or `coverage`. |
| `buildPaths` | Exclude declared rebuildable output under `dist`, `build`, `.next` or `target`. |
| `protectedPaths` | Protect existing acceptance configs, fixtures and indirect helpers during repair. |

SPEC, manifest, `tests/` and existing project files passed directly as command arguments are automatically protected. Declare indirect inputs explicitly; dependency graphs are not inferred. Edits, deletion, added directory contents and symlink replacements trigger review. Exclusions cannot overlap acceptance inputs or hide authored source; contract paths cannot traverse symlinks.

## Evidence

Reports are stored in `.harness/runs/<runId>/report.json` and `.harness/latest.json`. Fingerprints cover project files (including untracked files and lockfiles), environment and verifier. `.harness`, `.git`, `node_modules`, `.venv`, `__pycache__` and declared outputs are excluded. Install dependencies reproducibly from lockfiles.

Complete the agent's code review using [AGENTS.md](../AGENTS.md) and finish source and documentation updates before final `verify`, then share the report without editing fingerprinted files. The harness executes registered checks; a passing report does not replace code review. Later edits or environment changes require re-verification to claim current acceptance. Documentation-only changes may use focused checks without claiming old app evidence is current.

Review whether tests actually cover requirements. Local evidence and protected-input checks are not tamper-proof or filesystem write isolation; stronger guarantees require separate CI or restricted processes.

## Optional Stop hook

The controller works without hooks. To use a Stop gate, configure absolute paths in the host's trusted hook settings; this repository does not install or trust it automatically:

```json
{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"python3 /absolute/exp/harness/cli.py hook --project /absolute/project","timeout":30}]}]}}
```

```sh
python3 /path/to/exp/harness/cli.py resume --project /path/to/project
python3 /path/to/exp/harness/cli.py pause --project /path/to/project --phase waiting_input --reason "Need a user decision"
```

`resume` activates the gate without launching an agent. It continues active incomplete work up to its limit; paused or cancelled work can stop. Repair children set `EXP_HARNESS_WORKER=1` to avoid recursive interception. Verify actual host invocation before claiming integration.

## Test the toolkit

From the workbench root:

```sh
python3 -m unittest discover -s tests -v
python3 -B .agents/skills/exp-reset/scripts/test_reset.py
```

Controller tests use repair doubles; they do not establish live-model repair or host-hook integration.
