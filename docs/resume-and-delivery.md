# Resume and delivery — 2026-09-19

## Goal and accepted scope

Improve cold-start project resumption and concise delivery using the existing specification, native tests, and optional harness. Keep shared rules in AGENTS.md and adapt existing project documents in place. Do not add a controller, per-turn log, automatic Git delivery, or new harness fields.

The specification records current completed and remaining work, material decisions, open questions, evidence references, and the next action with its completion condition. Historical results must be reconciled with current files. Read-only work leaves project records unchanged. Finish fingerprinted documentation before final harness verification; deliver its final result through the report and response.

## Acceptance

- A new session can identify remaining work and preserve confirmed decisions from project files.
- Historical passing results do not establish current acceptance.
- Unanswered material questions do not become approval; independent authorized work can continue.
- Read-only review and handoff do not update project records.
- Final harness delivery leaves a fresh report without a subsequent SPEC edit.
- Skills remain discoverable and linked; Claude Code uses the same skill sources.

## Comparison protocol

After instruction validation, freeze the updated exp files and AgentFlow v8.2.0 at `fcb6878be0b2316cdba5a111f040655f161bfe03`. Give two independent, fresh-context subagents identical Python CLI source, decisions, stale historical evidence, task, permissions, and a 20-minute limit. Each gets its assigned workflow. AgentFlow uses fast-lane; neither may delegate, push, or write to external services. Local commits in disposable repositories are allowed for either route.

The task is to resume from files, repair durable task completion and unknown-ID handling, preserve the JSON contract, leave a pending CSV proposal unimplemented, verify behavior, and leave a usable handoff. Main-agent checks are held outside worker repositories, frozen before dispatch, and execute independently after both finish. This is workflow separation, not a filesystem security boundary.

Record correctness, decision preservation, evidence honesty, handoff completeness, elapsed time, interventions, and tokens only when available. Preserve first-round outputs if repairs are needed. A single run per workflow is a case study, not a statistical benchmark or a before/after proof of exp's improvement. The benchmark starts from prepared files; it does not exercise a real earlier conversation, automated compaction, or long-term recovery.

## Current status

Last updated: 2026-09-19. Implementation and first-round verification complete. No remaining authorized changes or open decisions. Use the Resume prompt on an existing project; inspect its current files and evidence before continuing work. No exp runtime or application source was changed, and no new dependencies were introduced.

## Verification results

- All six skills passed the official format validator. System and bundled Python initially lacked PyYAML; the validator then ran using an existing cached PyYAML package without installing a project dependency. All 22 checked local links resolved, all six Claude Code symlinks resolved to the same skill sources, and `git diff --check` passed.
- The existing toolkit suite passed 43 tests. These test the toolkit, not model performance.
- A disposable harness fixture passed verification and remained fresh after read-only report delivery. A subsequent SPEC edit correctly invalidated it. The fixture cleaned itself up. No harness implementation changes were needed.
- After freezing its comparison output, the exp agent performed a separate read-only review/handoff of the original fixture. It identified the two static defects, rejected synthetic historical evidence, left CSV unconfirmed, and did not run writing tests. The main agent compared file hashes before and after: no file changed. This follow-up reused the agent context; it was not a second fresh-context comparison.

Detailed local validation: [instruction checks](../2026-09-19-workflow-comparison/evidence/instruction-validation.json), [toolkit tests](../2026-09-19-workflow-comparison/evidence/exp-toolkit-tests.txt), [harness ordering](../2026-09-19-workflow-comparison/evidence/harness-delivery.json), [read-only check](../2026-09-19-workflow-comparison/evidence/readonly-validation.json).

## First-round comparison results

Both workers reproduced the failing baseline, repaired the same two production behaviors, preserved the JSON/CLI decisions, left CSV export unimplemented, and delivered startup instructions plus a usable specification handoff. Their recorded application test outputs and final diffs were inspected by the main agent.

The main agent then ran the seven frozen external checks against each output. Both passed durable completion, repeat completion, preservation of existing tasks, unknown-ID byte preservation, missing-store noncreation, add/list/ID behavior, empty-title rejection, and the absence of an export command (some checks cover multiple assertions). The original historical evidence remained unchanged.

| Observed result | exp | AgentFlow fast-lane |
| --- | --- | --- |
| Independent acceptance | 7/7 passed | 7/7 passed |
| Worker native tests | 6 passed | 6 passed |
| Worker fresh source-copy verification | Passed | Passed |
| Additional terminal evidence | Separate-process CLI smoke | Reusable real PTY journey |
| Human intervention during worker execution | None | None |
| Worker-recorded elapsed time | 2m01s | 5m59s |
| Token usage | Unavailable | Unavailable |
| Local Git delivery | Not requested or performed | Implementation and workflow closeout commits |

Worker times were 04:29:53–04:31:54 UTC for exp and 04:29:37–04:35:36 UTC for AgentFlow. They exclude main-agent setup, independent acceptance, and the read-only follow-up. Both dispatches inherited the same host model/reasoning configuration without overrides; independent model/token telemetry was not available.

AgentFlow's additional elapsed time included first-use hook setup, a repaired macOS PTY test, tracker proof/commit corrections, and a failed closeout followed by recovery. Our assignment combined `godev fast-lane` on one line; its parser expects `fast-lane` at the start of a line. The worker preserved the request and explicitly normalized the existing waiver before closeout succeeded. This invocation-specific problem is partly a fixture setup limitation, not proof of a general AgentFlow defect or intrinsic performance disadvantage.

Both workers initially ran the supplied baseline tests using their pre-existing OS temporary-directory behavior, despite the project-only write constraint. Both cleaned those temporary directories and corrected subsequent tests to project-local temporary storage. The benchmark should start with project-local temporary fixtures in any future round. No external service, extra agent, model CLI, or remote push was used by either worker.

For this small repair, both workflows achieved the same independently checked behavior and handoff. exp completed with less workflow machinery; AgentFlow provided additional PTY and Git/protocol evidence. These observations do not establish a general speed advantage, cost advantage, better product quality, long-term recovery quality, or an improvement over pre-change exp. A corrected invocation and repeated tasks would be needed for a stronger performance comparison. No exp correction or comparison rerun was needed after the first-round acceptance.

## Evidence and reproduction

The local [comparison project](../2026-09-19-workflow-comparison/README.md) retains the initial fixture, frozen evaluator, workflow snapshots, version hashes, shared owner request, first-round output snapshots, agent completion reports, and command output. Like other dated projects, it is excluded from Git; these links are available in this checkout and are not a claim that the raw evidence is distributed with the repository.

- [Comparison summary and limitations](../2026-09-19-workflow-comparison/evidence/comparison-summary.json)
- [exp independent checks](../2026-09-19-workflow-comparison/evidence/exp-external-tests.txt) and [AgentFlow independent checks](../2026-09-19-workflow-comparison/evidence/agentflow-external-tests.txt)
- [exp handoff](../2026-09-19-workflow-comparison/evidence/exp-first-round/SPEC.md) and [AgentFlow handoff](../2026-09-19-workflow-comparison/evidence/agentflow-first-round/.agentflow/devlog.md)

From the dated comparison directory, rerun the deterministic external checks with `python3 evaluator/check.py exp/2026-09-19-local-tasks` or `python3 evaluator/check.py agentflow/2026-09-19-local-tasks`. Python standard library only; each check cleans up its disposable stores and waits for its subprocesses. These commands recheck the saved outputs; they do not repeat the live-agent experiment.
