# Compiler tip compatibility audit

Checked against these exact source revisions on October 12, 2026:

- Java/GraalVM source main: `62e591e5639eac9cbbb36415eb0bf3fc9b68831b`
  - `docs/grammar.ebnf`
  - `docs/LANGUAGE.md`
  - `src/main/java/dev/oreslang/launcher/OresMain.java`
- LLVM source main: `40b4430c0bba01d4a1980270cb90457d910e4835`
  - `docs/SOURCE_PARITY.md`
  - `README.md`
  - `tests/fixtures/`

## Confirmed corrections to prototypes

- Replaced C-style `&&` with Oreslang conditional AND (comma) or `And(...)` expression intrinsic. Do not substitute `&&` or `||` into Oreslang source.
- Normalized `if ... then` with newline body and `fi`; no legacy `if ...; do`.
- Added explicit constructors to stateful session/capability demonstration classes.
- Normalized private actor declaration to canonical `actor Name { ... }` with instance methods without `fnc`.
- The Half-Sync/Half-Async demo no longer labels an explicitly async function `read_blocking`; the nonparking synchronous-looking contract is a separate, presently unverified feature.
- Composite, Interpreter, and Visitor examples now perform nontrivial class/method/recursive dispatch.

## Support matrix

| Capability | Java main | LLVM main |
|---|---|---|
| Full source language syntax (classes, closures, arrays) | Language contract defined; examples not yet compiler-run | Not supported as a whole |
| 70 .ores stdout-based pattern programs | Not verified with latest compiler | Not supported by documented i64-only source slice |
| Scalar i64 source, simple calls, arithmetic | Expected subset; still needs testing | Supported limited subset per README, but not run here |
| Actor isolation, async, resource/GC guarantees | Needs actual implementation-specific tests | Most source features fail closed |

**Important:** The static Python hygiene checker only catches known grammar mismatches. It is not the Java parser, static type checker, LLVM compiler or proof of runtime safety.

To compile-check on the Java source checkout:

```sh
python3 src/patterns/run_examples.py --mode compile --backend graalvm \
  --compiler-revision 62e591e5639eac9cbbb36415eb0bf3fc9b68831b \
  --runner-command 'mvn -q -ntp -f /path/to/oreslang-source.java/pom.xml -DskipTests exec:java "-Dexec.args=--check {source}"' \
  --report java-tip-compile.json
```

Run-mode requires a real CLI which emits the exact PASS oracle and exits nonzero on failure, without build-system output mixed into stdout. Compilation evidence must be recorded separately from successful runtime execution.
