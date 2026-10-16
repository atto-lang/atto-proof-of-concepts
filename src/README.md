# Oreslang proof-of-concepts: source workspace

- [60 proposed libraries](libraries/README.md).
- [32 library source experiments](libraries/EXPERIMENTS.md) with independent expected outputs (unverified).
- [90 design pattern briefs](patterns/README.md), now each with independent `example.ores` and `expected.stdout`.
- [Pattern runner](patterns/EXECUTING.md) and [source harness](patterns/run_examples.py).
- [Six integrated project plans](projects/README.md).
- [Fifteen language capabilities](validation/language-capabilities.md), [verification contracts](validation/README.md), and [roadmap](roadmap.md).

## Evidence maturity

**planned** = specification; **prototype** = source but no recorded passing toolchain run; **compiles** = exact compiler result; **runtime-verified** = actual executed checks; **formally-verified** = machine-checked proof with assumptions.

The original 70 have a pinned Java guest run. Patterns 71–80 passed pinned Java static parsing/type/ownership [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766), but have no documented guest execution; the 10 additional examples (81–90) also passed [pinned Java static checking](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38930550819). Full 90-example Java guest or LLVM parity is not established. Advanced concurrency and lifetime examples may only demonstrate sequential models; read their comments/README for missing proof obligations.
