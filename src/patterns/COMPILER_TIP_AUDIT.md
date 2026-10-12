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

### Known limitations

1. **Guest runtime is not verified.** A static PASS does not mean PASS markers were executed.
2. **LLVM parity is not verified.** LLVM documents a smaller supported source subset; unsupported-feature rejection is not an acceptance pass.
3. **Safety proofs are incomplete.** Actor single-execution, GC/reclamation, hazard pointers, RCU, work stealing and nonparking I/O still require scheduler/runtime validation and bounded/exhaustive models where relevant.
4. **A prototype is not necessarily a complete implementation.** Some pattern sources remain explicit sequential reference models, as recorded in [CONFORMANCE_MATRIX.md](CONFORMANCE_MATRIX.md).
5. This result pins the Java source revision. Future compiler-tip changes require a fresh run.

To inspect source and reproduce: use the pinned mirror sources and `OresSyntaxProbe.java`, `OresTypeProbe.java`, `OresNegativeProbe.java` in the private test-only PR linked above. No source-repository tokens are used by CI.

For native guest execution, a future Java launcher job must run each `example.ores` and compare exit status and exact `expected.stdout` output. The existing [run_examples.py](run_examples.py) supports independent compile-only and runtime modes.
