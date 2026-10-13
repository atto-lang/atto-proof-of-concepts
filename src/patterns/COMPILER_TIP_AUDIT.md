# Oreslang compiler tip compatibility audit — October 12, 2026

## Exact-source static validation

**Java source revision:** `43edad9e31333e1e20c8646a8a22728b586696ea`.

**Proof-of-concepts source:** branch `fix/patterns-java-tip-parser`, verified pattern and negative-fixture sources culminating in commit `228412c9ef6e3162a1900ec8ed407e18fa733feb`.

**Funded private runner:** [CI #38318787965](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38318787965) (mirror hosted in [test-only draft PR #6](https://github.com/agent-pontifex/agent-pontifex-daemon/pull/6), not for merge).

| Verification gate | Passed | Failed |
|---|---:|---:|
| Parse 70 independent `.ores` pattern examples | 70 | 0 |
| Static type, ownership and return-cleanup checks | 70 | 0 |
| Targeted compile-fail fixtures (6 semantic, 1 syntax) | 7 | 0 |

The CI uses **all 11 exact Java source files** for lexer, parser, AST, `TypeChecker`, `OwnershipChecker`, `ReturnCleanupChecker` and their direct dependencies, obtained at the same commit. The Java harness runs `Parser.parse` and `TypeChecker.check` per program. It does **not** execute Oreslang guest programs.

### Defects uncovered and corrected

- Patterns 23, 52 and 53 exported constructors on private file-root classes. Removed constructor export.
- Pattern 50 used `matches` as a function name, conflicting with contextual language syntax.
- 23 examples misclassified mutable collections or methods as read-only. Fixed using `val` mutable referents, `mut self` explicit method receivers and appropriate owned borrows.
- Pattern 37 used a moved closure twice; now borrows the callable where appropriate.
- Pattern 04 cloned by consuming the original, then attempted to use it again; fixed by borrowing the source.
- The negative suite exposed unsafe same-call aliasing. Java `main` now holds explicit call-site borrows through later argument evaluation, preventing borrow-then-move and mutable-borrow-then-move. Verified against the merged fix at `43edad9`.

### Actual Java guest execution (subsequent gate)

The full Java launcher and GraalVM runtime now **compiled/checked and actually executed all 70 examples** against their exact stdout oracles: [funded exact-source Java/GraalVM CI #38341093687](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687). The final run had **70/70 `--check`, 70/70 guest runs, 70/70 syntax/type/ownership probes, 7/7 negative probes and 10/10 Python runner contract tests**. This is a new gate beyond the original static-source results.

**Exact-source identity:** PoC source revision `a162edf0858f02b17048c33ac08dd39fc59854dc` had all 70 `example.ores` and 70 `expected.stdout` Git blobs reproduced byte-for-byte in donor test commit `cad46c4fcd06abb31707d8869b5f1ce1f352613e`. All 435 mirrored files from Java revision `43edad9e31333e1e20c8646a8a22728b586696ea` also matched their upstream Git blob SHA. No cross-organization checkout token was required. The donor test-only branch is not for merge.

The initial full execution of the older examples had **67/70 passes** in [CI #38319341132](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38319341132). Adapter (06), Facade (10) and Data Mapper (29) crashed because Java-tip's static checker inferred `int` for `int / int`, while the runtime returned `Double`. The samples now use bounded explicit integer-quotient reference functions and add negative-temperature, truncation and boundary checks. The underlying static/runtime type inconsistency is still open as [Java issue #798](https://github.com/ores-truffle-oreslang/oreslang-source.java/issues/798).

These passes prove only the stated **sample input/output behaviors**, not that the named pattern implementations are production safe, linearizable or fully implemented. See [PoC issue #6](https://github.com/ores-truffle-oreslang/oreslang-proof-of-concepts/issues/6) for the missing concurrent-safety and liveness proofs.

### Known limitations

1. **Guest runtime has limited behavioral coverage.** The 70 sample PASS markers executed, but many patterns remain simplified reference models without adversarial tests.
2. **LLVM parity is not verified.** LLVM documents a smaller supported source subset; unsupported-feature rejection is not an acceptance pass.
3. **Safety proofs are incomplete.** Actor single-execution, GC/reclamation, hazard pointers, RCU, work stealing and nonparking I/O still require scheduler/runtime validation and bounded/exhaustive models where relevant.
4. **A prototype is not necessarily a complete implementation.** Some pattern sources remain explicit sequential reference models, as recorded in [CONFORMANCE_MATRIX.md](CONFORMANCE_MATRIX.md).
5. This result pins the Java source revision. Future compiler-tip changes require a fresh run.

To inspect source and reproduce: use the pinned mirror sources and `OresSyntaxProbe.java`, `OresTypeProbe.java`, `OresNegativeProbe.java` in the private test-only PR linked above. No source-repository tokens are used by CI.

Guest execution was subsequently verified by the pinned Java launcher and exact stdout comparisons as documented above. The [run_examples.py](run_examples.py) supports independent compile-only and runtime modes and remains usable for additional Java and LLVM validation.
