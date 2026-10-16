# 84. Grow-Only Counter CRDT

- **Category:** distributed systems
- **Status:** native source prototype, not yet compiler-verified.

## Intent

Reconcile independent replica increments through componentwise maximum.

## Implemented reference behavior

Two-component grow-only counter, monotonic merge, idempotent join, out-of-order arrival, and rejection of invalid replicas/remote negative values.

## Safety and production limitations

Sequential replica model without transport, dynamic membership, integer overflow handling or durability.

## Acceptance

Run the actual pinned Oreslang parser, type/ownership checker and guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:84\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.ores) · [Output oracle](expected.stdout)
