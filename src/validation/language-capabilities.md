# Fifteen language capabilities and conformance gates

| # | Capability | Required property |
|---|---|---|
| 1 | Ownership and moves | Use-after-move and conflicting moves rejected |
| 2 | Borrow checking | Exclusive/shared borrow rules validated with targeted diagnostic fixtures |
| 3 | Garbage collection | Unreachable cycles reclaimed without losing reachable roots |
| 4 | Recursive data | Graphs, AST, trees and cyclic relationships represented safely |
| 5 | Closures | Lexical, escaping, owned and borrowed captures have correct lifetime |
| 6 | Generics | Containers, bounds and instantiation remain type safe |
| 7 | Traits | Associated types, constrained dispatch and defaults behave correctly |
| 8 | Interfaces | Dynamic dispatch and heterogeneous collection reference lifetimes are valid |
| 9 | Classes | Encapsulation, final fields and method dispatch are enforced |
| 10 | Product/sum types | Enums, tagged unions, tuples and exhaustive matching work |
| 11 | Concurrent memory | Memory ordering, linearizability and safe reclamation are tested |
| 12 | Actor isolation | One stateful turn at once; private state cannot escape |
| 13 | Async execution | Await, suspend, cancellation, resumption and task roots safe |
| 14 | Resources/FFI | Native handles closed deterministically and rooted across FFI |
| 15 | Backend parity | Java and LLVM portable observable semantics match |

For each capability: include at least one accepted program, one targeted rejected program where a static property is claimed, deterministic runtime edge cases, adversarial property/model checking as appropriate, and exact backend execution evidence. Compile rejection for unsupported syntax is not proof of any specific semantic rule.
