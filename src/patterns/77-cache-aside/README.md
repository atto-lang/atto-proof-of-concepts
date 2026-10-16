# 77. Cache Aside

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Read through to an origin on cache miss/expiration and explicitly invalidate on writes.

## Primary correctness property

A hit avoids refetch; expiration and invalidation must force a subsequent origin read.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

The origin value and clock are injected; this model has no distributed coherence, stampede suppression, clock overflow guarantees, eviction, or failure semantics.

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
