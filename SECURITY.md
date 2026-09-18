# Security

## Trust model

exp is a local development toolkit. It has no network service and no dependencies beyond the Python standard library. Its security boundary is the same as any local test runner.

- **`verify` runs project-defined commands.** Each check in a project's `acceptance.json` is executed as an argv list, without a shell, using your user permissions and full environment. Running the harness on a project is equivalent to running that project's test script. Review `acceptance.json` and the scripts it invokes before verifying a project you did not write.
- **`run` gives a coding agent write access to the project.** After a failed verification, the controller starts a Codex CLI process with the `workspace-write` sandbox and includes the verification report in its prompt. The report is marked as untrusted data, but check output can still influence the agent. Use `run` only with projects and test output you trust.
- **Protected-input checks detect changes; they do not prevent them.** The controller stops with `needs_review` when requirements or acceptance inputs change during repair. This is not filesystem isolation. Local evidence is not tamper-proof; use separate CI or restricted processes for stronger guarantees.
- **The Stop hook is opt-in.** This repository never installs or trusts a hook automatically.

## Evidence files

Reports under a project's `.harness/` record the Python executable path, platform details, check commands, and captured stdout/stderr. Environment variables are stored only as a SHA-256 hash, but anything your checks print is saved verbatim. The scaffold's `.gitignore` excludes `.harness/`; keep it excluded if you publish a project, and avoid printing secrets from checks.

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on this repository rather than opening a public issue. Include the affected command, a minimal reproduction, and the impact you observed.
