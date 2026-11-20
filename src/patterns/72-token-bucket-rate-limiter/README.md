# 72. Token Bucket Rate Limiter

- **Category:** reliability
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Bound bursts and refill admission credits over time.

## Implemented behavior

Tests burst depletion, denied consumption, time-based refill, bucket-capacity clamp, and backward-time rejection.

## Safety and production gaps

Time is an injected monotonic integer tick, not a runtime clock. Concurrent atomic admission, overflow checks, and distributed quota coordination are outside this model.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned Oreslang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:72\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.ores`](example.ores) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
