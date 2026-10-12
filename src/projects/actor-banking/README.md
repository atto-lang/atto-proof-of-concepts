# Actor banking and supervision

**Status: planned integration PoC, not built/tested.**

## Scope

Accounts as actors, transfer workflow, event sourcing and supervisor CONTROL.

## Key correctness obligation

Each account state is serializable, every transfer preserves total funds, and actor panic never bypasses the supervisor.

## Dependencies and patterns

oreslang-actors, oreslang-event-log, Saga, Supervisor Tree, CQRS.

## Acceptance tests

- Deterministic positive and negative examples, with reproducible inputs/expected outputs.
- Property-based operation sequences and a simpler executable reference oracle.
- Concurrency interleavings and cancellation/failure injection where applicable.
- GC/lifetime tests for all retained handles and closure/async roots.
- Java/GraalVM and LLVM results recorded separately, with exact compiler refs and checks.
- Performance measurements only after correctness; unsupported features explicitly tracked.

## Deliverables

Native Oreslang modules in this project directory, test fixtures and a result manifest with exact evidence links. A specification alone is not considered complete.
