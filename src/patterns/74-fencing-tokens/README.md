# 74. Fencing Tokens

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Prevent a previous lease holder from mutating shared state after a successor receives a higher token.

## Primary correctness property

Only the latest issued fencing token can authorize a write; stale and unissued tokens are rejected.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

A single issuer and protected resource are modeled in one in-memory object. In production, token allocation must be linearizable and tokens enforced by the actual downstream resource (not merely checked client-side).

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
