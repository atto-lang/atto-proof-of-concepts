# oreslang-iter

- **Catalog:** library 17/60
- **Priority:** P0
- **Status:** planned specification; no validated implementation implied

## Scope

Generic lazy and mutable iterators.

## Critical correctness requirement

Aliasing through iter_mut cannot create concurrent exclusive element borrows.

## Acceptance suite

- Positive: a valid iter program executes its defining operation and checks its postcondition.
- Negative: a program violating a relevant borrow, lifetime, visibility, or effect rule is rejected with a targeted compiler diagnostic (not a syntax-only failure).
- Invariant: Aliasing through iter_mut cannot create concurrent exclusive element borrows.
- Property/model: compare generated operation histories to a simpler reference implementation or mathematical model.
- Runtime: exercise allocation failure, cleanup, cancellation and adversarial interleavings where applicable.
- Backend parity: run matching supported programs on Java/GraalVM and LLVM; report unsupported capabilities rather than skipping silently.

## Deliverables

An independently runnable native Oreslang implementation, executable positive/negative compiler fixtures, property-based operations, reproducible backend matrix and benchmark only after correctness.

## Source placement

Add Oreslang source (*.ores) and per-case fixtures in this directory. Do not treat this plan as a passing test.
