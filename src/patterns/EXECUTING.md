# Executable pattern prototypes

All 70 numbered folders now contain an independently executable-intent native Oreslang `example.ores` plus an `expected.stdout` oracle, and each README links those files. They exercise representative behaviors; the complex concurrency/ownership cases are **sequential reference models**, not safe complete production implementations or formal proofs.

## Structural check

```sh
python3 src/patterns/run_examples.py --list
```

This verifies source/oracle presence, numbering and simple structural assumptions. It marks examples **UNVERIFIED**; it is not compiler CI.

## Actual execution

```sh
python3 src/patterns/run_examples.py \
  --runner-command 'oreslang run {source}' \
  --backend graalvm \
  --report pattern-graalvm.json
```

The command is an **example placeholder**. Replace it with a working Java or LLVM compile-and-execute entrypoint. Arguments are split without a shell. The runner fails when compilation/execution exits nonzero, times out, or produces output different from the oracle. A green structural workflow never proves an Oreslang program compiled.

## Current status and limitations

- 70 source prototypes and 70 oracles, no verified Java/LLVM executions recorded.
- 23 GoF + 27 enterprise/concurrency + 20 advanced examples.
- Examples for typestate, session types, capabilities, RAII, hazard pointers, epoch reclamation, RCU, sequence locks, work stealing, actor model and nonparking I/O **do not establish their named safety properties**. They are small reference models explicitly identifying missing runtime/compiler proof obligations in comments and README files.
- Prioritize replacing models with complete algorithms and compiler-negative fixtures and testing on both Java/GraalVM and LLVM.
