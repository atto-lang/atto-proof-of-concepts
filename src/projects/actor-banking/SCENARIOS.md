# Actor banking and supervision: deterministic reference scenario

**Status:** reference-oracle fixture only; no Oreslang compilation or integration execution claimed.

## Scope exercised

Two-account transfers, duplicate delivery, and insufficient-funds refusal. Sequential reference; no actors have been spawned.

## Test contract

The [scenario.json](scenario.json) is an exact test vector. Run `python3 src/projects/check_scenarios.py` from the repository root. The Python checker evaluates the independent reference state machine and asserts exact expected outputs. This is **not** a native Oreslang result; it is an oracle for forthcoming `.ores` implementations.

## Invariants and negative cases

- Debit and credit must be atomic, signed overflow must be rejected, and total balance must remain constant. Duplicate transfer ID is idempotent, and insufficient funds must leave balances unchanged.

## Native backend work still required

Actor termination races, CONTROL supervision, atomic two-party commit, reordering, and failure injection.

Do not promote this project to `runtime-verified`, `formally-verified`, or `LLVM zero-GC` on the strength of these Python fixtures. Produce independent compiler-positive and targeted compiler-negative fixtures, exact-tree Java/LLVM runs, and a reproducible failure corpus first.

Conflicting re-use of a successful idempotency ID with a different sender, recipient, or amount **fails closed**; equal replays leave both balances unchanged. Python integers have arbitrary precision, so native signed-overflow enforcement still needs targeted compiler/runtime tests.

Insufficient-funds refusals also consume the idempotency key: if funds later arrive, replaying the same transaction ID remains a no-op. The conflict check compares payloads for both accepted and rejected attempts.
