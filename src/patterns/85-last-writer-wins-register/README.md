# 85. Last-Writer-Wins Register

- **Category:** distributed systems
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Resolve simultaneous register writes by logical timestamp with replica ID tie-breaker.

## Implemented reference behavior

Reject stale versions, replay and lower-replica tie; accept higher-replica tie and larger timestamp; check stored value remains intact on invalid input.

## Safety and production limitations

Caller-provided logical versions, no Byzantine protection or network transport; intentionally drops concurrent losing writes.

## Acceptance

The pinned Java parser/type/ownership gate has passed; run the actual AttoLang guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:85\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.atto) · [Output oracle](expected.stdout)
