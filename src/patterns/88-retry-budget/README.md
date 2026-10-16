# 88. Retry Budget

- **Category:** reliability
- **Status:** native source prototype, not yet compiler-verified.

## Intent

Bound retry amplification by spending explicit credits and replenishing only under policy.

## Implemented reference behavior

Two-credit retry budget: reject excess/invalid cost, clamp replenishment, debit valid retries and prevent negative balances.

## Safety and production limitations

No timers, idempotency policy, jitter, error classification, or admission coordination across actors or hosts.

## Acceptance

Use the [pattern runner](../EXECUTING.md) with pinned real Oreslang compiler and runtime; require exit 0 and `PASS:88\n`. No sequential oracle establishes scheduler safety, durability or cross-backend parity.

[Source](example.ores) · [Output oracle](expected.stdout)
