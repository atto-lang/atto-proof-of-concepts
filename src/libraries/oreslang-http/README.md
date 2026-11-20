# oreslang-http

- **Catalog:** library 47/60
- **Priority:** P1
- **Status:** planned specification; no validated implementation implied

## Scope

Requests, responses, middleware, async handlers.

## Critical correctness requirement

Client disconnect/timeout never leaks request-owned resources.

## Acceptance suite

- Positive: a valid http program executes its defining operation and checks its postcondition.
- Negative: a program violating a relevant borrow, lifetime, visibility, or effect rule is rejected with a targeted compiler diagnostic (not a syntax-only failure).
- Invariant: Client disconnect/timeout never leaks request-owned resources.
- Property/model: compare generated operation histories to a simpler reference implementation or mathematical model.
- Runtime: exercise allocation failure, cleanup, cancellation and adversarial interleavings where applicable.
- Backend parity: run matching supported programs on Java/GraalVM and LLVM; report unsupported capabilities rather than skipping silently.

## Deliverables

An independently runnable native Oreslang implementation, executable positive/negative compiler fixtures, property-based operations, reproducible backend matrix and benchmark only after correctness.

## Source placement

Add Oreslang source (*.ores) and per-case fixtures in this directory. Do not treat this plan as a passing test.
