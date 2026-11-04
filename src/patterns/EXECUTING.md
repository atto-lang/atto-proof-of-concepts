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

## Fail-closed harness hardening (2026-10-30 candidate)

The pattern runner shares the **POSIX-only bounded process-group executor** and
fixture fingerprint/atomic JSON receipt primitives with the library runner.
It pins **all** pattern source/oracle file identities and SHA-256 digests before
the first command (including unselected patterns), refuses symlinked numbered
directories and fixture symlinks, rechecks each selected input before its
invocation, and rejects retroactive/unselected changes at the end.

Use --max-output-bytes 65536 (default, per stream; max 16 MiB) and a finite
--timeout. Reaching the limit or timeout terminates the non-detached runner
process group, not just the parent shell. Guest runtime stderr fails by default;
--allow-stderr is an explicit waiver. Compile mode can emit bounded compiler
diagnostics but proves exit status only.

A JSON --report is written via a temporary file plus atomic rename, and
cannot alias the source/oracle fixtures at admission. Evidence records a
SHA-256 digest of the runner argv template instead of the unredacted
command, so avoid supplying secrets on command lines altogether.
catalog_inputs_unchanged, complete_catalog, output_oracle_matched,
byte counts and truncation flags describe what was actually checked.

**Limits:** this is not a toolchain sandbox, signature verification, LLVM
execution, formal proof, isolation against intentionally detached children,
or protection against a malicious process controlling the filesystem.
Compiler identity and full guest execution require independently verified
Git source/object and executable provenance. An incomplete/filtered, compiler
only, or zero-step CI run is not a passing native Oreslang qualification.

Run the contract regression suite after every harness change:
- python3 -m unittest discover -s src/patterns -p test_run_examples.py -v
- python3 src/patterns/run_examples.py --list

## Current status and limitations

- The original 70 patterns at Java revision 43edad9 have a funded exact-source 70/70 Java check-and-run result [run #38341093687](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) on the pinned historical PoC revision. LLVM execution is not yet verified.
- 23 GoF + 27 enterprise/concurrency + 20 advanced + 20 reliability/distributed-systems/application/messaging/storage examples. Patterns 71–80 have pinned Java parser/type/ownership [static PASS](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) but no guest run. Patterns 81–90 now also have pinned Java parser/type/ownership [PASS](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38931053661); 7/7 targeted compile-negative probes passed.
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

The pinned historic 70/70 Java guest result remains unchanged. Subsequent static and guest verification for 71–90 is recorded below.

## Funded private static compiler carrier (71–80)

The [Scintilla carrier run #38929258766](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38929258766) assigned a real hosted runner and passed SHA-verification of 11 pinned Java lexer/parser/type/ownership source blobs and 20 new pattern source/oracle blobs, compiled these checkers on Java 25, parsed 10 programs, and type/ownership-checked 10 programs. It did **not** build/run the full Oreslang guest runtime. This verifies 71–80 **only**, not the new 81–90 sources or full backend parity.

## Full new-pattern Java static/negative gate (71–90)

[Funded exact-source CI run #38931053661](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38931053661) ran on `scintilla-run-test/gleam-runner-conformance` in a **private temporary mirror**, with no cross-organization checkout token: 59/59 Git blob identities (11 pinned Java compiler/parser/type-checker source files, 40 native source/oracle files, and 8 negative-test files including the Java probe); 20/20 parse; 20/20 type/ownership; 7/7 invalid programs rejected with targeted diagnostics. This is **static compiler-checker verification**, not native guest execution. Source pattern 85 originally failed due to reserved identifier `from` in [prior failed run](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38930125229), was renamed, and then passed. The donor carrier branch is test-only and must not be merged.

**Latest exact-source rerun after lease hardening:** [run #38931053661](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38931053661) pinned 59/59 exact Git blobs and reported `PARSER_SUMMARY passed=20 failed=0`, `TYPE_SUMMARY passed=20 failed=0`, and `NEGATIVE_SUMMARY passed=7 failed=0`. This run includes the integer-domain and invalid-holder-clock-poisoning fixes to pattern 82. It still does not run guest programs.

## Funded Java/GraalVM guest execution (new patterns 71–90)

[CI run #38932192949](https://github.com/scintilla-run-test/gleam-runner-conformance/actions/runs/38932192949) executed in a private test-only Scintilla carrier using a hosted GraalVM JDK 25 runner. All **51 compiler/pattern Git objects** and **81 Java runtime/build Git objects** were verified against pinned mirror manifests. The tested Oreslang source revision was `5a72cb9fa6c16808396c4e922e7110fa016c570e`, with Java runtime revision `230258a2f500e26547009f6a947a9f584522de32`. The mirrored Java runtime built successfully, then all new programs passed **20/20 parser**, **20/20 type/ownership**, **20/20 actual launcher `--check`**, and **20/20 guest executions** (exit 0, exact expected stdout). Detailed job logs and runtime JSON results are preserved by the workflow.

The historical 70/70 Java guest pass is **separate** and used different pinned compiler/source revisions; do not describe this as a single same-revision 90/90 test. Sample executions do not demonstrate full distributed consistency, linearizability, crash resilience, liveness, or LLVM/NET/WASM/Forge parity. The private test branch is not for merge.
