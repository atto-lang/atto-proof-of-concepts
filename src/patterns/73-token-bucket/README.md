# 73. Token Bucket

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Admit requests up to a burst capacity and replenish tokens at a fixed logical rate.

## Primary correctness property

Never exceed capacity or over-admit; reject zero/negative costs and nonmonotonic clock input.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

Uses bounded small integer tick arithmetic, not a real monotonic clock or atomic concurrent admission. Production use needs overflow-safe elapsed-time arithmetic and concurrent state protection.

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
