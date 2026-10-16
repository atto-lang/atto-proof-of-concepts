# Executable pattern prototypes

All 90 numbered folders now contain an independently executable-intent native Oreslang `example.ores` plus an `expected.stdout` oracle, and each README links those files. They exercise representative behaviors; the complex concurrency/ownership cases are **sequential reference models**, not safe complete production implementations or formal proofs.

## Structural check

```sh
python3 src/patterns/run_examples.py --list
```

This verifies source/oracle presence, numbering, rejects symlinked fixture files and checks simple structural assumptions. It marks examples **UNVERIFIED**; it is not compiler CI. Omitting `--runner-command` is now a failure unless `--list` was explicitly requested. Combining `--list` with a runner is an error, not a silent skip.

## Actual execution

```sh
python3 src/patterns/run_examples.py \
  --runner-command 'oreslang run {source}' \
  --backend graalvm \
  --report pattern-graalvm.json
```

JSON reports now bind each pattern and oracle to SHA-256 and fail if input files change during a run. `--backend` and `--compiler-revision` are user assertions, **not trusted attestation**; verify the actual checkout SHA in CI. Partial `--filter` runs are not marked as complete catalog coverage. Non-finite timeouts fail closed.

The command is an **example placeholder**. Replace it with a working Java or LLVM compile-and-execute entrypoint. Arguments are split without a shell. The runner fails when compilation/execution exits nonzero, times out, or produces output different from the oracle. A green structural workflow never proves an Oreslang program compiled.

## Current status and limitations

- The original 70 patterns at Java revision 43edad9 have a funded exact-source 70/70 Java check-and-run result [run #38341093687](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) on the pinned historical PoC revision. LLVM execution is not yet verified.
- 23 GoF + 27 enterprise/concurrency + 20 advanced + 20 reliability/distributed-systems/application/messaging/storage examples. Patterns 71–80 have pinned Java parser/type/ownership [static PASS](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) but no guest run. Patterns 81–90 are newly unverified.
- Examples for typestate, session types, capabilities, RAII, hazard pointers, epoch reclamation, RCU, sequence locks, work stealing, actor model and nonparking I/O **do not establish their named safety properties**. They are small reference models explicitly identifying missing runtime/compiler proof obligations in comments and README files.
- Prioritize replacing models with complete algorithms and compiler-negative fixtures and testing on both Java/GraalVM and LLVM.

## Tip-aligned compile-only validation

The Java tip exposes a CLI `--check` mode. Execute the `mvn exec:java` entrypoint from a checked-out `oreslang-source.java` project, not from an unrelated project without that Maven configuration:

```sh
python3 src/patterns/run_examples.py \
  --mode compile --backend graalvm \
  --compiler-revision 62e591e5639eac9cbbb36415eb0bf3fc9b68831b \
  --runner-command 'mvn -q -ntp -f /path/to/oreslang-source.java/pom.xml -DskipTests exec:java "-Dexec.args=--check {source}"' \
  --report java-tip-compile.json
```

**Compile mode** only verifies exit status and must never be counted as a passing runtime behavior assertion. For a runtime run, omit `--mode compile` and supply a working CLI that returns exact stdout. The [tip audit](COMPILER_TIP_AUDIT.md) records compiler SHAs and unsupported LLVM features.

Run the Python-only grammar hygiene check with:

```sh
python3 src/patterns/tip_syntax_hygiene.py
python3 -m unittest discover -s src/patterns -p 'test_tip_syntax_hygiene.py'
```

## Optional strict compiler revision syntax

`--require-revision` rejects unknown or abbreviated `--compiler-revision` values, but SHA format is **not proof** the supplied binary was built from that commit. Always verify the checkout and binary independently. This flag does not replace the previously implemented per-source/per-oracle hashing and change detection.

## October 16, 2026 private CI-carrier attempts (patterns 71–80)

Source PR #11 tip `246d685fdc436c743a965f4349516b82af99bfe0` has 10 new programs and exact output oracles. A private mirror copied **20/20 native-source/oracle Git blobs byte-for-byte** to the user-accessible private [agent-pontifex CI-only PR #26](https://github.com/agent-pontifex/agent-pontifex-daemon/pull/26). Its [workflow run #38927965493](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38927965493) failed with **zero executed steps and no assigned runner**, so no Java compilation occurred.

A second private test branch was created under [fiducia-cloud/fiducia-docs](https://github.com/fiducia-cloud/fiducia-docs/tree/test/oreslang-patterns-80-20261016): 11 pinned Java lexer/parser/type/ownership sources plus 10 Oreslang programs and 10 oracles, with an exact Git-blob manifest and Java 25 probe workflow. Its [initial run #38928536679](https://github.com/fiducia-cloud/fiducia-docs/actions/runs/38928536679) likewise failed **before runner assignment and before any steps**, despite that organization having successful workflow runs on October 15. These failures must not be labeled parser, type-checker or runtime test failures; Actions budget/billing and runner admission could not be definitively distinguished by the accessible GitHub API. The test branch is temporary and must not be merged.

The pinned historic 70/70 Java guest result remains unchanged; patterns 71–80 still have **no actual compiler/runtime evidence**.

## Funded private static compiler carrier (71–80)

The [Scintilla carrier run #38929258766](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) assigned a real hosted runner and passed SHA-verification of 11 pinned Java lexer/parser/type/ownership source blobs and 20 new pattern source/oracle blobs, compiled these checkers on Java 25, parsed 10 programs, and type/ownership-checked 10 programs. It did **not** build/run the full Oreslang guest runtime. This verifies 71–80 **only**, not the new 81–90 sources or full backend parity.
