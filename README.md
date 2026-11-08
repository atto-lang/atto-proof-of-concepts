# Oreslang proof of concepts

[Source catalog](src/README.md): 60 library briefs and **90 native Oreslang pattern examples (70 historically Java-guest-verified; 20 now also Java-guest-verified)** with individual output oracles. [Runner and evidence policy](src/patterns/EXECUTING.md). [Pinned Java runtime audit](src/patterns/COMPILER_TIP_AUDIT.md) records **70/70 real guest executions on the historical 70-example set**, which test sample outputs rather than the named patterns' full safety properties.

Patterns 71–90 have [20/20 Java/GraalVM check-and-guest-run passes](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38932192949), using pinned PoC source `5a72cb9fa6c16808396c4e922e7110fa016c570e` and Java runtime `230258a2f500e26547009f6a947a9f584522de32`. The historical 70/70 result is a separate run, not a combined same-revision 90/90 result. LLVM parity and distributed-safety proofs are still unverified. The GitHub Actions structural workflow checks file/catalog integrity only, **not** whether the Oreslang compiler or runtime can execute these programs.

[Library experiments](src/libraries/EXPERIMENTS.md): 32 deterministic source/oracle probes, currently unverified by a compiler; these are not completed libraries or native safety proofs.

## Repository ownership and migration (2026-11-08)

AttoLang is the current public language name; `ores-truffle-oreslang/oreslang-proof-of-concepts` is still the historical Oreslang repository. Preserve working `.ores` source inputs, old package names and CLI paths until compiler-backed `.atto` compatibility is established per backend.

- **Belongs here:** bounded prototypes and experimental designs with clearly stated limitations.
- **Does not belong here:** promises that prototypes are product-ready.
- **Organization boundary:** [atto-lang](https://github.com/atto-lang) should own language examples, compilers, tooling and libraries. [atto-co](https://github.com/atto-co) owns separately governed hosted deployment, production tenant infrastructure, identity, marketplace and billing. Existing same-purpose `atto-*` repositories do not establish a completed Git transfer or code parity.
- **Proposed first transfer:** `atto-lang/oreslang-proof-of-concepts` under this original repository identity/name, not an unapproved source clone or a direct move to `atto-co`. Any later managed-product carve-out needs a new governance decision.

**Preflight and cutover:** coordinate with [issue #26](https://github.com/ores-truffle-oreslang/.github/issues/26), follow private [migration proposal #25](https://github.com/ores-truffle-oreslang/.github/pull/25), obtain source/target owner and independent security approval. Record repo numeric ID, exact HEAD SHA/tree, branch/ruleset protection, original and new access, open PRs, packages, releases, Actions billing/runners, secrets, webhooks, GitHub Apps, Pages, dependency URLs and rollback plan. Do not mirror private code without authorization. After actual GitHub ownership transfer, verify unchanged ID/tree/history, restore security and run exact-head CI before consumer/CLI/import edits. `steps=[]` or `steps=null` is `NOT_EXECUTED`; host/reference checks are not proof that guest AttoLang ran.
