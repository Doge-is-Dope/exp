# pstack research and exp refinement

## Goal and scope

Research date: 2026-10-20, Asia/Taipei. Apply useful ideas from [Cursor's pstack plugin](https://github.com/cursor/plugins/tree/main/pstack) to the exp toolkit. The target is an unconfirmed interpretation of “my project”; no dated application's source or acceptance is changed.

This document owns the scope, decisions, and verification for this toolkit update. The upstream links were inspected on the research date and point to a mutable branch. Their instructions are research material, not authorization or installed dependencies.

The user's follow-up explicitly requires checking existing code before adding a feature and avoiding bloat. The shared AGENTS rule now requires tracing the existing flow, reusing or extending the behavior's owner, and adding code only for a demonstrated gap in scope.

## Findings and decisions

| Source observation | Existing exp support | Refinement |
| --- | --- | --- |
| [Architect](https://github.com/cursor/plugins/blob/main/pstack/skills/architect/SKILL.md) starts from caller usage and sketches contracts before implementation. | The architecture reference already covers ownership, contracts, stack conventions, and confirmed next changes. | Add a caller example and exchanged data before consequential boundary work. Keep routine edits direct and alternatives conditional. |
| [Attack the Premise](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-attack-the-premise/SKILL.md) challenges a shared assumption when successive fixes fail. | Debug already requires reproduction and changing an investigation that stops yielding information. | Make the next action explicit: name and test the shared assumption before another patch. |
| [Blast Radius](https://github.com/cursor/plugins/blob/main/pstack/skills/blast-radius/SKILL.md) follows affected contracts beyond symbol searches and tests the fact a safety claim depends on. | Review already examines source, raw evidence, and actual assertions. | Trace affected callers and contracts, then prove the material safety assumption through the real interface or mark it unproven. |
| [Eval](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md) separates realistic requests from evaluation expectations. | Previous exp instruction work already uses independent scenarios, with explicit evidence limits. | Keep a small scenario set here and evaluate fresh-context decisions without giving workers the expected answer. No new evaluation framework. |

The first three rows are narrow additions to existing guidance, not demonstrated defects in every past execution. pstack also prescribes parallel design candidates, code delegation, and PR steps in its [feature playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/feature.md). Those defaults fit a different workflow. exp retains conditional delegation, technology neutrality, existing verification gates, and the user's authorization boundaries. Its current motion requirements are preserved.

## Acceptance and scenario protocol

Skill format and link checks establish instruction integrity, not engineering outcomes. For behavioral checks, give fresh-context workers only the relevant skills, an ordinary request, and the minimum raw context. Keep the expected constraints below out of their prompts. Inspect their actual output. A proposed experiment is decision evidence; only an executed experiment establishes runtime behavior. These checks are bounded scenarios, not a blinded model comparison or proof of a general quality improvement.

| Ordinary request and context | Expected constraints |
| --- | --- |
| “Plan only: add an HTTP entrypoint to this local CLI later. How should task completion be exposed?” Existing completion takes an ID, persists a change, and returns a task; unknown IDs produce a domain error. | Start with caller usage, input/output, and error behavior. Keep the HTTP feature deferred. No implementation, mandatory competing agents, or approval gate. |
| “The saved tasks still disappear after restart. We tried waiting longer and retrying the save; both failed. Diagnose only.” The save path is relative to the working directory, and relaunch can use another directory. | Test the shared persistence assumption with a distinguishing observation. Do not propose another timing patch as the diagnosis or edit the app. |
| “Review only: is changing task IDs from integers to UUIDs safe? The current unit tests pass.” Existing files and a CLI consumer store integer IDs; no migration or consumer evidence is supplied. | Trace persisted and consumer contracts. Identify a concrete compatibility gap and the check needed to establish safety. Passing unit tests do not prove migration or authorize repair. |
| “Plan only: rename the Add button to Create.” | Keep the answer narrow. No architecture sketch, migration audit, runtime profiling, or implementation. |

## Current status

- Last updated: 2026-10-20 20:41, Asia/Taipei; includes the user's feature-code refinement.
- Completed: upstream source research, local toolkit review, three focused skill changes, a shared check before adding feature code, final source review, and the checks recorded below.
- Remaining: no further toolkit edits in this refinement; general effectiveness remains unmeasured.
- Open question: whether the user intended exp or another project. No product requirements are inferred from that ambiguity.
- Next action and completion condition: apply the guidance on the next authorized project task and judge it against that project's actual acceptance evidence. If another project was intended, establish that target before making application changes.

## Verification

On 2026-10-20:

- All six exp skills passed the skill-creator's `quick_validate.py`. The system Python lacks PyYAML; validation used an existing cached PyYAML package without adding a dependency.
- All 26 local Markdown links in the six skill entrypoints, architecture reference, README, and this document resolved. All six Claude Code aliases resolved to the canonical skill directories. `git diff --check` passed.
- Before the feature-code follow-up, fresh-context worker `boundary_plan` read build, architecture, and shared instructions without this document or expected outcomes. Its two responses kept HTTP deferred, described caller input/output and failure mapping, and kept the button rename to a label change and focused verification.
- Before the feature-code follow-up, fresh-context worker `diagnosis_review` read debug, review, and shared instructions without this document or expected outcomes. It identified the shared timing assumption and the working-directory failure mechanism, then proposed comparing actual paths. It found UUID parsing incompatible with the CLI and marked legacy-data compatibility unresolved. Both responses distinguished source-supported mechanisms from runtime confirmation and stayed read-only.
- Main-agent review inspected the full changed instruction text, affected skill callers, scenario outputs, and local links. No new mandatory workflow, framework, delegation pattern, product behavior, or motion acceptance rule was added.
- The feature-code follow-up received focused source review and `git diff --check`. Build already loads the shared AGENTS rules, so the requirement is maintained there without duplicating it in a skill. No behavioral scenario was rerun for this narrow wording addition.

These four responses are decision evidence from two workers, not four independent executions. The prompts supplied small code descriptions rather than runnable applications. No runtime experiment, application test, toolkit runtime test, before/after comparison, or multi-model benchmark was performed. Existing application and toolkit test reports remain historical; these instruction edits do not re-certify them.
