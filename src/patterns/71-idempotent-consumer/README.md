# 71. Idempotent Consumer

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Process a logical message once while returning the original result on duplicate delivery.

## Primary correctness property

A repeated message ID must not execute its side effect again, even if a later delivery carries a different payload.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

In-memory, single-process demonstration. A real consumer must persist the ID and result atomically with the business mutation, scope IDs appropriately, and handle concurrent deliveries and retention.

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
