# Ready-to-use prompts

Replace the bracketed text. Include only requirements that affect the outcome; you do not need to choose the technology first.

## Build an MVP

```text
Use $exp-build to complete [project name].
Goal: [who will use it and what they need to do]
Acceptance: [what must work]
Constraints or preferences: [platform, data, deployment, technology; omit if none]
Time budget: [optional]
Deliver a running result with startup instructions and evidence for the acceptance criteria; identify unfinished requirements.
```

## Explore architecture and flows

```text
Use $exp-brainstorm to explore [idea].
Recommend an architecture and explain the important choices and user flows.
Plan only; do not implement the application yet.
```

When a visual comparison would help, add: “Present the choices in interactive HTML.”

## Design or improve an interface

```text
Use $exp-design for [project or screen].
Main user task: [what people need to do]
Design constraints: [existing brand, platform, references; omit if none]
Propose a suitable visual direction and interaction states. Plan only; do not change application code.
```

For implementation, replace the last sentence with: “Implement the design and verify the affected interactions against the agreed acceptance criteria.”

For polished motion, add: “Use transitions.dev as a motion reference. Verify visual continuity and measured smoothness in a stated browser and workload; disclose any missing evidence.”

## Clarify requirements only

```text
Help clarify the scope and acceptance criteria for [idea]. Do not modify files yet.
```

## Review

```text
Use $exp-review to review [project] against [requirements or SPEC path].
Review code quality using the workspace principles and report evidence-backed issues and verification gaps. Do not edit the code yet.
```

## Fix a problem

```text
Use $exp-debug to fix a problem in [project].
Reproduction: [steps]
Expected: [result]
Actual: [result and error messages]
```

## Change requirements

```text
Change the requirements for [project] to [changes]. Update the existing specification and complete implementation and verification.
```

## Handoff

```text
Summarize current requirements, completed work, actual verification results, unresolved issues, and next steps for another session.
```

## Remove projects

```text
Use $exp-reset to list projects and let me select which ones to remove.
```

Selected projects move to `.practice-backups/` and can be restored.

## Optional harness acceptance

```text
Use $exp-build to complete [project] with harness acceptance.
Goal and observable acceptance: [requirements]
Register real executable checks, complete implementation, code review, and documentation,
then obtain a fresh passing harness report and provide its evidence.
```

## Bounded automatic repair

```text
Use the harness run controller to repair [existing harness project]
against its established acceptance checks. Limit repair to [attempts]
and [total seconds]. Report passing evidence or the concrete stopping reason.
```
