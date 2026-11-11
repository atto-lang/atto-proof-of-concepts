# 78. Dead Letter Queue

- **Category:** reliability
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Quarantine repeatedly failing messages after retry budget exhaustion.

## Implemented behavior

Enqueues only terminal failures, avoids duplicate dead-letter IDs, and declines admission on a bounded full queue.

## Safety and production gaps

An in-memory two-slot sequential queue; no broker acknowledgements, durable persistence, retry timing, replay, or poison-message sandbox.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned AttoLang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:78\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.atto`](example.atto) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
