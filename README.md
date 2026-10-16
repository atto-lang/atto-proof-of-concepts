# Oreslang proof of concepts

[Source catalog](src/README.md): 60 library briefs and **90 native Oreslang pattern examples (70 historically Java-guest-verified; 20 now also Java-guest-verified)** with individual output oracles. [Runner and evidence policy](src/patterns/EXECUTING.md). [Pinned Java runtime audit](src/patterns/COMPILER_TIP_AUDIT.md) records **70/70 real guest executions on the historical 70-example set**, which test sample outputs rather than the named patterns' full safety properties.

Patterns 71–90 have [20/20 Java/GraalVM check-and-guest-run passes](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38932192949), using pinned PoC source `5a72cb9fa6c16808396c4e922e7110fa016c570e` and Java runtime `230258a2f500e26547009f6a947a9f584522de32`. The historical 70/70 result is a separate run, not a combined same-revision 90/90 result. LLVM parity and distributed-safety proofs are still unverified. The GitHub Actions structural workflow checks file/catalog integrity only, **not** whether the Oreslang compiler or runtime can execute these programs.

[Library experiments](src/libraries/EXPERIMENTS.md): 32 deterministic source/oracle probes, currently unverified by a compiler; these are not completed libraries or native safety proofs.
