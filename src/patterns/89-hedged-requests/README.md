# 89. Hedged Requests

- **Category:** reliability
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Prefer the earliest successful request among a primary and delayed hedge.

## Implemented reference behavior

Deterministic completion arbitration of two attempts: fastest successful result wins, failed attempts ignored, ties favor the primary, invalid completion times rejected.

## Safety and production limitations

Only a result-selection model; no parallel I/O, cancellation of losing requests, idempotency checks, hedging delays or resource accounting.

## Acceptance

Use the [pattern runner](../EXECUTING.md) with a pinned real AttoLang guest runtime; require exit 0 and `PASS:89\n`. No sequential oracle establishes scheduler safety, durability or cross-backend parity.

[Source](example.atto) · [Output oracle](expected.stdout)
