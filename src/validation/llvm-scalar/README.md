# LLVM scalar smoke tests

Six native scalar source programs intentionally use LLVM's restricted source subset. Each expected exit status is 42, with empty stdout/stderr.

Run:

```sh
python3 src/validation/llvm-scalar/run_native.py --compiler /path/to/oreslang-llvmc --clang clang --compiler-revision FULL_40_HEX_SHA --compiler-checkout /path/to/oreslang-source.llvm --report llvm.json
```

The optional --compiler-checkout checks HEAD and tracked Git cleanliness; it cannot attest that a given executable was built from those sources. The driver additionally validates source SHA-256 before and after execution, rejects unexpected native stdout and stderr, and fails closed if evidence cannot be written.

Run Python driver tests:

```sh
python3 -m unittest discover -s src/validation/llvm-scalar -p test_run_native.py -v
```

The driver tests mock a compiler and test failures. One self-test uses genuine Clang on deliberately synthetic IR. This **does not establish Oreslang compilation or LLVM language parity**. A real pinned LLVM compiler run remains required.
