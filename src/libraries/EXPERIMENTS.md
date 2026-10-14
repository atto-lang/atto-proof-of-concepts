# Library experiments (behavioral probes, not implementations)

**32 of 60** named library directories contain `example.ores` and `expected.stdout`. A smoke/reference model is a deliberately small test of one related property, **not** a completed library. All examples are unverified on the current compiler and both backends.

- [oreslang-vec](oreslang-vec/example.ores) — Growable vector index preservation
- [oreslang-linked-list](oreslang-linked-list/example.ores) — Index-linked traversal and unlink
- [oreslang-deque](oreslang-deque/example.ores) — Wrap-around FIFO reference
- [oreslang-hashmap](oreslang-hashmap/example.ores) — Open addressing with colliding integer keys
- [oreslang-trees](oreslang-trees/example.ores) — Indexed binary-search tree lookup
- [oreslang-graphs](oreslang-graphs/example.ores) — Cycle-safe breadth-first exploration
- [oreslang-arena](oreslang-arena/example.ores) — Generational handle invalidation reference
- [oreslang-btree](oreslang-btree/example.ores) — B-tree page split separator ordering
- [oreslang-trie](oreslang-trie/example.ores) — Digit trie single-path exact match
- [oreslang-persistent](oreslang-persistent/example.ores) — Immutable snapshot reference after in-place source update
- [oreslang-interval-tree](oreslang-interval-tree/example.ores) — Augmented max endpoint and interval overlaps baseline
- [oreslang-iter](oreslang-iter/example.ores) — Deterministic filter-map-reduce oracle
- [oreslang-closures](oreslang-closures/example.ores) — Composition of first-class functions
- [oreslang-parser-combinators](oreslang-parser-combinators/example.ores) — Numeric token parser with consumption tracking
- [oreslang-ast](oreslang-ast/example.ores) — Postorder arithmetic tree evaluation
- [oreslang-interpreter](oreslang-interpreter/example.ores) — Stack-based arithmetic evaluator model
- [oreslang-di](oreslang-di/example.ores) — Service replacement through function injection
- [oreslang-cache](oreslang-cache/example.ores) — LRU victim after touch event
- [oreslang-serialize](oreslang-serialize/example.ores) — Fixed-width integer record version round-trip
- [oreslang-regex](oreslang-regex/example.ores) — DFA matching numeric token sequence 1 2* 3
- [oreslang-event-log](oreslang-event-log/example.ores) — Deterministic append-only event replay
- [oreslang-compiler](oreslang-compiler/example.ores) — Constant folding correctness oracle
- [oreslang-bytecode-vm](oreslang-bytecode-vm/example.ores) — Stack VM sequential ADD and MUL instruction model
- [oreslang-dop](oreslang-dop/example.ores) — Structure-of-arrays reduction
- [oreslang-property](oreslang-property/example.ores) — Exhaustive bounded sum formula check
- [oreslang-fuzz](oreslang-fuzz/example.ores) — Deterministic parser seed replay
- [oreslang-modelcheck](oreslang-modelcheck/example.ores) — Two bounded serial schedules preserve commutative total
- [oreslang-bench](oreslang-bench/example.ores) — Sorted measurement median and maximum oracle
- [oreslang-scheduler](oreslang-scheduler/example.ores) — Round-robin distribution under twelve dispatches
- [oreslang-work-stealing](oreslang-work-stealing/example.ores) — Sequential owner pop and thief steal reference
- [oreslang-channels](oreslang-channels/example.ores) — Bounded native channel send-receive FIFO smoke
- [oreslang-testkit](oreslang-testkit/example.ores) — Three independent assertion conditions

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
