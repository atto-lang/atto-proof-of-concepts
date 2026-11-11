# 88. Retry Budget

- **Category:** reliability
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Bound retry amplification by spending explicit credits and replenishing only under policy.

## Implemented reference behavior

Two-credit retry budget: reject excess/invalid cost, clamp replenishment, debit valid retries and prevent negative balances.

## Safety and production limitations

No timers, idempotency policy, jitter, error classification, or admission coordination across actors or hosts.

## Acceptance

Use the [pattern runner](../EXECUTING.md) with a pinned real AttoLang guest runtime; require exit 0 and `PASS:88\n`. No sequential oracle establishes scheduler safety, durability or cross-backend parity.

[Source](example.atto) · [Output oracle](expected.stdout)
