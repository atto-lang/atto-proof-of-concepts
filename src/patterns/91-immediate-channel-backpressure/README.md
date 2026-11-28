# 91. Immediate Channel Backpressure and Recoverable Ownership

- **Category:** actor channels, backpressure, ownership
- **Status:** draft source prototype; actual compiler and guest runtime execution **NOT VERIFIED**

## Intent

Show the typed immediate `try writech channel, value` contract without registering a waiter. This pattern exercises `Accepted`, `Full(original)`, retry after a consumer creates capacity, and `Closed(original)` after channel shutdown.

Unlike `writech` (cooperatively suspends) or `nb writech` (creates a Future), this probe must decide immediately. Both non-accepting variants return the *original* owned payload. The first write transfers the value to the channel; the retry transfers the recovered value only after the read creates capacity.

## Acceptance

- Compile and execute [`example.ores`](example.ores) with a pinned Java/GraalVM source revision that implements spec chapter 27 and prove exactly [`PASS:91`](expected.stdout) with exit 0.
- Verify the same guest with LLVM, .NET Native AOT, Forge and Wasm when their implementations exist. Do not use parser acceptance or source-only text checks as runtime evidence.
- Extend the test to the zero-capacity rendezvous case, concurrent close/read/write linearization, a non-Copy payload with destructor-count checks, and negative use-after-move diagnostics.
- Use the [pattern runner](../run_examples.py) for exact stdout checking. The shared bounded source-free history oracle in platform-conformance PR #728 is supplementary and does not prove guest execution.

**Status note:** the new typed operation is in Java source PR #3109 and spec PR #66; this is a deliberately draft example until the exact compiler/runtime receipt is produced.
