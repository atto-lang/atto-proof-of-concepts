# Crash-recoverable embedded key-value store

**Status: planned integration PoC, not built/tested.**

## Scope

B+ trees, WAL, transactions, cache, snapshots and crash recovery.

## Key correctness obligation

Recovery yields a committed prefix; all persisted values match a reference map after randomized operation histories.

## Dependencies and patterns

oreslang-btree, oreslang-kv-store, oreslang-cache, Repository, Unit of Work.

## Acceptance tests

- Deterministic positive and negative examples, with reproducible inputs/expected outputs.
- Property-based operation sequences and a simpler executable reference oracle.
- Concurrency interleavings and cancellation/failure injection where applicable.
- GC/lifetime tests for all retained handles and closure/async roots.
- Java/GraalVM and LLVM results recorded separately, with exact compiler refs and checks.
- Performance measurements only after correctness; unsupported features explicitly tracked.

## Deliverables

Native Oreslang modules in this project directory, test fixtures and a result manifest with exact evidence links. A specification alone is not considered complete.
