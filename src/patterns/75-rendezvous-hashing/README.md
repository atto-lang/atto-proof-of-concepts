# 75. Rendezvous Hashing

- **Category:** distributed systems
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Assign a key deterministically to the highest-scoring available node.

## Implemented behavior

Validates stable highest-score selection, unchanged assignment when an unrelated node disappears, and reassignment when the winning node disappears.

## Safety and production gaps

Toy small-integer scoring over three nodes, not a production-quality uniform 64-bit hash function; no live membership propagation.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned AttoLang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:75\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.atto`](example.atto) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
