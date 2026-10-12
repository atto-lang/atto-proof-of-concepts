# oreslang-files

- **Catalog:** library 45/60
- **Priority:** P1
- **Status:** planned specification; no validated implementation implied

## Scope

Nonparking file IO, descriptor lifecycle and cancellation.

## Critical correctness requirement

The _blocking API does not park an OresVM carrier; descriptors close once.

## Acceptance suite

- Positive: a valid files program executes its defining operation and checks its postcondition.
- Negative: a program violating a relevant borrow, lifetime, visibility, or effect rule is rejected with a targeted compiler diagnostic (not a syntax-only failure).
- Invariant: The _blocking API does not park an OresVM carrier; descriptors close once.
- Property/model: compare generated operation histories to a simpler reference implementation or mathematical model.
- Runtime: exercise allocation failure, cleanup, cancellation and adversarial interleavings where applicable.
- Backend parity: run matching supported programs on Java/GraalVM and LLVM; report unsupported capabilities rather than skipping silently.

## Deliverables

An independently runnable native Oreslang implementation, executable positive/negative compiler fixtures, property-based operations, reproducible backend matrix and benchmark only after correctness.

## Source placement

Add Oreslang source (*.ores) and per-case fixtures in this directory. Do not treat this plan as a passing test.
