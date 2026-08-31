#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
START_SCRIPT="${ROOT_DIR}/start.sh"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

assert_contains() {
  local pattern="$1"
  grep -Fq -- "${pattern}" "${START_SCRIPT}" || fail "start.sh 缺少: ${pattern}"
}

[[ -f "${START_SCRIPT}" ]] || fail "start.sh 不存在"
bash -n "${START_SCRIPT}" || fail "start.sh 语法错误"

assert_contains "set -Eeuo pipefail"
assert_contains "alembic upgrade head"
assert_contains "scripts/seed_dev.py"
assert_contains "0.0.0.0"
assert_contains "8000"
assert_contains "3000"
assert_contains "npm run dev"
assert_contains "trap cleanup"
assert_contains "port_in_use"

printf 'PASS: start.sh contract\n'
