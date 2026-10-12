# Oreslang proof-of-concepts: src workspace

- [60 proposed libraries](libraries/README.md), each with scoped correctness tests.
- [70 design patterns](patterns/README.md), each with a native implementation target.
- [Six integrated projects](projects/README.md), combining the hard language features.
- [Roadmap and top twelve proof targets](roadmap.md).
- [15 language capabilities](validation/language-capabilities.md) and [verification contracts](validation/README.md).
- [Native Oreslang source prototypes](pocs/README.md), including linked queue and selected patterns.

## Status

**planned** = a specification, **prototype** = source without verified run, **compiles** = exact compiler evidence, **runtime-verified** = reproducible passing tests, **formally-verified** = machine-checkable proof and declared assumptions.

The completed catalog does *not* prove the compiler, borrow checker or garbage collector. Run python3 src/validation/check_catalog.py for a structural-only check.
