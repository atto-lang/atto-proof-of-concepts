# 86. Credit-Based Flow Control

- **Category:** messaging
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Enforce bounded in-flight message capacity using explicit delivery credits.

## Implemented reference behavior

A two-credit admission table tracks unacknowledged IDs, rejects duplicate sends and invalid acknowledgments, and restores credits on completion.

## Safety and production limitations

Sequential state machine only; does not prove actor mailbox backpressure, network acknowledgments, retries or deadlock freedom.

## Acceptance

Use the [pattern runner](../EXECUTING.md) with a pinned real Oreslang guest runtime; require exit 0 and `PASS:86\n`. No sequential oracle establishes scheduler safety, durability or cross-backend parity.

[Source](example.ores) · [Output oracle](expected.stdout)
