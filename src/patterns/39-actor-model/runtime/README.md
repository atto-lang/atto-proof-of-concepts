# Actual Java actor runtime validation (additional to pattern 39)

The original `example.ores` is a sequential reference model. These **additional**
fixtures spawn actual Oreslang actors, await readiness/completion, and verify
observable output:

- `actor-isolation.ores`: two actor instances increment distinct actor-owned
  counters and independently return `1|1`.
- `actor-turn-exclusivity.ores`: two queued messages and an explicit
  `rt cooperate` verify the first receive turn resumes before the second.

Run `python3 src/patterns/run_actor_runtime.py` from the build/test mirror
root after the Java compiler is built and the runtime dependency classpath
has been generated. A passing sample is not proof of strict mailbox
linearizability, supervisor panic routing, physical actor heap isolation,
bounded scheduler fairness, or LLVM/AOT parity. These require separate tests.
