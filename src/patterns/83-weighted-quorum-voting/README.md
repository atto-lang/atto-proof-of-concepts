# 83. Weighted Quorum Voting

- **Category:** distributed systems
- **Status:** native source prototype; Java parser/type/ownership PASS (20/20 funded exact-source CI), guest runtime and LLVM not yet verified.

## Intent

Configure read/write votes so read–write and write–write quorums intersect.

## Implemented reference behavior

Exhaustive 64 read/write subset pairs for three weighted voters (2,1,1); test threshold constraints and all 15 valid read/write pairs.

## Safety and production limitations

Fixed membership, no failures or split-brain coordinator; actual distributed state machine and linearizability are not proved.

## Acceptance

The pinned Java parser/type/ownership gate has passed; run the actual AttoLang guest runtime using [runner instructions](../EXECUTING.md). Require exact `PASS:83\n` and exit 0; negative fixtures and concurrent state histories are required for stronger guarantees. The oracle is only a sample behavior, not a proof.

[Source](example.atto) · [Output oracle](expected.stdout)
