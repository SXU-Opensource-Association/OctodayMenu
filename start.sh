#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
BACKEND_PORT="8000"
FRONTEND_PORT="3000"
BACKEND_PID=""
FRONTEND_PID=""

fail() {
  printf '启动失败: %s\n' "$1" >&2
  exit 1
}

require_file() {
  [[ -f "$1" ]] || fail "缺少文件 $1"
}

require_directory() {
  [[ -d "$1" ]] || fail "缺少目录 $1"
}

require_executable() {
  [[ -x "$1" ]] || fail "缺少可执行文件 $1"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "未找到命令 $1"
}

port_in_use() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
    return
  fi
  if command -v nc >/dev/null 2>&1; then
    nc -z 127.0.0.1 "${port}" >/dev/null 2>&1
    return
  fi
  fail "需要 lsof 或 nc 来检查端口"
}

show_port_owner() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"${port}" -sTCP:LISTEN >&2 || true
  fi
}

detect_lan_ip() {
  local interface_name
  local address

  if command -v ipconfig >/dev/null 2>&1; then
    for interface_name in en0 en1; do
      address="$(ipconfig getifaddr "${interface_name}" 2>/dev/null || true)"
      if [[ -n "${address}" ]]; then
        printf '%s' "${address}"
        return
      fi
    done
  fi

  if command -v hostname >/dev/null 2>&1; then
    address="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
    if [[ -n "${address}" ]]; then
      printf '%s' "${address}"
    fi
  fi
}

terminate_process_tree() {
  local pid="$1"
  local child
  local children

  [[ -n "${pid}" ]] || return
  kill -0 "${pid}" >/dev/null 2>&1 || return

  if command -v pgrep >/dev/null 2>&1; then
    children="$(pgrep -P "${pid}" 2>/dev/null || true)"
    for child in ${children}; do
      terminate_process_tree "${child}"
    done
  fi

  kill "${pid}" >/dev/null 2>&1 || true
}

cleanup() {
  local exit_code=$?
  trap - INT TERM EXIT

  if [[ -n "${BACKEND_PID}" || -n "${FRONTEND_PID}" ]]; then
    printf '\n正在关闭前后端服务...\n'
  fi

  terminate_process_tree "${FRONTEND_PID}"
  terminate_process_tree "${BACKEND_PID}"

  if [[ -n "${FRONTEND_PID}" ]]; then
    wait "${FRONTEND_PID}" 2>/dev/null || true
  fi
  if [[ -n "${BACKEND_PID}" ]]; then
    wait "${BACKEND_PID}" 2>/dev/null || true
  fi

  exit "${exit_code}"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

require_file "${BACKEND_DIR}/.env"
require_executable "${BACKEND_DIR}/.venv/bin/python"
require_executable "${BACKEND_DIR}/.venv/bin/uvicorn"
require_executable "${BACKEND_DIR}/.venv/bin/alembic"
require_directory "${FRONTEND_DIR}/node_modules"
require_command npm

if port_in_use "${BACKEND_PORT}"; then
  show_port_owner "${BACKEND_PORT}"
  fail "后端端口 ${BACKEND_PORT} 已被占用"
fi

if port_in_use "${FRONTEND_PORT}"; then
  show_port_owner "${FRONTEND_PORT}"
  fail "前端端口 ${FRONTEND_PORT} 已被占用"
fi

printf '正在执行数据库迁移...\n'
(
  cd "${BACKEND_DIR}"
  .venv/bin/alembic upgrade head
  .venv/bin/python scripts/seed_dev.py
)

printf '正在启动 FastAPI...\n'
(
  cd "${BACKEND_DIR}"
  exec .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port "${BACKEND_PORT}"
) &
BACKEND_PID=$!

printf '正在启动 Next.js...\n'
(
  cd "${FRONTEND_DIR}"
  exec npm run dev -- --port "${FRONTEND_PORT}"
) &
FRONTEND_PID=$!

LAN_IP="$(detect_lan_ip)"
printf '\n项目已启动：\n'
printf '  本机访问: http://127.0.0.1:%s\n' "${FRONTEND_PORT}"
if [[ -n "${LAN_IP}" ]]; then
  printf '  局域网访问: http://%s:%s\n' "${LAN_IP}" "${FRONTEND_PORT}"
fi
printf '按 Ctrl+C 同时关闭前后端服务。\n\n'

while true; do
  if ! kill -0 "${BACKEND_PID}" >/dev/null 2>&1; then
    if wait "${BACKEND_PID}"; then
      fail "FastAPI 服务已退出"
    else
      fail "FastAPI 服务异常退出"
    fi
  fi

  if ! kill -0 "${FRONTEND_PID}" >/dev/null 2>&1; then
    if wait "${FRONTEND_PID}"; then
      fail "Next.js 服务已退出"
    else
      fail "Next.js 服务异常退出"
    fi
  fi

  sleep 1
done
