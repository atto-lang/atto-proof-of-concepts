# Crash-recoverable embedded key-value store: deterministic reference scenario

**Status:** reference-oracle fixture only; no AttoLang compilation or integration execution claimed.

## Scope exercised

Committed-prefix recovery when a crash discards pending writes, followed by further committed writes.

## Test contract

The [scenario.json](scenario.json) is an exact test vector. Run `python3 src/projects/check_scenarios.py` from the repository root. The Python checker evaluates the independent reference state machine and asserts exact expected outputs. This is **not** a native AttoLang result; it is an oracle for forthcoming `.atto` implementations.

## Invariants and negative cases

- Recovery must expose exactly a committed prefix; pending uncommitted writes vanish after crash. Uncommitted rollback must not overwrite earlier committed values.

## Native backend work still required

Disk flush ordering, torn writes, fsync durability, actual WAL pages, concurrent transaction isolation, and crash-replay tests.

Do not promote this project to `runtime-verified`, `formally-verified`, or `LLVM zero-GC` on the strength of these Python fixtures. Produce independent compiler-positive and targeted compiler-negative fixtures, exact-tree Java/LLVM runs, and a reproducible failure corpus first.
