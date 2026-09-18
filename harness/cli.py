#!/usr/bin/env python3
"""CLI entrypoint; run with python3 /path/to/exp/harness/cli.py."""
from pathlib import Path
import argparse
import json
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness.verify import verify, VerificationError
from harness.controller import hook, run, set_state, status, project_lock


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify and close a local MVP delivery loop")
    parser.add_argument("command", choices=["verify", "status", "run", "pause", "resume", "hook"])
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--agent-timeout", type=float, default=300)
    parser.add_argument("--budget-seconds", type=float, default=1200)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--reason", default="")
    parser.add_argument("--phase", choices=["waiting_input", "blocked", "paused_incomplete"], default="waiting_input")
    args = parser.parse_args(argv)
    project = args.project.resolve()
    try:
        if not (project / ".exp-project.json").is_file():
            raise VerificationError("Project must contain .exp-project.json")
        if args.command == "verify":
            with project_lock(project):
                value = verify(project)
            code = 0 if value["status"] == "pass" else 1
        elif args.command == "run":
            value = run(project, args.max_attempts, args.agent_timeout, args.budget_seconds, args.codex)
            code = 0 if value["phase"] == "complete" else 1
        elif args.command == "status":
            value = status(project)
            code = 0 if value["fresh"] and value["verificationStatus"] == "pass" else 1
        elif args.command == "hook":
            event = json.load(sys.stdin)
            # Never recursively intercept the subprocess coding worker.
            if os.environ.get("EXP_HARNESS_WORKER") == "1" or event.get("hook_event_name", "Stop") != "Stop":
                value = {}
            else:
                with project_lock(project):
                    value = hook(project, event)
            code = 0
        else:
            if args.command == "pause" and not args.reason.strip():
                raise VerificationError("pause requires a concrete --reason")
            with project_lock(project):
                value = set_state(project, "working" if args.command == "resume" else args.phase,
                                  reason=args.reason, hookContinuations=0, maxHookContinuations=args.max_attempts)
            code = 0
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return code
    except (OSError, ValueError) as exc:
        if args.command == "hook":
            print(json.dumps({"decision": "block", "reason": f"Harness gate error; do not claim completion: {exc}"}))
            return 0
        print(json.dumps({"status": "error", "message": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
