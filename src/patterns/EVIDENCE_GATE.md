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

In `--mode compile`, **only process exit code** proves a compile check passed. Runtime output is not validated. In `--mode run`, the process must exit 0 AND stdout must exactly equal the pattern's `expected.stdout`. Results embed source and oracle SHA-256 and compiler labels. Only a verified exact source checkout and compiler binary can establish provenance; the submitted revision label is untrusted. Python runner tests use a fake subprocess and do **not** prove Oreslang compiled.

## Current blockers

The original repository GitHub Actions runs have been reporting failure with **no job steps and no accessible logs**, so runner allocation/billing/policy must be checked before claiming a real CI run. Do not relabel a zero-step failed workflow as a passed test. LLVM's limited supported source subset is not equivalent to all 70 Java-language examples.

Java validation at the pinned historic tip achieved 70/70 compile and guest execution checks in [funded run #38341093687](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38341093687). A fresh current-tip matrix is still desirable. Java's `OresMain --check` can perform compile-only validation. When compilation succeeds, test an actual run separately. Never test private code in another organization without respecting code access authorization and repository policy.
