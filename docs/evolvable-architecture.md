# Evolvable architecture: research and implementation plan

## Goal and status

Research and completion date: 2026-09-19. Status: approved scope implemented and validated. Shared rules, architecture reference, skill routing, specification guidance, and prompt examples are complete. This document is the source of scope, decisions, and observed results for this toolkit change.

Help exp produce MVPs whose responsibilities, names, contracts, and dependencies support the next confirmed change without sacrificing proportionate delivery. Apply this to the applications exp builds; do not turn the workbench into an application framework.

Keep two outcomes distinct: **evolvability** concerns the cost and safety of changing software; **runtime scalability** concerns behavior as workload and resources change. Good module boundaries support the former but do not prove the latter.

## Research and implications

The sources below support decision criteria, not a universally best folder layout. The exp recommendations are an adaptation to this technology-neutral, predominantly single-developer MVP workflow.

| Finding | Primary source and evidence type | Implication for exp |
| --- | --- | --- |
| Early service boundaries are uncertain; distributed services add operating and refactoring costs. | Martin Fowler, [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html), practitioner observations explicitly described as tentative. | Prefer a simple deployment shape for a new small app when appropriate. Make internal responsibilities clear; do not mandate microservices or a four-layer layout. |
| Deferring speculative capabilities is compatible with ongoing refactoring and easy-to-change code. | Martin Fowler, [Yagni](https://martinfowler.com/bliki/Yagni.html), design guidance. | Invest in present readability, tests, and necessary boundaries. A hypothetical future provider does not itself justify implementing a provider framework. |
| Similar code can evolve for different reasons; extracting it too early can create condition-heavy abstractions. | Sandi Metz, [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction), practitioner analysis. | Judge shared semantics and change ownership, not a fixed duplication count. One provider may merit isolation; two similar functions may properly remain separate. |
| Architecture should enable independent change and testing with limited coordination. | [DORA: Loosely coupled teams](https://dora.dev/capabilities/loosely-coupled-teams/), research-based delivery capability guidance. | Inspect whether a change forces unrelated responsibilities to change. Do not transplant team/service deployment measures directly into a single-process MVP score. |
| Complex domain logic can justify DDD; simpler CRUD responsibilities can use simpler designs. | [Microsoft: Designing a DDD-oriented microservice](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice), official platform guidance. | Preserve useful framework conventions and proportional structure. Do not manufacture a domain layer containing only duplicated data types. |
| Naming conventions depend on the language and ecosystem; .NET recommends an I prefix for interfaces. | [Microsoft: Names of Classes, Structs, and Interfaces](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/names-of-classes-structs-and-interfaces), official naming guidance. | Require meaningful, consistent terms while following the chosen stack. Do not universally prohibit Service, Manager, or I-prefixed interfaces. |
| Significant decisions need their context, consequences, and status preserved for later maintainers. | Michael Nygard, [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), original ADR proposal. | Adapt the reasoning to the existing SPEC tradeoffs section. Preserve an existing ADR system, but do not create a second mandatory decision registry. |
| Architecture can evolve through small changes and feedback; executable checks can protect selected structural properties. | Fowler, [Foreword to Building Evolutionary Architectures](https://martinfowler.com/articles/evo-arch-forward.html), and [ArchUnit user guide](https://www.archunit.org/userguide/html/000_Index.html), design guidance and a concrete testing implementation. | Test relevant dependency or contract invariants with stack-appropriate tools. Structural tests prove those invariants, not overall design quality. ArchUnit is an example, not a toolkit dependency. |
| Capacity and resilience depend on workload, resources, constraints, and validation. | [Google Cloud: Patterns for scalable and resilient apps](https://docs.cloud.google.com/architecture/scalable-and-resilient-apps), official cloud architecture guidance. | Require workload and environment evidence before claiming runtime scale. Cloud-specific products are not defaults for local MVPs. |

## Decisions for this plan

- Keep one build workflow. Scale architecture effort with confirmed changes, business rules, state ownership, deployment constraints, and failure consequences. Do not add Rapid/Evolving profiles, a new CLI mode, or a mandatory architecture phase for small edits.
- Preserve technology neutrality: functions, modules, framework services, packages, or classes may all establish useful boundaries. A single deployment unit is often suitable, but no universal layering or directory tree is required.
- Boundaries need a concrete reason: distinct responsibilities, shared business rules, an external contract, a confirmed replacement, data integrity, or focused testing. A second implementation is neither required nor sufficient to justify an interface. Avoid forwarding-only wrappers unless they enforce a meaningful contract.
- Distinguish source dependency from runtime calls. When using ports, the consuming core/application owns the required capability; an adapter implements that contract, and an entrypoint assembles them. Do not make domain code import concrete adapters or describe a runtime call diagram as an import rule.
- Keep cohesive behavior together. Separate I/O and orchestration where mixing them obscures rules, duplicates policy across entrypoints, or prevents appropriate tests. A trivial application can express this with a few functions.
- Name concepts consistently within their domain context, and name responsibilities precisely. Separate transport, domain, and storage representations when their semantics differ; avoid redundant copies when they do not. Follow language and repository conventions before prescribing spellings or suffixes.
- Treat schema migrations, transaction boundaries, asynchronous behavior, errors, and resource ownership as part of a boundary when relevant. An interface name alone does not make a database or provider replaceable.
- Preserve existing architecture and public contracts during scoped updates. Diagnose a concrete coupling or acceptance issue before widening a refactor. A speculative change exercise can inform a proposal, but cannot authorize a future feature or unrelated restructuring.

## Implementation

Shared principles live in [AGENTS.md](../AGENTS.md). Build, brainstorm, and review conditionally load one [architecture reference](../.agents/skills/exp-build/references/architecture.md). [SPEC](../scaffold/SPEC.md) records consequential decisions and actual capacity requirements; [PROMPTS.md](../PROMPTS.md) provides examples.

Use meaningful behavior, contract, and dependency checks. Complete required gates; broaden verification only for changes, failures, or unresolved concerns. Keep small edits proportionate.

## Behavioral acceptance scenarios

| Scenario | Required outcome and evidence |
| --- | --- |
| Small one-off CSV summarizer with no confirmed extension | It runs correctly using a natural, small structure. Every introduced abstraction has a present responsibility; no unused provider/factory/repository infrastructure. Verify observable output and documented startup from a fresh source copy. |
| Existing task CLI with an explicitly confirmed later HTTP entrypoint, but only CLI work authorized now | Input parsing and reusable task operations have a justified boundary; tests can invoke the operations without CLI parsing. A static HTTP change exercise identifies reuse and affected contracts. No HTTP endpoint is implemented in this phase. |
| Actual authorized extension of the preceding fixture | Freeze the CLI baseline, then give another fresh-context agent the separate request to add local HTTP access. The new transport reuses task rules, preserves the CLI/storage contract, and passes real local HTTP and existing CLI tests. Inspect the diff for duplicated policy and unrelated changes; document any necessary contract change. This verifies one concrete extension, not all future changes. |
| Existing framework CRUD and language-specific naming | A read-only architecture review preserves framework conventions and, for a .NET sample, does not reject the I prefix. Similar-looking but semantically distinct rules are not forced into a generic service. Preserve fixture hashes and classify unsupported preferences separately from defects. |
| Service with explicit concurrency/data-volume acceptance but no supplied load evidence | Review identifies the missing runtime evidence even if layering looks clean. It names a bounded verification method using the supplied workload rather than claiming capacity or inventing targets. This scenario validates review judgment, not service performance. |
| Narrow copy change or planning-only request | The agent stays within scope; no unrelated architecture refactor, mandatory reference-reading cascade, new approval gate, or runtime load-test campaign. Planning remains planning. |

A fixture prompt's declared extension is not permission to implement it until that phase is requested. Any review, study, or simulation is labeled separately from executed acceptance. Do not infer production readiness from passing local tests.

## Validation summary — 2026-09-19

Separate fresh-context agents exercised the scenarios above. Main-agent review inspected source and diffs and ran independent acceptance checks.

| Scenario | Result |
| --- | --- |
| CSV | Independent acceptance 6/6; cohesive implementation without unused abstractions. |
| CLI preparation | Independent acceptance 7/7; reusable operations with HTTP deferred. |
| HTTP extension | Independent HTTP 6/6; native and fresh-source tests 11/11. Existing core and CLI files unchanged. |
| Review | Preserved .NET naming and independently owned rules; identified missing capacity evidence. |
| Scope | Export remained planned; copy-only task changed just the requested heading. |

Fixtures and raw outputs remain local, ignored validation artifacts. These results cover Python 3.14.7 and serial loopback operations. They do not establish runtime capacity, .NET execution, or improvement over the previous exp version.

## Prompt maintenance

Following [OpenAI's Astra prompting guidance](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra#prompting-best-practices), keep instructions clear, communication concise, and verification proportionate. Preserve user scope and avoid conflicting or repeated guidance.

Updated 2026-09-19: wording shortened and local evidence links removed. Scenario results above describe the evaluated wording before this edit; focused static checks validate this documentation revision. Next: use the guidance on the next requested project and verify its acceptance criteria.
