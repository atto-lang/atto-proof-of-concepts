# 82. Lease Expiration and Renewal

- **Category:** distributed systems
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Bound an exclusive ownership claim using a monotonic expiry.

## Implemented reference behavior

Acquire, conflict rejection, holder-only renewal, takeover at expiration, release, and injected clock rollback rejection.

## Safety and production limitations

Local clock and authority model, not a network lease or fencing-token-enforced durable lock; the demo rejects ticks and durations beyond one million to keep 32-bit arithmetic bounded; real deployments require a monotonic trusted clock and fencing.

## Acceptance

The pinned Java parser/type/ownership gate has passed; run the actual AttoLang guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:82\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.atto) · [Output oracle](expected.stdout)
