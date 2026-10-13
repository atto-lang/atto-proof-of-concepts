# Executable pattern prototypes

All 70 numbered folders now contain an independently executable-intent native Oreslang `example.ores` plus an `expected.stdout` oracle, and each README links those files. They exercise representative behaviors; the complex concurrency/ownership cases are **sequential reference models**, not safe complete production implementations or formal proofs.

## Structural check

```sh
python3 src/patterns/run_examples.py --list
```

This verifies source/oracle presence, numbering and simple structural assumptions. It marks examples **UNVERIFIED**; it is not compiler CI. Omitting `--runner-command` is now a failure unless `--list` was explicitly requested. Combining `--list` with a runner is an error, not a silent skip.

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

- Java revision 43edad9 has a funded exact-source 70/70 Java check-and-run result [run #38341093687](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) on the pinned historical PoC revision. LLVM execution is not yet verified.
- 23 GoF + 27 enterprise/concurrency + 20 advanced examples.
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
