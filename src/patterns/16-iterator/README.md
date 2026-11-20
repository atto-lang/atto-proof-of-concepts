# 16. Iterator

- **Category:** GoF behavioral
- **Status:** prototype (`example.ores` + `expected.stdout`; no verified compiler/runtime result)

## Intent

Abstract collection traversal.

## Primary safety/correctness property

Mutation cannot invalidate a still-live borrowed element unnoticed.

## Required native Oreslang PoC

Implement real behavior with classes, traits/interfaces, generics, closures, recursive structures, actor isolation, ownership, or async/sync primitives as appropriate. Do not substitute a trivial stub.

## Acceptance tests

1. A positive example compiles and asserts observable results.
2. Invalid aliasing, lifetime, state or effect programs fail with *targeted semantic diagnostics*, when applicable.
3. Run adversarial resource, cancellation and concurrency cases as applicable; for concurrent structures check operation histories.
4. Record Java/GraalVM and LLVM commands, commit SHAs, stdout/exit codes, diagnostics and test results. Unimplemented backends are not passes.
5. Compare with a native Oreslang idiom, such as traits, enums, closures, or actors, where relevant.

An independent native Oreslang prototype and output oracle have been added; they have not yet passed a documented compiler/runtime run.

## Native example

[`example.ores`](example.ores) · [`expected.stdout`](expected.stdout) · [shared harness](../run_examples.py)
