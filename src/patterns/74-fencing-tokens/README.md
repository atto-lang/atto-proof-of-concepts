# 74. Fencing Tokens

- **Category:** distributed systems
- **Status:** new native source prototype; Java/GraalVM and LLVM compilation/execution **not yet verified** for this revision.

## Intent

Reject effects from stale holders after a newer lease epoch is issued.

## Implemented behavior

Issues increasing tokens; rejects previous-holder writes, fabricated future values, duplicate application, and accepts newer epochs.

## Safety and production gaps

Local sequencer plus sink model; a durable linearizable token issuer and downstream fence enforcement are necessary in a distributed deployment.

## Evidence / acceptance

Run the source using the [pattern runner](../run_examples.py) with a real pinned AttoLang compiler and runtime, first on Java/GraalVM then on LLVM where supported. Require exact `PASS:74\n` and zero exit status; also test expected compiler rejections where ownership or concurrency applies. Passing this oracle alone does **not** establish full real-world safety.

[Native `example.atto`](example.atto) · [`expected.stdout`](expected.stdout) · [runner instructions](../EXECUTING.md)
