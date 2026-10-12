# GC conformance matrix

Test root enumeration for registers, stack, closures, suspended tasks, actor mailboxes, FFI roots, and global state. Test reachable and unreachable self/multi-node cycles; relocating GC fixups (when moving); weak references; write barriers; mutator/collector concurrency; resource cleanup separately from GC; large churn and fragmentation. Record allocation counts and liveness observations; do not assume collection is instantaneous. On LLVM exercise the actual native heap. Do not infer native safety from JVM results.
