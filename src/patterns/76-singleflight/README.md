# 76. Singleflight Request Coalescing

- **Category:** reliability
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Admit only one in-flight operation per key until its leader completes.

## Implemented behavior

Checks duplicate suppression, independent in-flight keys, release, slot reuse, and finite admission capacity.

## Safety and production gaps

Admission-only sequential model: does not share a future/result with followers, coordinate scheduler races, or handle cancellation.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned AttoLang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:76\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.atto`](example.atto) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
