---
name: exp-review
description: Review an MVP against its requirements and execution evidence when an assessment is requested.
---

# exp review

Follow [AGENTS.md](../../../AGENTS.md) for workspace conventions, code quality, and verification. Establish the requirement source and review scope. Inspect implementation and raw evidence rather than relying on the author's summary. Judge architecture against the actual use case and constraints, and distinguish defects from preferences.

For harness-enabled projects, compare SPEC criteria, `acceptance.json`, and the actual assertions. Use `harness/cli.py status --project <project>` for freshness and `verify` when current execution is needed; consult [the contract](../../../harness/README.md) for details. A green report cannot establish behavior that its checks never exercise. For UI or motion review, use the applicable evidence criteria in [exp-design](../exp-design/SKILL.md); inspect intermediate-state coverage when required, not only settled values.

Run focused checks to resolve concrete uncertainty. If independent review is requested, use a fresh-context reviewer with the requirements and raw artifacts. Its agreement is not execution evidence. Review alone does not authorize product edits. If the user prohibits all file writes, use read-only inspection and report checks that could not run; harness verification writes evidence files.

Report actionable findings with location, trigger, impact, and evidence. Separate static findings, historical results, and current execution; state acceptance status and verification gaps. If no defect is found, say so without claiming none can exist.
