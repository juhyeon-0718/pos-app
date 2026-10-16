#!/bin/sh
# pre-push guard 설치. 워크트리는 .git 공통 디렉터리의 hooks를 공유하므로 한 번만 실행하면 된다.
set -e
hooks_dir="$(git rev-parse --git-common-dir)/hooks"
src="$(git rev-parse --show-toplevel)/scripts/git-hooks/pre-push"
cp "$src" "$hooks_dir/pre-push"
chmod +x "$hooks_dir/pre-push"
echo "installed: $hooks_dir/pre-push"
