# Actor scheduler and work stealing: deterministic reference scenario

**Status:** reference-oracle fixture only; no Oreslang compilation or integration execution claimed.

## Scope exercised

Task lifecycle transition oracle: single execution, cancellation, post-shutdown refusal.

## Test contract

The [scenario.json](scenario.json) is an exact test vector. Run `python3 src/projects/check_scenarios.py` from the repository root. The Python checker evaluates the independent reference state machine and asserts exact expected outputs. This is **not** a native Oreslang result; it is an oracle for forthcoming `.ores` implementations.

## Invariants and negative cases

- A task executes at most once, cancelled tasks never execute, and shutdown denies new work. Real concurrent owner/thief interleavings are absent.

## Native backend work still required

Carrier exclusivity, wakeup coalescing, atomic owner/thief races, suspension, fairness, supervisor STOP cleanup.

Do not promote this project to `runtime-verified`, `formally-verified`, or `LLVM zero-GC` on the strength of these Python fixtures. Produce independent compiler-positive and targeted compiler-negative fixtures, exact-tree Java/LLVM runs, and a reproducible failure corpus first.

The sequential reference STOP policy cancels every queued task once, allows no further dispatches, and refuses new submissions. Testing actual worker preemption, in-flight graceful draining, STOP resource cleanup, and cross-carrier resumption is still required.
