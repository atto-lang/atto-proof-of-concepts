# Library validation catalog

**60 library candidates.** Every directory includes a test/implementation brief. Presence does not imply implementation.

| # | Library | Priority | Target |
|---|---|---|---|
| 1 | [oreslang-vec](./oreslang-vec/) | P0 | Growable arrays, contiguous storage, slices, iterators |
| 2 | [oreslang-linked-queue](./oreslang-linked-queue/) | P0 | Linked FIFO with head/tail, enqueue, dequeue and bounded-key implementation |
| 3 | [oreslang-linked-list](./oreslang-linked-list/) | P0 | Singly/doubly linked node ownership and insertion/removal |
| 4 | [oreslang-deque](./oreslang-deque/) | P0 | Double-ended queue and ring-buffer storage |
| 5 | [oreslang-hashmap](./oreslang-hashmap/) | P0 | Hash map/set with generic key hashing, equality, resize |
| 6 | [oreslang-trees](./oreslang-trees/) | P0 | BST, AVL and red-black self-balancing trees |
| 7 | [oreslang-graphs](./oreslang-graphs/) | P0 | Directed/undirected graphs, shared identity, cycles, traversals |
| 8 | [oreslang-arena](./oreslang-arena/) | P0 | Regions, slot allocation and generational handles |
| 9 | [oreslang-btree](./oreslang-btree/) | P1 | B-tree/B+ tree pages, split/merge, cursors |
| 10 | [oreslang-trie](./oreslang-trie/) | P1 | Prefix/radix/Patricia tries |
| 11 | [oreslang-persistent](./oreslang-persistent/) | P1 | Persistent vectors, HAMT, immutable tree snapshots |
| 12 | [oreslang-intrusive](./oreslang-intrusive/) | P1 | Intrusive lists and embedded node links |
| 13 | [oreslang-skiplist](./oreslang-skiplist/) | P1 | Probabilistic multilevel ordered lists |
| 14 | [oreslang-interval-tree](./oreslang-interval-tree/) | P1 | Interval and segment trees with augmented metadata |
| 15 | [oreslang-rope](./oreslang-rope/) | P1 | Ropes and piece tables for large text |
| 16 | [oreslang-core](./oreslang-core/) | P0 | Option Result tuples tagged unions unwrap trap ordering |
| 17 | [oreslang-iter](./oreslang-iter/) | P0 | Generic lazy and mutable iterators |
| 18 | [oreslang-closures](./oreslang-closures/) | P0 | Lexical, escaping, recursive and mutable-capture closures |
| 19 | [oreslang-traits](./oreslang-traits/) | P0 | Traits, associated types, bounds, defaults, dispatch |
| 20 | [oreslang-interfaces](./oreslang-interfaces/) | P0 | Interfaces, multiple implementations and heterogeneous collections |
| 21 | [oreslang-classes](./oreslang-classes/) | P0 | Constructors, encapsulation, inheritance, override and final fields |
| 22 | [oreslang-parser-combinators](./oreslang-parser-combinators/) | P1 | Recursive parsers built from generic closures and combinators |
| 23 | [oreslang-ast](./oreslang-ast/) | P1 | Recursive abstract syntax trees, visitors, rewrites |
| 24 | [oreslang-interpreter](./oreslang-interpreter/) | P1 | Lexical environments, closures, recursive functions and evaluation |
| 25 | [oreslang-di](./oreslang-di/) | P1 | Dependency injection, scopes and cycle detection |
| 26 | [oreslang-ownership](./oreslang-ownership/) | P0 | Unique, shared, weak references, moves and borrowed views |
| 27 | [oreslang-gc-lab](./oreslang-gc-lab/) | P0 | Reachability, cycle collection, roots, weak references, relocation |
| 28 | [oreslang-sync](./oreslang-sync/) | P0 | Mutex, RW lock, semaphore, guards and condition variables |
| 29 | [oreslang-atomics](./oreslang-atomics/) | P0 | CAS, publication, load/store ordering and counters |
| 30 | [oreslang-channels](./oreslang-channels/) | P0 | Bounded/unbounded SPSC MPSC SPMC MPMC message passing |
| 31 | [oreslang-concurrent-queue](./oreslang-concurrent-queue/) | P0 | Lock-based and lock-free queues, ABA and reclamation |
| 32 | [oreslang-work-stealing](./oreslang-work-stealing/) | P0 | Owner push/pop and concurrent thief steal deques |
| 33 | [oreslang-actors](./oreslang-actors/) | P0 | Mailbox state isolation, control, supervision and ownership |
| 34 | [oreslang-futures](./oreslang-futures/) | P0 | Future promise await and cancel semantics |
| 35 | [oreslang-streams](./oreslang-streams/) | P1 | Async iterators, backpressure, fan-in and fan-out |
| 36 | [oreslang-stm](./oreslang-stm/) | P1 | Optimistic transactions, validation, retries |
| 37 | [oreslang-concurrent-map](./oreslang-concurrent-map/) | P1 | Sharded/resizable concurrent hash maps |
| 38 | [oreslang-cache](./oreslang-cache/) | P1 | Concurrent LRU LFU TTL eviction |
| 39 | [oreslang-scheduler](./oreslang-scheduler/) | P1 | Fair dispatch, priorities, wakeups and shutdown |
| 40 | [oreslang-structured-concurrency](./oreslang-structured-concurrency/) | P1 | Scoped task trees, cancellation and error aggregation |
| 41 | [oreslang-serialize](./oreslang-serialize/) | P1 | Generic record encoding, cycles and schema versions |
| 42 | [oreslang-json](./oreslang-json/) | P1 | Recursive JSON AST with streaming decoding |
| 43 | [oreslang-regex](./oreslang-regex/) | P1 | Regex AST, automata and execution engine |
| 44 | [oreslang-ffi](./oreslang-ffi/) | P1 | Native pointers, buffers, callbacks, pinning and safe wrappers |
| 45 | [oreslang-files](./oreslang-files/) | P1 | Nonparking file IO, descriptor lifecycle and cancellation |
| 46 | [oreslang-network](./oreslang-network/) | P1 | Sockets, async completion, partial IO, buffer ownership |
| 47 | [oreslang-http](./oreslang-http/) | P1 | Requests, responses, middleware, async handlers |
| 48 | [oreslang-sqlite](./oreslang-sqlite/) | P1 | Prepared statements, transaction handles and FFI resource scopes |
| 49 | [oreslang-kv-store](./oreslang-kv-store/) | P1 | B+ tree/LSM, WAL, snapshot and crash recovery |
| 50 | [oreslang-event-log](./oreslang-event-log/) | P1 | Append-only events, projections and deterministic replay |
| 51 | [oreslang-compiler](./oreslang-compiler/) | P1 | Symbols, recursive IR, optimization and type checking |
| 52 | [oreslang-bytecode-vm](./oreslang-bytecode-vm/) | P1 | Call frames, closure env, stack/heap roots and interpreter |
| 53 | [oreslang-dop](./oreslang-dop/) | P1 | Array of structures vs structure of arrays and packed layouts |
| 54 | [oreslang-gpu](./oreslang-gpu/) | P2 | Host-device buffers, kernel boundaries and transfer fences |
| 55 | [oreslang-browser-bridge](./oreslang-browser-bridge/) | P1 | Worker isolation, structured transfer, message cancellation |
| 56 | [oreslang-testkit](./oreslang-testkit/) | P0 | Assertions, fixtures, deterministic setup and cleanup |
| 57 | [oreslang-property](./oreslang-property/) | P0 | Property-based generators and shrinking |
| 58 | [oreslang-fuzz](./oreslang-fuzz/) | P0 | Grammar-based fuzzing, corpus persistence and replay |
| 59 | [oreslang-modelcheck](./oreslang-modelcheck/) | P0 | Bounded exhaustive schedule exploration and invariants |
| 60 | [oreslang-bench](./oreslang-bench/) | P0 | Benchmarks, allocation counts and latency percentiles |

## Evidence policy

A passing library implementation requires compiler-positive, targeted compiler-negative, runtime, property-based and cross-backend results. Do not mark planned proposals as validated.

## Source experiment coverage

32/60 directories have bounded prototype examples and output oracles. See [EXPERIMENTS.md](EXPERIMENTS.md); compilation, memory safety, and Java/LLVM backend parity are **not** established.
