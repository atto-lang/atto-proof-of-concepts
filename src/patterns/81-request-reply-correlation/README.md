# 81. Request–Reply Correlation

- **Category:** messaging
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Match out-of-order replies to outstanding request IDs.

## Implemented reference behavior

Bounded pending request ID table: duplicate admission rejection, out-of-order completion, replay rejection and slot reuse.

## Safety and production limitations

Sequential correlation table only; no actor mailbox, response future, timeout, cancellation or network transport.

## Acceptance

The pinned Java parser/type/ownership gate has passed; run the actual AttoLang guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:81\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.atto) · [Output oracle](expected.stdout)
