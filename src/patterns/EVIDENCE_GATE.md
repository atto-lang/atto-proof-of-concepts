# Real compiler evidence gate

The 70-pattern runner supports a strict evidence mode:

```sh
python3 src/patterns/run_examples.py \
  --mode compile --require-revision \
  --compiler-revision FULL_40_HEX_COMPILER_COMMIT \
  --backend java-tip \
  --runner-command 'YOUR_COMPILER_COMMAND_WITH_{source}' \
  --report java-tip-compile.json
```

In `--mode compile`, **only process exit code** proves a compile check passed. Runtime output is not validated. In `--mode run`, the process must exit 0 AND stdout must exactly equal the pattern's `expected.stdout`. Results embed source SHA-256 and compiler revision to prevent confusing a historical pass with the current source. Python runner tests use a fake subprocess and do **not** prove Oreslang compiled.

## Current blockers

GitHub Actions runs on the repository are reporting failure with **no job steps and no accessible logs**, so runner allocation/billing/policy must be checked before claiming a real CI run. Do not relabel a zero-step failed workflow as a passed test. LLVM's limited supported source subset is not equivalent to all 70 Java-language examples.

Java's current `OresMain --check` (invoked through its Maven executable launcher) is the first target. When compilation succeeds, test an actual run separately. Never test private code in another organization without respecting code access authorization and repository policy.
