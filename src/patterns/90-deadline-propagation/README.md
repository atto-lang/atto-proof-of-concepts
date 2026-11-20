# 90. Deadline Propagation

- **Category:** reliability
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Ensure child operations cannot extend an inherited parent deadline.

## Implemented reference behavior

Clamps requested child deadlines, rejects expired parent or child, prevents negative timestamps, and tests equality at the deadline boundary.

## Safety and production limitations

Uses caller-supplied integer ticks; no real clock, async cancellation, propagation across processes or overflow policy.

## Acceptance

Use the [pattern runner](../EXECUTING.md) with a pinned real Oreslang guest runtime; require exit 0 and `PASS:90\n`. No sequential oracle establishes scheduler safety, durability or cross-backend parity.

[Source](example.ores) · [Output oracle](expected.stdout)
