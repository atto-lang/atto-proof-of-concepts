# Rust catalog structural gate (no Oreslang guest execution)

Zero third-party crates, no shell invocation, no compiler execution, no network.
This implements the 60-library / 90-pattern / 32-probe baseline and the paired
fixture/oracle and symlink admission rules in the Python hardening PR #16.

Run from the repository root:

```sh
cargo test --manifest-path tools/catalog-gate/Cargo.toml --offline --locked
cargo run --manifest-path tools/catalog-gate/Cargo.toml --offline --locked -- --root src
```

The gate checks **catalog layout and static oracle bytes only**. It never
compiles or executes `.atto` files and must not be represented as evidence of
Java/GraalVM, LLVM, isolation, channels, or concurrency semantics.

This crate is intentionally separate from existing Python scripts while Rust
replacement tests are verified. Once PR #16 lands, compare both validators
against the same full catalog and adversarial fixtures before deleting any
Python validator or changing required CI gates. Counts are code constants for
release admission, not attacker-selectable CLI flags.
