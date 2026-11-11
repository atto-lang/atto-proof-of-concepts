# 77. Cache Aside

- **Category:** enterprise/application
- **Hardening:** Rejects keys beyond the safe signed 32-bit multiplication range before loading or mutating the cache; tests the rejection and upper valid boundary.
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Load data on a miss and explicitly invalidate cached entries after changes.

## Implemented behavior

Checks hits avoid backing loads, misses load fresh values, unrelated invalidation is ignored, and matching invalidation forces reload.

## Safety and production gaps

Single-entry toy cache; no backing database, expiry policy, invalidation race, or multi-process coherence.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned AttoLang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:77\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.atto`](example.atto) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
