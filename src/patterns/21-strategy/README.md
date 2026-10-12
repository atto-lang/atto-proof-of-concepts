# 21. Strategy

- **Category:** GoF behavioral
- **Status:** planned (brief only; no verified implementation)

## Intent

Select interchangeable algorithms at runtime.

## Primary safety/correctness property

Each strategy obeys a shared contract under lexical captures.

## Required native Oreslang PoC

Implement real behavior with classes, traits/interfaces, generics, closures, recursive structures, actor isolation, ownership, or async/sync primitives as appropriate. Do not substitute a trivial stub.

## Acceptance tests

1. A positive example compiles and asserts observable results.
2. Invalid aliasing, lifetime, state or effect programs fail with *targeted semantic diagnostics*, when applicable.
3. Run adversarial resource, cancellation and concurrency cases as applicable; for concurrent structures check operation histories.
4. Record Java/GraalVM and LLVM commands, commit SHAs, stdout/exit codes, diagnostics and test results. Unimplemented backends are not passes.
5. Compare with a native Oreslang idiom, such as traits, enums, closures, or actors, where relevant.

No passing implementation is claimed by this catalog entry alone.
