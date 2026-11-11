# 87. Write-Ahead Log Replay

- **Category:** storage
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Reconstruct state from ordered write records and validated checkpoint positions.

## Implemented reference behavior

A bounded three-record in-memory log verifies append order, full replay, checkpoint-tail replay, out-of-range rejection, and overflow admission.

## Safety and production limitations

No durable fsync, disk record framing, torn-write handling, crash replay or transactional persistence; sentinel results are for demonstrative small integers.

## Acceptance

Use the [pattern runner](../EXECUTING.md) with a pinned real AttoLang guest runtime; require exit 0 and `PASS:87\n`. No sequential oracle establishes scheduler safety, durability or cross-backend parity.

[Source](example.atto) · [Output oracle](expected.stdout)
