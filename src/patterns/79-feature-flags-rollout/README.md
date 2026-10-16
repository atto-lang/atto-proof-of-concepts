# 79. Feature Flags and Sticky Rollout

- **Category:** enterprise/application
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Choose a deterministic per-account cohort and enforce a global kill switch.

## Implemented behavior

Checks zero/full rollout, stable hash assignment, account cohort discrimination, invalid configurations, and kill-switch precedence.

## Safety and production gaps

Fixed toy integer hash rather than real rollout bucketing; dynamic flag propagation, privacy, experiments, and release safety aren't modeled.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned Oreslang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:79\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.ores`](example.ores) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
