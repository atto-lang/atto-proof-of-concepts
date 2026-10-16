# 76. Dead Letter Queue

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Retry transient failures to a bounded budget and quarantine repeatedly failing messages.

## Primary correctness property

Failures exceeding the retry budget produce exactly one dead-letter entry; a successful delivery is never retried.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

No broker, ack, persistence, redrive policy, concurrency, or poison-message serialization is implemented. This is a deterministic routing state machine only.

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
