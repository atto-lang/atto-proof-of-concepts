#!/usr/bin/env bash
# Verify the Git subtree actually checked out at a directory, not an adjacent
# CI workflow or a caller-supplied commit label. A source tree may be mirrored
# below a test repository's root without changing its Git tree identity.
set -euo pipefail
if (( $# != 2 )); then
  echo 'usage: verify_source_tree.sh CHECKOUT_DIRECTORY EXPECTED_40_HEX_TREE' >&2
  exit 2
fi
checkout=$(cd -- "$1" && pwd -P)
expected=${2,,}
if [[ ! "$expected" =~ ^[a-f0-9]{40}$ ]]; then
  echo 'expected Git tree SHA must be 40 hex characters' >&2
  exit 2
fi
repo=$(git -C "$checkout" rev-parse --show-toplevel 2>/dev/null) || {
  echo "not a Git checkout: $checkout" >&2; exit 2;
}
repo=$(cd -- "$repo" && pwd -P)
if [[ "$checkout" == "$repo" ]]; then
  selector='HEAD^{tree}'
  scope='.'
else
  if [[ "$checkout" != "$repo"/* ]]; then
    echo 'checkout escapes Git worktree' >&2; exit 2
  fi
  scope=${checkout#"$repo"/}
  selector="HEAD:$scope"
fi
actual=$(git -C "$repo" rev-parse --verify "$selector" 2>/dev/null) || {
  echo "cannot resolve source tree at $scope" >&2; exit 1;
}
if [[ "$(git -C "$repo" cat-file -t "$actual")" != 'tree' ]]; then
  echo "not a Git tree at $scope" >&2; exit 1
fi
if [[ "$actual" != "$expected" ]]; then
  echo "source tree mismatch: expected=$expected actual=$actual scope=$scope" >&2
  exit 1
fi
if ! git -C "$repo" diff --quiet HEAD -- "$scope"; then
  echo "tracked source differs from committed Git tree: $scope" >&2
  exit 1
fi
if ! git -C "$repo" diff --cached --quiet HEAD -- "$scope"; then
  echo "staged source differs from committed Git tree: $scope" >&2
  exit 1
fi
if [[ -n "$(git -C "$repo" ls-files --others --exclude-standard -- "$scope")" ]]; then
  echo "untracked source files would invalidate the checked-out tree: $scope" >&2
  exit 1
fi
printf 'SOURCE_TREE_VERIFIED sha=%s scope=%s\n' "$actual" "$scope"
