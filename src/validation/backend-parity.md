# Cross-backend behavioral comparison

Targets: `oreslang-source.java` (GraalVM/JVM), `oreslang-source.llvm` (native), and where supported Wasm/Browser.

Collect structured results for parse, format, compile, expected diagnostic, execution, allocation/liveness, process exit code, and sanitizer results. Compare portable observable semantics rather than implementation-specific GC timing, thread scheduling or execution time. Run on x86-64 and ARM64; only claim 32-bit where implemented.

Do not count intentional fail-closed unsupported-feature diagnostics as successful positive conformance.
