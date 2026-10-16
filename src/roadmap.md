# Implementation sequence

1. **Ownership foundations**: core, vector, linked queue, linked list, arena and testkit.
2. **Recursive and polymorphic structures**: trees, graphs, hash map, traits, interfaces and AST.
3. **Closures and runtime lifetimes**: closure captures, iterators, persistent structures, GC lab and parser combinators.
4. **Concurrency**: mutexes, reader/writer locks, atomics, channels, concurrent queues, actors, futures and model checking.
5. **Systems integration**: FFI, serialization, network, KV store and bytecode VM.
6. **Design pattern catalog and self-hosting**: 78 patterns with code and tests (71–78 need compiler verification); reference interpreter and both-backend conformance.

## Twelve highest-value proof targets

1. Doubly linked list; 2. Red-black tree; 3. Cyclic graph; 4. Persistent HAMT; 5. Parser combinators with closures; 6. Recursive AST+interpreter; 7. Generational arena; 8. MPMC queue; 9. Reader/writer protected map; 10. Supervised actors; 11. Work-stealing scheduler; 12. Async HTTP server.

Passing criteria and required evidence: [verification contracts](validation/README.md), [language capabilities](validation/language-capabilities.md), [integration projects](projects/README.md).
