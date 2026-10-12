# Graph editor with undo/redo

**Status: planned integration PoC, not built/tested.**

## Scope

Cyclic graphs, immutable command history, Visitor and serialization.

## Key correctness obligation

After any sequence of edits and undo/redo, the graph matches the reference state and reclaimed nodes do not remain reachable.

## Dependencies and patterns

oreslang-graphs, oreslang-persistent, oreslang-serialize, Visitor, Memento, Command.

## Acceptance tests

- Deterministic positive and negative examples, with reproducible inputs/expected outputs.
- Property-based operation sequences and a simpler executable reference oracle.
- Concurrency interleavings and cancellation/failure injection where applicable.
- GC/lifetime tests for all retained handles and closure/async roots.
- Java/GraalVM and LLVM results recorded separately, with exact compiler refs and checks.
- Performance measurements only after correctness; unsupported features explicitly tracked.

## Deliverables

Native Oreslang modules in this project directory, test fixtures and a result manifest with exact evidence links. A specification alone is not considered complete.
