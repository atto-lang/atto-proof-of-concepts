# 85. Last-Writer-Wins Register

- **Category:** distributed systems
- **Status:** native source prototype, not yet compiler-verified.

## Intent

Resolve simultaneous register writes by logical timestamp with replica ID tie-breaker.

## Implemented reference behavior

Reject stale versions, replay and lower-replica tie; accept higher-replica tie and larger timestamp; check stored value remains intact on invalid input.

## Safety and production limitations

Caller-provided logical versions, no Byzantine protection or network transport; intentionally drops concurrent losing writes.

## Acceptance

Run the actual pinned Oreslang parser, type/ownership checker and guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:85\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.ores) · [Output oracle](expected.stdout)
