# 80. Vector Clocks

- **Category:** distributed systems
- **Hardening:** Rejects increment attempts when either component reaches the signed 32-bit maximum without wrapping, and tests unchanged state after the rejection.
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Track causal ordering and detect concurrent events without a total order.

## Implemented behavior

Advances two components, detects concurrent histories, merges component-wise maxima, and verifies happens-before/equality relations.

## Safety and production gaps

Two-participant sequential model; no actor transport, epoch management, overflow protection, dynamic membership, or real distributed consistency proof.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned Oreslang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:80\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.ores`](example.ores) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
