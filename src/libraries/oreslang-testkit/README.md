# oreslang-testkit

- **Catalog:** library 56/60
- **Priority:** P0
- **Status:** planned specification; no validated implementation implied

## Scope

Assertions, fixtures, deterministic setup and cleanup.

## Critical correctness requirement

Failing checks cannot be reported as successes or leave resources alive.

## Acceptance suite

- Positive: a valid testkit program executes its defining operation and checks its postcondition.
- Negative: a program violating a relevant borrow, lifetime, visibility, or effect rule is rejected with a targeted compiler diagnostic (not a syntax-only failure).
- Invariant: Failing checks cannot be reported as successes or leave resources alive.
- Property/model: compare generated operation histories to a simpler reference implementation or mathematical model.
- Runtime: exercise allocation failure, cleanup, cancellation and adversarial interleavings where applicable.
- Backend parity: run matching supported programs on Java/GraalVM and LLVM; report unsupported capabilities rather than skipping silently.

## Deliverables

An independently runnable native AttoLang implementation, executable positive/negative compiler fixtures, property-based operations, reproducible backend matrix and benchmark only after correctness.

## Source placement

Add AttoLang source (*.atto) and per-case fixtures in this directory. Do not treat this plan as a passing test.
