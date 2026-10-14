#!/usr/bin/env bash
# Verify the Git subtree actually checked out at a directory, not an adjacent
# CI workflow or a caller-supplied commit label. A source tree may be mirrored
# below a test repository's root without changing its Git tree identity.
set -euo pipefail
if (( $# < 2 || $# > 3 )); then
  echo 'usage: verify_source_tree.sh CHECKOUT_DIRECTORY EXPECTED_40_HEX_TREE [--allow-generated-target]' >&2
  exit 2
fi
checkout=$(cd -- "$1" && pwd -P) || { echo "source directory not found" >&2; exit 2; }
expected=${2,,}
if [[ ! "$expected" =~ ^[a-f0-9]{40}$ ]]; then
  echo 'expected Git tree SHA must be 40 hex characters' >&2
  exit 2
fi
if (( $# == 3 )) && [[ "$3" != '--allow-generated-target' ]]; then
  echo 'unknown verifier option' >&2
  exit 2
fi
allow_target=false
if (( $# == 3 )); then allow_target=true; fi
repo=$(git -C "$checkout" rev-parse --show-toplevel 2>/dev/null) || {
  echo "not a Git checkout: $checkout" >&2; exit 2;
}
repo=$(cd -- "$repo" && pwd -P)
if [[ "$checkout" == "$repo" ]]; then
  selector='HEAD^{tree}'
  scope='.'
  generated='target/'
else
  if [[ "$checkout" != "$repo"/* ]]; then
    echo 'checkout escapes Git worktree' >&2; exit 2
  fi
  scope=${checkout#"$repo"/}
  selector="HEAD:$scope"
  generated="$scope/target/"
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
# Independently compare HEAD's committed blob map with the *index* map.
# Cached diffs can be influenced by per-path index flags; a missing/replaced
# path is never acceptable just because Git's normal status is quiet.
declare -A head_entries=()
while IFS= read -r -d '' record; do
  metadata=${record%% Independently
# hash indexed physical bytes and executable modes so flags cannot hide edits.
tracked=0
while IFS= read -r -d '' record; do
  metadata=${record%%
\t'*}
  relative=${record#*
\t'}
  read -r mode object stage <<< "$metadata"
  if [[ "$stage" != 0 || ( "$mode" != '100644' && "$mode" != '100755' ) ]]; then
    echo "unsupported staged object or source file mode: $relative" >&2; exit 1
  fi
  if [[ "${head_entries[$relative]-}" != "$mode $object" ]]; then
    echo "Git index differs from HEAD tree: $relative" >&2; exit 1
  fi
  physical="$repo/$relative"
  if [[ ! -f "$physical" || -L "$physical" ]]; then
    echo "source file missing, nonregular, or symlink: $relative" >&2; exit 1
  fi
  if [[ "$(realpath -e -- "$physical")" != "$physical" ]]; then
    echo "source resolved through a symlink: $relative" >&2; exit 1
  fi
  if [[ "$(git -C "$repo" hash-object --no-filters -- "$physical")" != "$object" ]]; then
    echo "source blob does not match Git index: $relative" >&2; exit 1
  fi
  if [[ "$mode" == 100755 && ! -x "$physical" ]] ||
     [[ "$mode" == 100644 && -x "$physical" ]]; then
    echo "source executable mode differs from Git index: $relative" >&2; exit 1
  fi
  tracked=$((tracked + 1))
done < <(git -C "$repo" ls-files --stage -z -- "$scope")
if (( tracked == 0 )); then
  echo "empty tracked source subtree: $scope" >&2; exit 1
fi
if (( tracked != ${#head_entries[@]} )); then
  echo "Git index path count differs from committed HEAD source tree" >&2; exit 1
fi
# Ordinary untracked and ignored contents require separate queries.
while IFS= read -r -d '' unexpected; do
  echo "untracked source file would invalidate tree: $unexpected" >&2; exit 1
done < <(git -C "$repo" ls-files --others --exclude-standard --directory -z -- "$scope")
while IFS= read -r -d '' unexpected; do
  if [[ "$allow_target" == true && "$unexpected" == "$generated" &&
        -d "$checkout/target" && ! -L "$checkout/target" ]]; then
    continue
  fi
  echo "ignored source file would invalidate tree: $unexpected" >&2; exit 1
done < <(git -C "$repo" ls-files --others --ignored --exclude-standard --directory -z -- "$scope")
printf 'SOURCE_TREE_VERIFIED sha=%s scope=%s tracked=%d\n' "$actual" "$scope" "$tracked"
\t'*}
  relative=${record#* Independently
# hash indexed physical bytes and executable modes so flags cannot hide edits.
tracked=0
while IFS= read -r -d '' record; do
  metadata=${record%%
\t'*}
  relative=${record#*
\t'}
  read -r mode object stage <<< "$metadata"
  if [[ "$stage" != 0 || ( "$mode" != '100644' && "$mode" != '100755' ) ]]; then
    echo "unsupported staged object or source file mode: $relative" >&2; exit 1
  fi
  physical="$repo/$relative"
  if [[ ! -f "$physical" || -L "$physical" ]]; then
    echo "source file missing, nonregular, or symlink: $relative" >&2; exit 1
  fi
  if [[ "$(realpath -e -- "$physical")" != "$physical" ]]; then
    echo "source resolved through a symlink: $relative" >&2; exit 1
  fi
  if [[ "$(git -C "$repo" hash-object --no-filters -- "$physical")" != "$object" ]]; then
    echo "source blob does not match Git index: $relative" >&2; exit 1
  fi
  if [[ "$mode" == 100755 && ! -x "$physical" ]] ||
     [[ "$mode" == 100644 && -x "$physical" ]]; then
    echo "source executable mode differs from Git index: $relative" >&2; exit 1
  fi
  tracked=$((tracked + 1))
done < <(git -C "$repo" ls-files --stage -z -- "$scope")
if (( tracked == 0 )); then
  echo "empty tracked source subtree: $scope" >&2; exit 1
fi
# Ordinary untracked and ignored contents require separate queries.
while IFS= read -r -d '' unexpected; do
  echo "untracked source file would invalidate tree: $unexpected" >&2; exit 1
done < <(git -C "$repo" ls-files --others --exclude-standard --directory -z -- "$scope")
while IFS= read -r -d '' unexpected; do
  if [[ "$allow_target" == true && "$unexpected" == "$generated" &&
        -d "$checkout/target" && ! -L "$checkout/target" ]]; then
    continue
  fi
  echo "ignored source file would invalidate tree: $unexpected" >&2; exit 1
done < <(git -C "$repo" ls-files --others --ignored --exclude-standard --directory -z -- "$scope")
printf 'SOURCE_TREE_VERIFIED sha=%s scope=%s tracked=%d\n' "$actual" "$scope" "$tracked"
\t'}
  read -r mode object_type object <<< "$metadata"
  if [[ "$object_type" != 'blob' ]]; then
    echo "HEAD contains unsupported non-blob: $relative" >&2; exit 1
  fi
  head_entries["$relative"]="$mode $object"
done < <(git -C "$repo" ls-tree -r -z HEAD -- "$scope")
if (( ${#head_entries[@]} == 0 )); then
  echo "HEAD contains no source blobs at $scope" >&2; exit 1
fi
# Git diff/status honor assume-unchanged and skip-worktree. Independently
# hash indexed physical bytes and executable modes so flags cannot hide edits.
tracked=0
while IFS= read -r -d '' record; do
  metadata=${record%%
\t'*}
  relative=${record#*
\t'}
  read -r mode object stage <<< "$metadata"
  if [[ "$stage" != 0 || ( "$mode" != '100644' && "$mode" != '100755' ) ]]; then
    echo "unsupported staged object or source file mode: $relative" >&2; exit 1
  fi
  physical="$repo/$relative"
  if [[ ! -f "$physical" || -L "$physical" ]]; then
    echo "source file missing, nonregular, or symlink: $relative" >&2; exit 1
  fi
  if [[ "$(realpath -e -- "$physical")" != "$physical" ]]; then
    echo "source resolved through a symlink: $relative" >&2; exit 1
  fi
  if [[ "$(git -C "$repo" hash-object --no-filters -- "$physical")" != "$object" ]]; then
    echo "source blob does not match Git index: $relative" >&2; exit 1
  fi
  if [[ "$mode" == 100755 && ! -x "$physical" ]] ||
     [[ "$mode" == 100644 && -x "$physical" ]]; then
    echo "source executable mode differs from Git index: $relative" >&2; exit 1
  fi
  tracked=$((tracked + 1))
done < <(git -C "$repo" ls-files --stage -z -- "$scope")
if (( tracked == 0 )); then
  echo "empty tracked source subtree: $scope" >&2; exit 1
fi
# Ordinary untracked and ignored contents require separate queries.
while IFS= read -r -d '' unexpected; do
  echo "untracked source file would invalidate tree: $unexpected" >&2; exit 1
done < <(git -C "$repo" ls-files --others --exclude-standard --directory -z -- "$scope")
while IFS= read -r -d '' unexpected; do
  if [[ "$allow_target" == true && "$unexpected" == "$generated" &&
        -d "$checkout/target" && ! -L "$checkout/target" ]]; then
    continue
  fi
  echo "ignored source file would invalidate tree: $unexpected" >&2; exit 1
done < <(git -C "$repo" ls-files --others --ignored --exclude-standard --directory -z -- "$scope")
printf 'SOURCE_TREE_VERIFIED sha=%s scope=%s tracked=%d\n' "$actual" "$scope" "$tracked"
