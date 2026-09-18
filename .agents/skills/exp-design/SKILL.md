---
name: exp-design
description: Design, refine, or review MVP interfaces, interaction states, and motion.
---

# exp design

Follow [AGENTS.md](../../../AGENTS.md). Use the established project and the user's requested scope: advice and review do not authorize product edits; an implementation request does not need another design approval gate.

## Direction and scope

Identify the main task, audience, platform, and existing design conventions. Preserve successful patterns and explain consequential choices briefly in the existing specification when edits are authorized. A small change may need only a recommendation; use a prototype when it resolves a meaningful uncertainty and label simulated behavior.

For new interactive interfaces or substantive motion changes, read [motion design and acceptance](references/motion.md). Also read it when reviewing motion or investigating flicker, jumps, or interruption behavior. A copy-only change or static screenshot review does not require motion testing. Existing explicit performance requirements remain binding.

## Design judgment

Treat references and user-approved work as evidence of intent and experience. Observe what holds attention, what makes a change legible, and how rhythm, typography, spacing, and emphasis work together. Explain the consequential relationship; adjectives such as polished, premium, or minimal are not a design rationale. Transfer the useful principle to the current task rather than copying a style, parameter, or implementation.

Interpret feedback at the scope it supports. A preference for one transition is a clue about that interaction, not proof that the user wants the same effect everywhere. Distinguish an explicit preference from your hypothesis about its cause. When authorized, keep consequential preferences and their context in the existing project specification; revise the hypothesis when new feedback contradicts it.

Where the choice materially affects the experience, compare the current result with an approved reference or a plausible alternative using the same content, action, size, and repetition rate. Try alternatives locally when they resolve a real uncertainty; do not require multiple mockups for routine edits. Consider retaining the current design, reducing an effect, or using no motion when that better supports the task. Look beyond novelty and first impressions to repeated use, readability, interruption, and the coherence of the whole interface.

Make a contextual choice and state the important tradeoff briefly. Technical correctness and performance are necessary evidence, but do not select the most pleasing design by themselves. Evaluate perceptual quality separately through actual viewing and interaction; a test pass cannot settle a preference. Missing dynamic evidence remains unverified, not an invitation to invent an aesthetic verdict.

## Interface quality

- Make the main action and current state easy to find. Remove redundant copy and competing decoration; preserve labels, navigation cues, and explanations needed to act. Use grouping, alignment, and typography before adding containers. Match spacing to content density.
- Reuse the project's visual roles and components. Refine icon scale, stroke, alignment, text clearance, and target size together. Preserve platform semantics, keyboard behavior, and visible focus when customizing controls. Apple-inspired appearance does not require native chrome on the web.
- Organize supporting content within the region it describes. Check the whole layout when content grows: short and long lists should not unexpectedly move unrelated controls. Verify stacked layouts where relevant.
- Use the user's language and consistent product vocabulary. Keep implementation details out of product copy.

## State design

Treat loading, populated, empty, refreshing, and failed results as states of the affected region. Empty means a successful request confirmed no data; distinguish no records from no filter matches. During refresh, preserve useful results and their actual scope until replacement data arrives. Keep input recoverable and recovery actions discoverable.

Choose one primary feedback surface per event. List state belongs near the results; a toast may suit a brief action outcome. Update a single notification through a task's lifecycle rather than stacking duplicates. Essential errors must remain discoverable after transient feedback disappears. Fast responses and repeated actions should not flash notices, dim unchanged content, or replay entrances; an unchanged action that has no refresh purpose should do no work.

## Implementation and review

Use the existing stack and applicable platform guidance; for web implementation use `modern-web-guidance` when available. When invoked from build or debug, return findings and design decisions to that active workflow without restarting it. For a standalone implementation request, use [exp-build](../exp-build/SKILL.md) for delivery or [exp-debug](../exp-debug/SKILL.md) for a reproduced failure.

Verify the affected flow with representative data, sizes, and input methods. Choose cases that expose the actual risk: empty/short/long content, long labels, changing value widths, fast/slow/failed requests, repeated input, keyboard focus, or text enlargement. Observe intermediate states as well as settled results. Use the motion reference for motion acceptance; screenshots alone cannot establish interaction behavior.

Report observed defects with location, impact, and a concrete correction. Separate stylistic preferences, measured defects, and unverified behavior. Report limitations rather than inventing compliance, performance scores, or findings. Shared code review and completion requirements remain in AGENTS.

## References

This independently written workflow was informed by [dickwu/apple-design-skill](https://github.com/dickwu/apple-design-skill); no upstream skill text is bundled. Consult relevant [Apple HIG](https://developer.apple.com/design/human-interface-guidelines) for Apple-specific decisions, [WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/) for accessibility criteria, or [Sonner](https://sonner.emilkowal.ski/) for toast patterns. References inform choices; they do not mandate a library or style. Cite the exact source used and disclose unavailable references.
