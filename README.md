# AttoLang proof of concepts

**Canonical source extension:** `.atto` (repository name is retained for Git history and links).

## Migration status — November 10, 2026

All 149 checked-in guest-source files were moved from `.ores` to `.atto` with their Git blob SHAs preserved: 90 numbered pattern entrypoints, 32 library probes, and 27 supporting source files (multifile, actor runtime, negative and LLVM fixtures). All source/oracle data is unchanged at this stage.

This is a **file-format migration, not yet a verified compiler-tip language upgrade**. The original 70/70 and later 20/20 Java guest-execution receipts refer to historical revisions; they do **not** attest this branch. The current Java/GraalVM compiler main revision observed for follow-up qualification is `6d8eb70048eafc9a84c5aebe9c1bb06104f16e76`. Syntax drift (including operators, ownership and declarations), runtime output parity, LLVM and other AOT backend acceptance require new exact-head compiler tests. Use `python3 src/validation/check_catalog.py` for a **structural-only** check and `python3 src/patterns/run_examples.py --list` for inventory.

[Source catalog](src/README.md): 60 library briefs and **90 native AttoLang pattern examples (70 historically Java-guest-verified; 20 now also Java-guest-verified)** with individual output oracles. [Runner and evidence policy](src/patterns/EXECUTING.md). [Pinned Java runtime audit](src/patterns/COMPILER_TIP_AUDIT.md) records **70/70 real guest executions on the historical 70-example set**, which test sample outputs rather than the named patterns' full safety properties.

Patterns 71–90 have [20/20 Java/GraalVM check-and-guest-run passes](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38932192949), using pinned PoC source `5a72cb9fa6c16808396c4e922e7110fa016c570e` and Java runtime `230258a2f500e26547009f6a947a9f584522de32`. The historical 70/70 result is a separate run, not a combined same-revision 90/90 result. LLVM parity and distributed-safety proofs are still unverified. The GitHub Actions structural workflow checks file/catalog integrity only, **not** whether the AttoLang compiler or runtime can execute these programs.

[Library experiments](src/libraries/EXPERIMENTS.md): 32 deterministic source/oracle probes, currently unverified by a compiler; these are not completed libraries or native safety proofs.
