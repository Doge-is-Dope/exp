---
name: exp-debug
description: Diagnose and repair an MVP failure from a reproduction or execution evidence.
---

# exp debug

Follow [AGENTS.md](../../../AGENTS.md) for workspace conventions, code quality, and verification. Establish expected behavior and reproduce the failure when possible. For harness failures, inspect the report and raw outputs to distinguish application defects from missing evidence or environment errors.

Use evidence to discriminate between likely causes. If attempts stop producing new information, change the investigation strategy. Preserve useful evidence and unrelated changes.

Fix the cause within the requested scope, review the correction, and rerun the failing scenario and affected checks using the project's established verification workflow. For harness commands and incomplete states, consult [the contract](../../../harness/README.md) when needed. A diagnosis-only request ends before product edits.

Return the cause, correction, observed result, and remaining uncertainty or blocker. For implemented repairs, reconcile the existing specification's status and affected acceptance evidence using the shared work-boundary rules; diagnosis-only findings belong in the response unless document changes were requested.
