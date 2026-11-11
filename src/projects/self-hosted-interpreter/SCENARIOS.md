# Self-hosted reference interpreter: deterministic reference scenario

**Status:** reference-oracle fixture only; no AttoLang compilation or integration execution claimed.

## Scope exercised

Lexical scoping, addition, multiplication, variable lookup, and explicit unbound-name error.

## Test contract

The [scenario.json](scenario.json) is an exact test vector. Run `python3 src/projects/check_scenarios.py` from the repository root. The Python checker evaluates the independent reference state machine and asserts exact expected outputs. This is **not** a native AttoLang result; it is an oracle for forthcoming `.atto` implementations.

## Invariants and negative cases

- Lexical shadowing takes precedence over parent scope. A missing binding yields an explicit error rather than a nullable value.

## Native backend work still required

Full AttoLang parsing and grammar, closure lifetimes, effects, type checking, escaping captures, and JVM/LLVM parity.

Do not promote this project to `runtime-verified`, `formally-verified`, or `LLVM zero-GC` on the strength of these Python fixtures. Produce independent compiler-positive and targeted compiler-negative fixtures, exact-tree Java/LLVM runs, and a reproducible failure corpus first.
