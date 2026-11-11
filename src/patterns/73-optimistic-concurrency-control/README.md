# 73. Optimistic Concurrency Control

- **Category:** reliability
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Reject a write when the caller's observed version is stale.

## Implemented behavior

Applies compare-and-increment updates, rejects stale writers and invalid values without changing the version.

## Safety and production gaps

The model is sequential. A database CAS or atomic transaction is required to prevent real concurrent lost updates.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned AttoLang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:73\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.atto`](example.atto) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
