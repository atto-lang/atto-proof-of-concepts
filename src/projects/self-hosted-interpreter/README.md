# Self-hosted reference interpreter

**Status: planned integration PoC, not built/tested.**

## Scope

Tokenizer, recursive AST, lexical environment, closures, evaluator and tests.

## Key correctness obligation

Evaluation matches documented language semantics on both backends; illegal captures are rejected rather than emulated unsafely.

## Dependencies and patterns

oreslang-ast, oreslang-closures, oreslang-interpreter, Interpreter, Visitor.

## Acceptance tests

- Deterministic positive and negative examples, with reproducible inputs/expected outputs.
- Property-based operation sequences and a simpler executable reference oracle.
- Concurrency interleavings and cancellation/failure injection where applicable.
- GC/lifetime tests for all retained handles and closure/async roots.
- Java/GraalVM and LLVM results recorded separately, with exact compiler refs and checks.
- Performance measurements only after correctness; unsupported features explicitly tracked.

## Deliverables

Native Oreslang modules in this project directory, test fixtures and a result manifest with exact evidence links. A specification alone is not considered complete.
