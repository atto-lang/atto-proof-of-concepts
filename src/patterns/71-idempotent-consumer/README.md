# 71. Idempotent Consumer

- **Category:** reliability
- **Hardening:** The in-memory example bounds signed balance updates before committing the message ID, and exercises both positive and negative boundary refusals. It does not implement a durable atomic inbox.
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Apply a message effect once when deliveries may be repeated.

## Implemented behavior

Stores accepted message IDs before applying a bounded in-memory balance update; checks duplicates and a full deduplication ledger.

## Safety and production gaps

Single-process sequential model with capacity three. Durable atomic inbox+business write and concurrent crash/retry behavior remain unproved.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned Oreslang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:71\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.ores`](example.ores) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
