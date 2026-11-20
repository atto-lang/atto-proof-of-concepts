#!/usr/bin/env bash
# Exact-tree Java/GraalVM qualification for library PoCs. Not an LLVM gate.
# Usage: run_java_guest_gate.sh JAVA_SOURCE_DIR EXPECTED_JAVA_TREE EXPECTED_POC_TREE JAVA_ORIGIN_COMMIT EVIDENCE_DIR
set -euo pipefail
if (( $# != 5 )); then
  echo 'usage: run_java_guest_gate.sh JAVA_SOURCE_DIR JAVA_TREE POC_TREE JAVA_ORIGIN_COMMIT EVIDENCE_DIR' >&2
  exit 2
fi
java_source=$(cd -- "$1" && pwd -P) || { echo "Java source directory not found" >&2; exit 2; }
expected_java_tree=$2
expected_poc_tree=$3
java_origin_commit=${4,,}
evidence=$5
if [[ ! "$java_origin_commit" =~ ^[a-f0-9]{40}$ ]]; then
  echo 'Java origin commit label must be full SHA' >&2; exit 2
fi
poc_source=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
validator="$(dirname -- "${BASH_SOURCE[0]}")/verify_source_tree.sh"
"$validator" "$poc_source" "$expected_poc_tree"
"$validator" "$java_source" "$expected_java_tree"
if [[ ! -f "$java_source/pom.xml" ]]; then
  echo 'missing pinned Java Maven pom.xml' >&2; exit 2
fi
command -v realpath >/dev/null || { echo 'realpath is required' >&2; exit 2; }
# Reject protected paths before mkdir can create files within source.
evidence=$(realpath -m -- "$evidence")
check_evidence_path() {
  local meta source
  if [[ "$evidence" == "$poc_source" || "$evidence" == "$poc_source"/* ||
        "$evidence" == "$java_source" || "$evidence" == "$java_source"/* ]]; then
    echo 'evidence must be outside protected source trees' >&2; exit 2
  fi
  # A funded CI mirror may store a source subtree inside a larger worktree.
  # Protect that *outer* worktree's Git database as well as both source roots.
  for source in "$poc_source" "$java_source"; do
    meta=$(git -C "$source" rev-parse --absolute-git-dir) || {
      echo 'cannot identify Git metadata for source checkout' >&2; exit 2;
    }
    meta=$(realpath -m -- "$meta")
    if [[ "$evidence" == "$meta" || "$evidence" == "$meta"/* ]]; then
      echo 'evidence must be outside Git metadata' >&2; exit 2
    fi
  done
}
check_evidence_path
mkdir -p -- "$evidence"
evidence=$(cd -- "$evidence" && pwd -P)
check_evidence_path
# Fail closed on stale or mixed evidence from an earlier build.
if [[ -n "$(find "$evidence" -mindepth 1 -print -quit)" ]]; then
  echo 'evidence directory must be empty before a new qualification' >&2; exit 2
fi
command -v mvn >/dev/null || { echo 'mvn is required' >&2; exit 2; }
command -v java >/dev/null || { echo 'java is required' >&2; exit 2; }
command -v python3 >/dev/null || { echo 'python3 is required' >&2; exit 2; }
java_bin=$(command -v java)
{
  echo "POC_TREE=${expected_poc_tree,,}"
  echo "JAVA_TREE=${expected_java_tree,,}"
  echo "JAVA_COMMIT_LABEL=$java_origin_commit"
  echo "JAVA_BINARY=$java_bin"
  command -v sha256sum >/dev/null && sha256sum -- "$java_bin" || true
  java -version 2>&1
  mvn -version
} > "$evidence/provenance.txt"
# Build only from a previously identity-verified checkout, and record the
# actual dependency classpath rather than guessing a fat JAR exists.
mvn -B -ntp -q -f "$java_source/pom.xml" -DskipTests package \
  dependency:build-classpath "-Dmdep.outputFile=$evidence/java-dependencies.classpath"
if [[ ! -f "$java_source/target/classes/module-info.class" ||
      ! -f "$evidence/java-dependencies.classpath" ]]; then
  echo 'Maven did not produce expected modular Java compiler artifacts' >&2; exit 1
fi
# Permit only generated Java target/ AFTER strict source admission and build.
"$validator" "$poc_source" "$expected_poc_tree"
"$validator" "$java_source" "$expected_java_tree" --allow-generated-target
classpath="$java_source/target/classes:$(cat "$evidence/java-dependencies.classpath")"
# shlex-safe command for the library harness. {source} is the ONLY substitution
# and the harness invokes argv directly without a shell.
# Oreslang is a named JPMS module, not an unnamed-classpath application.
# Match the upstream Java CI launcher contract exactly.
printf -v prefix '%q ' "$java_bin" --enable-native-access=org.graalvm.truffle,dev.oreslang,ALL-UNNAMED \
  -p "$classpath" -m dev.oreslang/dev.oreslang.launcher.OresMain
python3 "$poc_source/src/libraries/check_prototypes.py" \
  --runner-command "${prefix} --check {source}" \
  --mode compile --backend java-graalvm-check \
  --compiler-revision "$java_origin_commit" --require-revision \
  --report "$evidence/java-compile.json"
python3 "$poc_source/src/libraries/check_prototypes.py" \
  --runner-command "${prefix} {source}" \
  --mode run --backend java-graalvm-jvm \
  --compiler-revision "$java_origin_commit" --require-revision \
  --report "$evidence/java-runtime.json"
# Validate full-catalog count and both reports. The library runner is still a
# caller-controlled process harness; source and executable identity must be
# read from provenance artifacts rather than inferred from stdout alone.
python3 - "$evidence/java-compile.json" "$evidence/java-runtime.json" <<'PY'
import json, sys
for path, mode in zip(sys.argv[1:], ('compile', 'run')):
    with open(path, encoding='utf-8') as f:
        report = json.load(f)
    assert report['mode'] == mode, (path, 'mode mismatch')
    assert report['selected'] == 32 and report['inventory_total'] == 32, (path, 'incomplete inventory')
    assert report['complete_catalog'] and report['catalog_inputs_unchanged'], (path, 'dirty catalog')
    assert len(report['results']) == 32 and all(x['success'] for x in report['results']), (path, 'failure')
    if mode == 'run':
        assert report['output_oracle_matched'], (path, 'stdout mismatch')
    print('PASS pinned Java library gate:', mode, len(report['results']))
PY
# Catch compiler and source mutation after both modes have executed.
"$validator" "$poc_source" "$expected_poc_tree"
"$validator" "$java_source" "$expected_java_tree" --allow-generated-target
