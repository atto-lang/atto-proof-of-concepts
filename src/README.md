# AttoLang proof-of-concepts: source workspace

- [60 proposed libraries](libraries/README.md).
- [32 library source experiments](libraries/EXPERIMENTS.md) with independent expected outputs (unverified).
- [90 design pattern briefs](patterns/README.md), now each with independent `example.atto` and `expected.stdout`.
- [Pattern runner](patterns/EXECUTING.md) and [source harness](patterns/run_examples.py).
- [Six integrated project plans](projects/README.md).
- [Fifteen language capabilities](validation/language-capabilities.md), [verification contracts](validation/README.md), and [roadmap](roadmap.md).

## Evidence maturity

**planned** = specification; **prototype** = source but no recorded passing toolchain run; **compiles** = exact compiler result; **runtime-verified** = actual executed checks; **formally-verified** = machine-checked proof with assumptions.

The original 70 have a historical pinned Java guest run. New patterns 71–90 now have [20/20 pinned Java/GraalVM guest checks and exact-output executions](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38932192949), against source `5a72cb9fa6c16808396c4e922e7110fa016c570e` and Java runtime `230258a2f500e26547009f6a947a9f584522de32`. These are two independent pinned cohorts, not a single 90/90 same-revision run. LLVM backend parity and adversarial concurrency/liveness safety remain unverified.

## Current AttoLang extension policy

All checked-in guest examples are `*.atto`; `.ores` is historical only. The Python/Rust catalog gates reject legacy source paths. No fresh compiler/guest result has been obtained for this migrated branch; see the root migration status before relying on earlier Java receipts.

[Latest compiler-tip AttoLang `.atto` fixtures](validation/atto-tip/README.md) are source-identity probes, not runtime passes.
