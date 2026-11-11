# Actual Java actor runtime validation (additional to pattern 39)

The original `example.atto` is a sequential reference model. These **additional**
fixtures spawn actual Oreslang actors, await readiness/completion, and verify
observable output:

- `actor-isolation.atto`: two actor instances increment distinct actor-owned
  counters and independently return `1|1`.
- `actor-turn-exclusivity.atto`: two queued messages and an explicit
  `rt cooperate` verify the first receive turn resumes before the second.

Run `python3 src/patterns/run_actor_runtime.py` from the build/test mirror
root after the Java compiler is built and the runtime dependency classpath
has been generated. A passing sample is not proof of strict mailbox
linearizability, supervisor panic routing, physical actor heap isolation,
bounded scheduler fairness, or LLVM/AOT parity. These require separate tests.

## Verified Java execution

The exact six proof/harness Git blobs in PoC commit
`2bb22316c8d43d08c8e4851b6bcd33a63bdf9251` match private funded
test-host commit `6a399d817d8a04ee09f8a8e525c1f1e39c867139`
byte-for-byte. The host ran the Java/GraalVM launcher against both actor
fixtures and exact stdout oracles: **2/2 passed**, alongside 70/70 existing
pattern guest executions, in
[funded CI #38342677493](https://github.com/agent-pontifex/agent-pontifex-daemon/actions/runs/38342677493).
The mirrored Java compiler source at that run was revision
`0452ead01d82ba235f7348b2f71c3fcb1c8b9c5a`.

The overall funded run was red because its separate full-JUnit job exposed
two unrelated legacy division-error tests while the language's numeric
soundness bug was being fixed in Java PR #806. Both actor runtime tests and
the existing 70-program runtime job **passed**. The numeric test repair is
tracked independently; do not interpret the red aggregate as a failed actor
execution.
