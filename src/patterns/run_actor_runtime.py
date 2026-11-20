#!/usr/bin/env python3
"""Run the two real actor proofs against a built Oreslang Java launcher.

This is guest execution, not proof of OS-level isolation, scheduler fairness,
or arbitrary concurrency histories. Each case requires an exact stdout oracle.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
CASES = (
    ("actor-isolation", "1|1"),
    ("actor-turn-exclusivity", "before|after|second"),
)
CP_PATH = Path("java-source/target/runtime-classpath.txt")


def main() -> int:
    if not CP_PATH.is_file() or not Path("java-source/target/classes").is_dir():
        print("Missing built Java compiler or runtime classpath", file=sys.stderr)
        return 2
    classpath = "java-source/target/classes:" + CP_PATH.read_text(encoding="utf-8").strip()
    results = []
    for name, expected in CASES:
        source = HERE / "39-actor-model" / "runtime" / (name + ".ores")
        oracle = source.with_suffix(".stdout")
        if not source.is_file() or not oracle.is_file():
            print("Missing actor runtime source or oracle: " + name, file=sys.stderr)
            return 2
        original_source = source.read_bytes()
        original_oracle = oracle.read_bytes()
        if original_oracle != expected.encode("utf-8"):
            print("Incorrect actor oracle: " + name, file=sys.stderr)
            return 2
        command = ["java", "-cp", classpath, "dev.oreslang.launcher.OresMain", str(source)]
        start = time.monotonic()
        try:
            proc = subprocess.run(command, capture_output=True, timeout=30, check=False)
            unchanged = original_source == source.read_bytes() and original_oracle == oracle.read_bytes()
            ok = unchanged and proc.returncode == 0 and proc.stdout == original_oracle
            result = {"name": name, "success": ok, "returncode": proc.returncode,
                      "stdout": proc.stdout.decode("utf-8", "replace"),
                      "stderr": proc.stderr.decode("utf-8", "replace")[-1500:],
                      "source_sha256": hashlib.sha256(original_source).hexdigest(),
                      "oracle_sha256": hashlib.sha256(original_oracle).hexdigest(),
                      "seconds": round(time.monotonic() - start, 3)}
        except (OSError, subprocess.TimeoutExpired) as error:
            result = {"name": name, "success": False, "error": str(error)}
        results.append(result)
        print(("PASS " if result["success"] else "FAIL ") + name, flush=True)
        if not result["success"]:
            print(json.dumps(result, sort_keys=True), file=sys.stderr, flush=True)
    report = {"cases": len(results), "passed": sum(int(r["success"]) for r in results),
              "results": results, "scope": "real actor guest execution; not stress/model checking"}
    print("ACTOR_RUNTIME_SUMMARY passed=%d failed=%d total=%d" %
          (report["passed"], len(results)-report["passed"], len(results)))
    return 0 if report["passed"] == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
