# Graph editor with undo/redo: deterministic reference scenario

**Status:** reference-oracle fixture only; no Oreslang compilation or integration execution claimed.

## Scope exercised

Immutable snapshot command history including cycle creation, undo, redo, and redo invalidation.

## Test contract

The [scenario.json](scenario.json) is an exact test vector. Run `python3 src/projects/check_scenarios.py` from the repository root. The Python checker evaluates the independent reference state machine and asserts exact expected outputs. This is **not** a native Oreslang result; it is an oracle for forthcoming `.ores` implementations.

## Invariants and negative cases

- Undo then redo must restore byte-equivalent node/edge sets. New edits invalidate redo. Stale node handles and edges to absent nodes must be rejected.

## Native backend work still required

Real heap references, stale identity rejection, immutable structural sharing, cycle reclamation, and serialization.

Do not promote this project to `runtime-verified`, `formally-verified`, or `LLVM zero-GC` on the strength of these Python fixtures. Produce independent compiler-positive and targeted compiler-negative fixtures, exact-tree Java/LLVM runs, and a reproducible failure corpus first.
