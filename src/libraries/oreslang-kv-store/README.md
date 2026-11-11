# oreslang-kv-store

- **Catalog:** library 49/60
- **Priority:** P1
- **Status:** planned specification; no validated implementation implied

## Scope

B+ tree/LSM, WAL, snapshot and crash recovery.

## Critical correctness requirement

Recovery returns exactly the durable committed prefix.

## Acceptance suite

- Positive: a valid kv-store program executes its defining operation and checks its postcondition.
- Negative: a program violating a relevant borrow, lifetime, visibility, or effect rule is rejected with a targeted compiler diagnostic (not a syntax-only failure).
- Invariant: Recovery returns exactly the durable committed prefix.
- Property/model: compare generated operation histories to a simpler reference implementation or mathematical model.
- Runtime: exercise allocation failure, cleanup, cancellation and adversarial interleavings where applicable.
- Backend parity: run matching supported programs on Java/GraalVM and LLVM; report unsupported capabilities rather than skipping silently.

## Deliverables

An independently runnable native AttoLang implementation, executable positive/negative compiler fixtures, property-based operations, reproducible backend matrix and benchmark only after correctness.

## Source placement

Add AttoLang source (*.atto) and per-case fixtures in this directory. Do not treat this plan as a passing test.
