# 82. Lease Expiration and Renewal

- **Category:** distributed systems
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Bound an exclusive ownership claim using a monotonic expiry.

## Implemented reference behavior

Acquire, conflict rejection, holder-only renewal, takeover at expiration, release, and injected clock rollback rejection.

## Safety and production limitations

Local clock and authority model, not a network lease or fencing-token-enforced durable lock; tick arithmetic overflow must be bounded by callers.

## Acceptance

The pinned Java parser/type/ownership gate has passed; run the actual Oreslang guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:82\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.ores) · [Output oracle](expected.stdout)
