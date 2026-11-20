# Compile-fail regression fixtures

**Java exact-tip negative suite:** seven sources under [java-tip/](java-tip/) passed against Java compiler source `43edad9e31333e1e20c8646a8a22728b586696ea` in [funded CI #38318787965](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38318787965). Each test requires failure in the intended phase with its targeted diagnostic.

| Java fixture | Required failure |
|---|---|
| `java-tip/mutability-readonly-collection.ores` | Mutation through read-only collection binding |
| `java-tip/mutability-readonly-receiver.ores` | Field mutation through read-only implicit `self` |
| `java-tip/use-after-move.ores` | Access after transfer of owned value |
| `java-tip/conflicting-borrows.ores` | Mutable and shared loans overlap inside a call |
| `java-tip/borrow-then-move-same-call.ores` | Shared call-argument loan conflicts with later move of same owner |
| `java-tip/mutborrow-then-move-same-call.ores` | Exclusive call-argument loan conflicts with later move |
| `java-tip/public-constructor-private-class.ores` | Public constructor declared in private class (parser rejection) |

**LLVM-origin fixtures**, currently not verified with LLVM in this workspace: `native-reject-take-then-reuse.ores`, `class-double-borrow-reject.ores`, `source-actor-send-borrow-reject.ores` (originally from LLVM commit `40b4430c0bba01d4a1980270cb90457d910e4835`).

Important: syntax rejection does not count as evidence of type/borrow safety, and semantic rejection must match the expected diagnostic, not an unrelated unsupported-feature error.
