# 72. Transactional Inbox

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Apply an incoming message only if the inbox record and domain update commit together.

## Primary correctness property

A rolled-back message can be retried, but a committed message ID cannot be applied again.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

The commit decision is injected, not a real database transaction. Implement durable inbox rows, unique indexes, same-transaction domain writes and concurrency/rollback fault injection before relying on exactly-once effects.

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
