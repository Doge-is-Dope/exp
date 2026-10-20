# Architecture decisions

Keep design proportional to confirmed requirements. Record consequential choices, alternatives, and revisit conditions in the existing specification or ADRs.

- Before implementing a consequential boundary, sketch one caller's use and the data it exchanges, then derive the smallest useful contract. Include the failure or lifecycle rule that could invalidate the design. A short example in the existing specification is enough; routine edits do not need a separate design artifact. Compare alternatives only when the choice changes a material tradeoff.
- Organize by responsibility and data ownership. Follow domain terminology and stack conventions, including customary interface prefixes. Functions, modules, or framework services may suffice; use layers only when they help.
- Justify boundaries through current rules, confirmed changes, external contracts, integrity, or testability. Separate I/O when it obscures or duplicates rules. One provider may warrant isolation; similar code with different business meanings may remain separate. Avoid forwarding-only wrappers without a useful contract.
- With ports, the consuming core defines the capability, adapters implement it, and the entrypoint assembles them. Core code does not import concrete adapters. Function arguments or constructors can provide injection.
- Define relevant boundary semantics: errors, cancellation, resource lifetime, async work, transactions, concurrency, and migrations. Separate representations when their meanings differ. An interface alone does not guarantee replaceability.
- Trace a confirmed next change through responsibilities, contracts, and data. Identify reuse and coupling while preserving authorized scope. If no extension is confirmed, assess current cohesion and testability.
- Test behavior and material contracts; protect important dependency rules with existing stack tools. Judge concrete effects, not file counts or preferred patterns. Distinguish defects, evidence gaps, and optional improvements.
- Verify capacity against the specified workload and environment. Modular code does not prove scale. Add caching, queues, or services when requirements or measured bottlenecks justify them.

For example, a one-off CSV tool may need only cohesive functions. A CLI with a confirmed HTTP extension benefits from reusable operations, while HTTP stays deferred until requested. Framework CRUD can retain its natural conventions.
