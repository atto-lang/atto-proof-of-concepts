# 78. Scatter Gather

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Collect worker responses from a fan-out request up to a deadline, counting each worker at most once.

## Primary correctness property

Late, invalid, and duplicate responses do not change the aggregate; arrivals need not be ordered.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

Responses are injected sequentially. No futures, cancellation, network fan-out, physical timer, partial-failure policy, or single-flight actor synchronization is exercised.

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
