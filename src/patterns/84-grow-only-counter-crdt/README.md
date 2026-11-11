# 84. Grow-Only Counter CRDT

- **Category:** distributed systems
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Reconcile independent replica increments through componentwise maximum.

## Implemented reference behavior

Two-component grow-only counter, monotonic merge, idempotent join, out-of-order arrival, and rejection of invalid replicas/remote negative values.

## Safety and production limitations

Sequential replica model without transport, dynamic membership, integer overflow handling or durability.

## Acceptance

The pinned Java parser/type/ownership gate has passed; run the actual AttoLang guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:84\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.atto) · [Output oracle](expected.stdout)
