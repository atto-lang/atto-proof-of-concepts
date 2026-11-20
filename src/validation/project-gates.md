# Project release gates

1. 60 library brief directories and 70 pattern brief directories exist.
2. At least the agreed core subset has real native source, tests and reproducible toolchain runs.
3. Compiler-negative tests fail for intended semantic reasons.
4. Runtime and property tests reproduce known invariants.
5. Concurrency model checks record explicit bounds and linearizability checks.
6. Java and LLVM pass the same supported programs.
7. All 70 pattern examples eventually execute with tests; **descriptions are not examples**.
8. Formal proof claims reference formal models, assumptions and machine-checked artifacts.
