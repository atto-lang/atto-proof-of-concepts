# Rust PoC pattern runner — host-only development gate

This directory introduces a dependency-free POSIX Rust replacement for
the pattern subprocess harness, without deleting or bypassing the existing
Python implementation from PR #16. This is the next stage of issue #15.

## Intent and scope

- Discover exactly 90 numbered pattern directories and their nonempty
  executable example sources and byte-exact numbered PASS oracles.
- Pin SHA-256 plus device/inode/mode/length of all fixtures before any run;
  verify before/after selected cases and revalidate the full inventory,
  including unselected fixtures, before reporting a pass.
- User-provided executable argv uses one exact {source} placeholder;
  parsing supports single/double quotes and escapes, with no implicit shell.
- Execute each program in a dedicated POSIX process group, with a finite
  timeout, bounded concurrent stdout/stderr consumption (capacity-4 channel),
  a cap on each stream (maximum 16MiB), and group-wide SIGKILL
  on a timeout, output-limit violation, or cancellation (SIGINT/SIGTERM).
- Default execution requires zero exit, byte-exact stdout, no stderr and
  unchanged inputs. Compile mode checks only process exit, not stdout.
- Reports are atomic JSON files, refuse aliases to source/oracle fixtures,
  and store SHA-256 of the command template rather than the raw command.
- A requested compiler revision is a caller-supplied label, NOT attested.

## Commands

    cargo fmt --manifest-path tools/pattern-runner/Cargo.toml --all -- --check
    cargo clippy --manifest-path tools/pattern-runner/Cargo.toml --offline --locked --all-targets -- -D warnings
    cargo test --manifest-path tools/pattern-runner/Cargo.toml --offline --locked
    cargo run --manifest-path tools/pattern-runner/Cargo.toml --offline --locked -- --root . --list

To run an authorized, independently pinned toolchain, supply its real argv:

    cargo run --manifest-path tools/pattern-runner/Cargo.toml --offline --locked -- \
      --root . --runner-command 'oreslang run {source}' \
      --backend java-graalvm --compiler-revision FULL_40_HEX_HEAD \
      --require-revision --mode run --timeout 40 --max-output-bytes 65536 \
      --report ./pattern-rust-receipt.json

This is illustrative only. No working compiler or guest execution is implied.

## Known limitations / migration not complete

- The existing Python --filter accepts arbitrary regular expressions.
  This Rust version supports only literal --filter-prefix; --filter fails
  closed rather than changing semantics. Keep Python until parity is verified.
- The lexical entrypoint/braces/PASS/FAIL check is structural only, not a
  parser or proof that assertions are executable.
- POSIX process groups are not a sandbox. Untrusted compilers may spawn
  detached descendants or modify arbitrary files. Only run authorized
  compiler binaries on trusted isolated hosts.
- Large fixtures (>4MiB), symlinks and nonregular files fail closed.
  Reports may include stdout/stderr and must be treated as sensitive.
- Rust host tests (including synthetic sh children) cannot prove native
  Oreslang, Java/LLVM parity, scheduler safety or liveness.
- The CI workflow is admission-gated: steps=[] means NOT_EXECUTED.

Keep this draft until format, lint, tests, inventory and Python-equivalent
negative checks pass at exact authorized source head/tree.
