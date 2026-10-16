# Oreslang proof of concepts

[Source catalog](src/README.md): 60 library briefs and **90 native Oreslang pattern examples (70 historically Java-guest-verified; 20 Java-static-verified)** with individual output oracles. [Runner and evidence policy](src/patterns/EXECUTING.md). [Pinned Java runtime audit](src/patterns/COMPILER_TIP_AUDIT.md) records **70/70 real guest executions on the historical 70-example set**, which test sample outputs rather than the named patterns' full safety properties.

Patterns 71–80 passed pinned Java parsing, type and ownership checking [CI](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766); their guest execution remains unverified. Patterns 81–90 have now also passed the funded [20/20 pinned Java parser/type/ownership + 7/7 negative CI gate](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38930550819). None of 71–90 has newly verified Java guest execution; LLVM parity is unverified. LLVM parity is unverified. The GitHub Actions structural workflow checks file/catalog integrity only, **not** whether the Oreslang compiler or runtime can execute these programs.

[Library experiments](src/libraries/EXPERIMENTS.md): 32 deterministic source/oracle probes, currently unverified by a compiler; these are not completed libraries or native safety proofs.
