# Motion design and acceptance

Use for new interactive interfaces, substantive motion work, or motion review. Preserve explicit user requirements and the project's established gates. Scale scenarios to the affected interactions; do not impose a full audit on unrelated edits.

## Design the transition

Inspect relevant live examples from [transitions.dev](https://transitions.dev/) or the user's reference. Observe the trigger, intermediate states, rhythm, easing, and response to interruption. If the source cannot be inspected, disclose that and describe the alternative design basis. A link alone is not evidence of reference review.

Evaluate the motion in its surrounding interface and at the expected interaction frequency. Compare how alternatives guide attention and preserve the relationship between old and new information, including whether movement should be noticeable at all. Tune duration, distance, direction, and easing together for that purpose; a preferred example does not establish universal values. When a user prefers an earlier result, investigate the experience it preserves before choosing whether to retain its mechanism or achieve that quality another way.

Describe the intended continuity in the existing specification: what changes, what remains still, and how another action retargets an unfinished transition. Choose effects for the information being conveyed, such as position continuity for reordered rows, coordinated resizing, or place-aligned digits for totals. These are options, not a required visual recipe. A generic fade on every update is not sufficient design reasoning.

Keep unchanged labels, units, punctuation, and unaffected content stable. For numeric transitions, show the true value without fictional count-up intermediates; expose one accurate accessible value and hide decorative copies. Consider digit-count and sign changes when relevant.

Repeated input must reach the newest state without snapping back to a fixed entrance pose, accumulating copies, stealing focus, delaying requests, or blocking controls. Preserve the currently displayed position/opacity when retargeting where continuity calls for it. Support immediate or subdued reduced-motion behavior, including a preference change during motion.

Use the platform's animation capabilities or a suitable library under the shared dependency rule. On the web, prefer transform/opacity where appropriate and avoid interleaving layout reads and writes across many elements. Inspect geometry animation costs rather than assuming a chosen API guarantees performance.

## Prove the behavior

Record the tested environment and workload: browser, viewport, representative content count, and frame target or display cadence when available. Use established performance targets; otherwise use the measured frame interval diagnostically rather than inventing a universal FPS guarantee.

Exercise representative transitions and the most demanding affected case. Observe the start, intermediate frames, interruption, and settlement in the running UI or a suitable recording. Include repeated unchanged input and rapid reversal where applicable. Check readability, flashes, clipping, layout jumps, focus, and input responsiveness, plus the reduced-motion alternative.

Pair visual observation with a browser performance trace or equivalent platform profiling evidence. Inspect frame timing/dropped frames where exposed, main-thread blocking, and layout/paint work. Investigate repeatable stalls caused by the implementation and recheck affected scenarios after correction. Average FPS, a screenshot, or absence of console errors alone cannot prove smoothness.

Regression assertions should target observable behavior during the transition, not only final values or whether an animation exists. Examples include a no-op action making no request or visual change, unaffected content keeping its position/opacity, and interrupted motion reaching the latest result without an initial jump. Use real browser evidence for rendering claims; mocked timing/geometry checks establish logic only.

## Completion

Keep a concise evidence record in the project's existing verification notes: requirement/scenario, environment, observation or assertion, artifact when available, and pass/fail/unverified result. Link it from the existing specification or report; no separate scoring framework is needed.

A harness pass covers only its registered assertions. Inspect coverage and preserve any required visual/performance checks outside the harness in the completion assessment. If required live observation or profiling is unavailable, finish unaffected work and mark motion acceptance incomplete with the concrete missing evidence. Do not lower the requirement, repeatedly rerun unchanged tests, or claim all-device smoothness. Claim measured smoothness only for the tested environment and workload.
