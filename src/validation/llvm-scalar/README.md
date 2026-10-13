# LLVM scalar source baseline

Six small source files intentionally restrict themselves to the documented LLVM source compiler subset (typed integer functions, calls, unary/binary operators and optional module). Each should exit with code **42** after LLVM IR generation and Clang linking.

From a machine with a built compiler and Clang:

```sh
python3 src/validation/llvm-scalar/run_native.py \
  --compiler /path/to/oreslang-source.llvm/build/oreslang-llvmc \
  --clang clang \
  --compiler-revision FULL_40_CHARACTER_LLVM_COMMIT_SHA \
  --report llvm-scalar-results.json
```

The driver fails closed on compiler errors, empty IR, Clang failure, execution mismatch, and timeouts. It captures individual stdout/stderr and source SHA-256 for reproducibility.

This subset does **not** prove classes, closures, actors, GC, concurrency or parity with the 70 full examples. No execution claim without a real run. `nested-calls.ores` exercises only nested calls.
