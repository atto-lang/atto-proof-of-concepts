# Compile-fail regressions (not runnable pattern examples)

These sources are copied from the source.llvm compiler-tip fixtures at `40b4430c0bba01d4a1980270cb90457d910e4835`. They test intended semantic restrictions on ownership and actor sends:

| Fixture | Expected failure |
|---|---|
| `native-reject-take-then-reuse.ores` | Using a moved scalar after `rt take` |
| `class-double-borrow-reject.ores` | Simultaneous conflicting exclusive/shared owner borrows |
| `source-actor-send-borrow-reject.ores` | Passing a live borrowed value over an actor send boundary |

A fixture passes only when the **corresponding compiler** fails with the intended semantic diagnostic and emits no partial LLVM IR. A parse error or unsupported-feature diagnostic is not adequate proof. Source presence alone is not verification, and Java/LLVM parity is not yet established.
