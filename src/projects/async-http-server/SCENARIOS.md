# Asynchronous HTTP server: deterministic reference scenario

**Status:** reference-oracle fixture only; no Oreslang compilation or integration execution claimed.

## Scope exercised

Request routing, cancellation, exactly-once response completion/resource release, and missing-path handling in a synchronous reference.

## Test contract

The [scenario.json](scenario.json) is an exact test vector. Run `python3 src/projects/check_scenarios.py` from the repository root. The Python checker evaluates the independent reference state machine and asserts exact expected outputs. This is **not** a native Oreslang result; it is an oracle for forthcoming `.ores` implementations.

## Invariants and negative cases

- Each request ID is released exactly once, cancelled requests never produce successful responses, and unknown paths are 404. Real disconnection and partial I/O remain untested.

## Native backend work still required

Network sockets, carrier thread nonparking, partial reads, cancellation races, and streaming backpressure.

Do not promote this project to `runtime-verified`, `formally-verified`, or `LLVM zero-GC` on the strength of these Python fixtures. Produce independent compiler-positive and targeted compiler-negative fixtures, exact-tree Java/LLVM runs, and a reproducible failure corpus first.
