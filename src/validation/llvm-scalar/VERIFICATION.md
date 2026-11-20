# LLVM scalar verification — October 12/13, 2026

The test-only verification branches copied source blobs byte-for-byte from the [PoC PR #3](https://github.com/ores-truffle-oreslang/oreslang-proof-of-concepts/pull/3). No cross-organization checkout token or source-repository credential was needed.

## Executed evidence

| Gate | Exact funded Actions run | Result |
|---|---|---|
| Python LLVM driver negative-path, timeout, provenance and synthetic-Clang self-tests | [#38343524269](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38343524269) | 13/13 passed |
| Real pinned Oreslang LLVM compiler → LLVM IR → Clang → native exit | [#38343676750](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38343676750) | 6/6 passed |
| Python pattern runner evidence/CLI contract on complete 70-pattern inventory | [#38343847995](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38343847995) | 11/11 passed, inventory 70 |
| Historical Java/GraalVM compiler and 70 guest executions | [#38341093687](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687) | 70/70 compile and run at its pinned Java/PoC revisions |

### LLVM exact-source identity

- Tested LLVM source commit: `6a11aafbfc90d6340d8bca5808e84ed15c9a8b37` (integrated PR #288 source snapshot).
- Original LLVM repository Git tree: `ff91eb5593d662e707156580e774adaa7ad9c344`.
- Verification-only donor commit: `106c5ec2ea190aad442a59ae4496ef7c6cccaa26`, with `llvm-full` tree assertion before compilation.
- The source compiler was genuinely built in the CI runner with CMake, rather than replaced by the fake compiler used in unit tests.
- The LLVM driver report says `checkout_verified: false` because the donor's `llvm-full` is a Git subtree rather than a nested checkout. The separate job-level Git tree assertion verified that subtree, but a built binary is not a cryptographic provenance attestation.
- Six fixture binaries returned `42` with empty stdout/stderr: forward call, arithmetic precedence, nested calls, unary minus, module wrapper and call composition.

### Regression found and repaired

The initial new pattern-runner revision-gate test used a string containing literal backslash+n rather than a newline; the exact-output runner correctly returned failure. The corrected PoC commit `1022af44f4068f61b766b7a75c46a5864098e78b` was mirrored and rerun. The repaired funded verification reported 11/11 Python tests passing.

## Limitations

1. The LLVM pass is a **scalar-source subset**, not compiler parity for the 70 complex Java examples.
2. The prior 70 Java runtime passes were on **different pinned source revisions**. Do not extrapolate them to every future Java tip or newer PoC file without rerunning.
3. The native CI does not prove GC correctness, actor single-execution, lock-free algorithms, hazard-pointer reclamation, hard realtime scheduling, or nonparking synchronous-looking I/O.
4. Python mock tests and synthetic IR checks are explicitly **harness self-tests**, not evidence of an Oreslang compiler accepting source.
5. The original PoC repository's Actions workflow continues reporting failures without useful job-step logs; funded donor verification is shown separately rather than mislabeling the home-org check as green.

PR #3 remains draft until reviewers decide the bounded verified scope is ready to merge or additional current-tip parity is required.
