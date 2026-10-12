# Oreslang proof-of-concepts: src workspace

- [60 proposed libraries](libraries/README.md) with per-library acceptance briefs.
- [70 design patterns](patterns/README.md) with per-pattern acceptance briefs.
- [Verification contracts](validation/README.md) for borrow checks, GC, actor isolation, locks and backend parity.
- [Native source prototypes](pocs/README.md), including a linked-queue and selected patterns.

## Evidence levels

**planned** = brief only; **prototype** = source exists, not verified; **compiles** = actual compiler result recorded; **runtime-verified** = reproducible assertions/tests pass; **formally-verified** = checked proofs and explicit assumptions.

Do not confuse a completed catalog with proven compiler/runtime correctness.

Run python3 src/validation/check_catalog.py to check *only* structural catalog completeness.
