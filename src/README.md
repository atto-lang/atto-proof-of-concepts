# Oreslang proof-of-concepts: source workspace

- [60 proposed libraries](libraries/README.md).
- [32 library source experiments](libraries/EXPERIMENTS.md) with independent expected outputs (unverified).
- [80 design pattern briefs](patterns/README.md), now each with independent `example.ores` and `expected.stdout`.
- [Pattern runner](patterns/EXECUTING.md) and [source harness](patterns/run_examples.py).
- [Six integrated project plans](projects/README.md).
- [Fifteen language capabilities](validation/language-capabilities.md), [verification contracts](validation/README.md), and [roadmap](roadmap.md).

## Evidence maturity

**planned** = specification; **prototype** = source but no recorded passing toolchain run; **compiles** = exact compiler result; **runtime-verified** = actual executed checks; **formally-verified** = machine-checked proof with assumptions.

The original 70 examples have a pinned historical 70/70 Java guest run; the 10 new examples (71–80) remain **unverified source prototypes**. Full 80-example Java and LLVM parity is not established. Advanced concurrency and lifetime examples may only demonstrate sequential models; read their comments/README for missing proof obligations.
