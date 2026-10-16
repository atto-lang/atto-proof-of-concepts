# 75. Rendezvous Hashing

- **Category:** distributed systems
- **Status:** source prototype, unverified by Java/GraalVM or LLVM compiler/runtime.

## Intent

Choose a deterministic shard by highest per-key/node score, with minimal reassignment when a node joins.

## Primary correctness property

Adding a node may retain the previous winner or move a key only to the new node, never to a different existing node.

## Exercise

The standalone [native Oreslang example](example.ores) checks observable success and failure cases using an exact [stdout oracle](expected.stdout). Run it through the [shared harness](../run_examples.py). The harness must use a real Oreslang compiler/runner and check exit code and output; structural checks are not runtime evidence.

## Limitations and next validation

Demonstration scores use tiny integer arithmetic and fixed numeric node IDs. Production systems need a stable high-quality 64/128-bit hash, canonical key encoding, weights, availability policy and migration/versioning.

Before claiming production correctness: run against pinned Java and LLVM compiler commits, add adverse inputs, assert failures against mutation/duplicate/reordering histories, and use integration or concurrency checks appropriate to the pattern.
