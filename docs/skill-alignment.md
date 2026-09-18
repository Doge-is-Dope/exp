# Skill alignment — 2026-09-18

## Goal and source

Align the exp workflow with [OpenAI's Astra skills and prompts guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra). Keep precise discovery, conditional detail, outcome-based instructions, clear authorization, and explicit completion. This is a toolkit change; it does not re-certify either expense MVP.

## Plan

1. Shorten exp-design discovery and separate conditional motion guidance from the main design workflow.
2. Preserve the user's design and motion acceptance requirements. Connect implementation and review to evidence for the actual requirements, including intermediate UI states rather than only final values.
3. Remove prompt duplication and contextualize costly verification. Preserve native-test defaults, existing harness contracts, dependency notification, and authorized autonomous repairs.
4. Validate skill structure and local links. Run independent realistic scope/acceptance scenarios and inspect the outputs. Record limitations rather than treating a format check as behavioral proof.

## Acceptance

- Small edits and screenshot-only reviews stay within scope without requiring an unrelated performance audit.
- Substantive motion work reads the motion reference, includes actual interaction and performance evidence, and cannot claim full acceptance when required evidence is missing.
- Harness success remains limited to registered assertions; missing intermediate-state coverage is an explicit gap.
- Authorization and verification rules remain consistent across AGENTS, skills, README, and prompts.
- No fixed framework, animation effect, FPS guarantee, or new quality scoring system is imposed.

## Verification

- Six exp skills passed `quick_validate.py`; 20 local Markdown links resolved; `git diff --check` passed.
- Independent scope check (`skill_forward_scope`, fresh context): a button-copy-only planning request stayed read-only, proposed focused verification, and did not require a motion audit. A screenshot-only motion review declined to claim smoothness and identified the missing interaction/profiling evidence. These are observed decision outputs, not executed product tests.
- Independent actual-evidence review (`skill_forward_motion`, fresh context): inspected the comparison MVP's source, tests, screenshots, and harness run `79fb548ac3614eaba83b5996dd6bdd4c`. Correctly distinguished 4 passing acceptance cases and 14 browser assertions from unverified motion quality. Identified settled-state-only browser checks, mocked motion geometry, missing profiling, and a reduced-motion cancellation claim without a matching cancellation assertion. No application edits or test reruns were performed; this validates review decisions, not application smoothness.

## Implemented decisions

- `exp-design` has a concise discovery description and a main workflow; motion design and acceptance live in a linked conditional reference. User-required measured motion acceptance is retained.
- Build maps completion to evidence; review explicitly inspects intermediate-state coverage for motion requirements. Automated pass is not promoted into a broader quality claim.
- Design returns to an active caller rather than recursively starting build again. Brainstorm HTML is optional in prompt examples. Shared rules authorize isolated local verification and repair within the requested scope.
- No product source, harness implementation, technology choice, external library, or numerical performance threshold was changed in this alignment task. Existing working-tree changes from prior tasks are preserved.

## Limits

This verifies instruction structure and bounded independent decisions. It does not demonstrate higher design quality across all future tasks, or establish either MVP's measured animation performance. Those remain application-level acceptance work.

## Re-verification and comparison

On 2026-09-18, reran all six skill format validators, resolved all 20 local Markdown links, and checked `git diff --check`; all passed. A new fresh-context reviewer (`recheck_skills`) read the current instructions without this report and found no contradictions across four scenarios: a narrow button rename, screenshot-only motion evidence, settled-state-only harness evidence, and introducing a useful external library. These are bounded decision checks, not an old/new model benchmark or an application performance test.

| Area | Earlier instruction or observed gap | Current instruction and recheck |
| --- | --- | --- |
| Motion acceptance | Existing MVP browser assertions primarily checked settled results | Review must inspect intermediate states and pair visual observation with profiling; reviewer correctly marked missing evidence incomplete |
| Small changes | General delivery requirements could be read too broadly | Copy-only edits receive proportionate checks without motion testing or a new approval gate |
| Evidence claims | A green report could be mistaken for broader quality proof in execution | Existing harness boundary is retained and explicitly connected to motion review; screenshot-only claims are rejected |
| Prompt scope | Committed brainstorm prompt always requested interactive HTML | HTML is conditional on usefulness or request |
| Dependencies | User requires advance notification | Shared rule remains notification with rationale and impact, without an extra approval gate |

No product source was changed or product tests rerun during this re-verification. The comparison documents instruction changes and observed reviewer decisions; it does not demonstrate that either MVP's appearance or animation changed.

## Design judgment update — 2026-09-18

Following the user's clarification about taste, `exp-design` now asks agents to explain the relationship between a design choice and the experience it creates, transfer principles rather than prescribed effects, treat inferred preferences as contextual hypotheses, and compare consequential alternatives under comparable conditions. The motion reference connects timing, distance, direction, and easing to attention, information continuity, and expected interaction frequency. Technical acceptance remains distinct from perceptual preference. No particular project's animation parameters became universal rules.

Validation: skill format passed, four local links resolved, and `git diff --check` passed. Fresh-context `taste_forward_check` read only the current instructions and three realistic requests, without this report or conversation history:

- A user liked slow dashboard motion but requested a high-frequency warehouse interface. The agent proposed immediate scan results and a restrained cue, considered no motion, and treated the cause of the dashboard preference as unconfirmed.
- Users preferred one transfer-confirmation transition; both alternatives passed performance checks, but only written descriptions were supplied. The agent selected the preferred option as a candidate while keeping rendered readability and motion acceptance unverified.
- A button-label-only change received focused checks without a motion audit or extra prototypes.

No instruction conflict was found in these scenarios. These are observed contextual decisions, not proof of superior generated visuals, model training, or a new MVP acceptance result. No application code was changed.
