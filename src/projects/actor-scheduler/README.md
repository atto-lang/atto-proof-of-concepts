# Actor scheduler and work-stealing engine

**Status: planned integration PoC, not built/tested.**

## Scope

Task deques, futures, actor mailboxes, wakeup coalescing, shutdown and supervision.

## Key correctness obligation

No task or actor stateful turn runs twice concurrently, including across suspend/resume and cancellation.

## Dependencies and patterns

oreslang-work-stealing, oreslang-scheduler, oreslang-futures, Actor Model, Work Stealing.

## Acceptance tests

- Deterministic positive and negative examples, with reproducible inputs/expected outputs.
- Property-based operation sequences and a simpler executable reference oracle.
- Concurrency interleavings and cancellation/failure injection where applicable.
- GC/lifetime tests for all retained handles and closure/async roots.
- Java/GraalVM and LLVM results recorded separately, with exact compiler refs and checks.
- Performance measurements only after correctness; unsupported features explicitly tracked.

## Deliverables

Native Oreslang modules in this project directory, test fixtures and a result manifest with exact evidence links. A specification alone is not considered complete.
