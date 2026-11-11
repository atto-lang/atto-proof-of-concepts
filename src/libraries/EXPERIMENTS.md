# Library experiments (behavioral probes, not implementations)

**32 of 60** named library directories contain `example.atto` and `expected.stdout`. A smoke/reference model is a deliberately small test of one related property, **not** a completed library. All examples are unverified on the current compiler and both backends.

- [oreslang-vec](oreslang-vec/example.atto) — Growable vector index preservation
- [oreslang-linked-list](oreslang-linked-list/example.atto) — Index-linked traversal and unlink
- [oreslang-deque](oreslang-deque/example.atto) — Wrap-around FIFO reference
- [oreslang-hashmap](oreslang-hashmap/example.atto) — Open addressing with colliding integer keys
- [oreslang-trees](oreslang-trees/example.atto) — Indexed binary-search tree lookup
- [oreslang-graphs](oreslang-graphs/example.atto) — Cycle-safe breadth-first exploration
- [oreslang-arena](oreslang-arena/example.atto) — Generational handle invalidation reference
- [oreslang-btree](oreslang-btree/example.atto) — B-tree page split separator ordering
- [oreslang-trie](oreslang-trie/example.atto) — Digit trie single-path exact match
- [oreslang-persistent](oreslang-persistent/example.atto) — Immutable snapshot reference after in-place source update
- [oreslang-interval-tree](oreslang-interval-tree/example.atto) — Augmented max endpoint and interval overlaps baseline
- [oreslang-iter](oreslang-iter/example.atto) — Deterministic filter-map-reduce oracle
- [oreslang-closures](oreslang-closures/example.atto) — Composition of first-class functions
- [oreslang-parser-combinators](oreslang-parser-combinators/example.atto) — Numeric token parser with consumption tracking
- [oreslang-ast](oreslang-ast/example.atto) — Postorder arithmetic tree evaluation
- [oreslang-interpreter](oreslang-interpreter/example.atto) — Stack-based arithmetic evaluator model
- [oreslang-di](oreslang-di/example.atto) — Service replacement through function injection
- [oreslang-cache](oreslang-cache/example.atto) — LRU victim after touch event
- [oreslang-serialize](oreslang-serialize/example.atto) — Fixed-width integer record version round-trip
- [oreslang-regex](oreslang-regex/example.atto) — DFA matching numeric token sequence 1 2* 3
- [oreslang-event-log](oreslang-event-log/example.atto) — Deterministic append-only event replay
- [oreslang-compiler](oreslang-compiler/example.atto) — Constant folding correctness oracle
- [oreslang-bytecode-vm](oreslang-bytecode-vm/example.atto) — Stack VM sequential ADD and MUL instruction model
- [oreslang-dop](oreslang-dop/example.atto) — Structure-of-arrays reduction
- [oreslang-property](oreslang-property/example.atto) — Exhaustive bounded sum formula check
- [oreslang-fuzz](oreslang-fuzz/example.atto) — Deterministic parser seed replay
- [oreslang-modelcheck](oreslang-modelcheck/example.atto) — Two bounded serial schedules preserve commutative total
- [oreslang-bench](oreslang-bench/example.atto) — Sorted measurement median and maximum oracle
- [oreslang-scheduler](oreslang-scheduler/example.atto) — Round-robin distribution under twelve dispatches
- [oreslang-work-stealing](oreslang-work-stealing/example.atto) — Sequential owner pop and thief steal reference
- [oreslang-channels](oreslang-channels/example.atto) — Bounded native channel send-receive FIFO smoke
- [oreslang-testkit](oreslang-testkit/example.atto) — Three independent assertion conditions

## Execute deliberately

Run `python3 src/libraries/check_prototypes.py --list` to check source/oracle structure **only**. An execution runner must use a real compiler and compare exact stdout and exit code. Source files must execute independently. No green structural CI should be presented as evidence of compiler support, AOT, zero-GC, thread safety, or memory/lifetime soundness.

Complete library work still needs API/implementation, negative compiler cases, randomized differential/property testing, cancellation/failure injection, a real compiler checkout SHA, and Java/GraalVM + LLVM native execution records. Particularly: `graphs` traverses indexed data, `arena` models generations but does not control allocations, `persistent` models snapshots via copying, `work-stealing` and `scheduler` are sequential oracles, and `channels` is not a concurrent stress test.

### Lexical hygiene gate

Library inventory now applies the existing Java-tip conservative lexical checker to every library source. This rejects C-style `&&` / `||` operators and unterminated source strings/comments but is still **not compiler parsing**. `--list` remains explicitly structural-only.

The inventory rejects symlink library directories and symlink source/oracle fixtures. Execution mode optionally requires a full 40-character hexadecimal compiler revision via `--require-revision`; **format validation does not attest the compiler binary**.

## Targeted backend execution

Run a real compiler against the source examples by passing `--runner-command`. The command is split into argv without a shell. `--mode compile` checks only the process exit status (stdout is **not** validated); it never counts as runtime verification. The default `--mode run` requires an exact PASS oracle. Use `--filter 'oreslang-(vec|hashmap)'` for an explicit partial selection; empty matches fail, and JSON reports contain `selected`, `inventory_total`, `complete_catalog`, and the execution mode. A passing partial or compile-only run is not full library coverage. The backend and compiler-revision strings are caller assertions, not attested build identities.

Self-tests for exact stdout, compile/run separation, filter fail-closed behavior, and input mutation are Python-only; run `python3 -m unittest discover -s src/libraries -p 'test_check_prototypes.py' -v` before trusting a new runner configuration.

An `output_oracle_matched` result proves only that the caller-supplied executable returned the expected process output under the runner. It is **not an attested compiler or guest-runtime result**; a mock runner can return the same output. Bind evidence to an independently verified toolchain checkout and executable before promoting an experiment's status.

### 2026-10-13 runner integrity audit

- All fixture SHA-256 hashes are pinned **before** the first subprocess starts, including fixtures outside any `--filter` selection. An earlier runner cannot rewrite a later example and cause the rewritten bytes to become the trusted baseline.
- Every input is rehashed when execution finishes; retroactive changes to previously checked examples or modifications to unselected files fail the entire run.
- Source markers and the public entrypoint are checked against an active-code lexical mask rather than raw comments and string literals. This remains lexical hygiene, **not** parsing.
- `--max-output-bytes` (default 65,536 per stream; maximum 16 MiB) spools child output to temporary files and limits memory used for report text; oversized stdout **or** stderr fails even compile-only mode.
- Reports include `catalog_inputs_unchanged` and stream byte counts; output matching still does not attest a compiler binary.

A `--report` destination that resolves to a source/oracle fixture (including a hardlink or symlink alias, selected or not) is rejected before invoking any runner. Persist evidence outside the protected examples.

### Identity-based fail-closed admission

The execution harness now pins the source/oracle content hash *and* regular-file identity (device, inode and mode), not just bytes. A replaced, symlinked or chmod-modified fixture is rejected even if its text is identical. If an input drifts before a given invocation, the runner does not execute that case. This is protection against persistent changes between checks, **not a sandbox or cryptographic attestation against a cooperating malicious runner**.

### Bounded subprocess execution

The runner uses POSIX process groups and nonblocking pipes to enforce stdout/stderr limits **while a process is running**, rather than after accumulating unbounded temporary files. Output exceeding the limit causes process-group termination. Timeouts also terminate the process group, including non-detached children. This is **not** a sandbox against intentionally detached processes, privilege changes, or hostile toolchains. In `--mode run`, stderr must be empty unless `--allow-stderr` is explicitly specified; compile-only mode still accepts compiler diagnostic stderr, subject to byte limits.

### Atomic evidence publication

JSON reports are written to a freshly created temporary file in the target directory, flushed, synced, then atomically renamed over the destination. A subprocess-created late symlink/hardlink at the report pathname cannot redirect file writes into the source/oracle; the destination directory entry is replaced rather than followed. This is not a secure sandbox against a malicious actor that controls the entire filesystem hierarchy.

## Exact-source Java/GraalVM guest gate

`src/validation/run_java_guest_gate.sh` executes the full 32-probe Java compilation and JVM guest-output qualification **when both private source directories are already available in an authorized checkout**. It accepts five arguments, in order: the Java compiler source directory, expected Java Git **tree SHA**, expected PoC Git **tree SHA**, original Java commit SHA (provenance label), and a dedicated evidence directory outside both source trees.

The gate first verifies the actual checked-out Git tree object of each source directory (including when mirrored into a subdirectory of a funded test repo). It rejects wrong tree identities, changed tracked files, staged modifications, and unexpected untracked files. It then builds the Java compiler using Maven, constructs an explicit `target/classes` plus dependency classpath, runs all 32 examples through the Java launcher `--check`, executes them again as JVM guests with exact output oracles, validates both complete JSON reports, and re-verifies source integrity. Reports and Java/JDK/Maven provenance are written outside the source tree.

A matching Git tree is necessary evidence of source identity, **not** evidence of a successful compile, a trusted binary, permission-safe secret transfer, Java/LLVM parity, or correct actor semantics. The commit label supplied to the gate is not independently attested by a mirror. Run the actual gate only on an authorized checkout with real Java/JDK 25 and Maven. The eight local Git unit tests in `src/validation/test_verify_source_tree.py` exercise the admission verifier, **not** the guest compiler. The source-org Actions budget is still preventing those source workflows from starting.

The Java entrypoint is a named JPMS module. The gate invokes `java --enable-native-access=ALL-UNNAMED -p CLASSPATH -m dev.oreslang/dev.oreslang.launcher.OresMain`, matching the upstream Java CI; an ordinary `-cp` main-class launch is **not** equivalent and was corrected before any guest pass was claimed.

### Exact-tree admission hardening: ignored files and index flags

The verifier now checks physical Git blob hashes and executable modes for every tracked source file. It fails on Git-ignored contamination as well as ordinary untracked files, and does not trust `assume-unchanged` or `skip-worktree` index flags. Tracked source symlinks/submodules are rejected. The **optional** `--allow-generated-target` is only used after a strict clean-source gate and Maven build; it permits the Java compiler's ignored `target/` directory and no other ignored/untracked source paths. The Java evidence directory is resolved and checked for source-tree aliasing **before** creation. These guards constrain evidence provenance but do not sandbox an untrusted Maven build or attest an independently supplied Java origin commit.

Java gate preflight tests (`src/validation/test_java_guest_gate.py`) now reject evidence paths inside either source tree, including paths resolving through symlinks, **before creating directories**; a bad expected source tree is similarly rejected before evidence creation. These are real local Git fixture tests, not compiler executions.

The Java gate additionally refuses **nonempty evidence directories**, preventing stale reports being reused, and rejects evidence paths inside either source checkout's Git metadata directory (including a linked worktree or outer funded mirror). Both checks run before Maven or source compilation.
