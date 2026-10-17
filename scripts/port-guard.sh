#!/usr/bin/env bash
# 端口占用检查（仅 lsof/ps，不杀进程、不换端口）。
#
# 用法示例（在项目 dev.sh 中）:
#   if command -v jdp-os >/dev/null; then jdp-os port check <id> || exit 1
#   else . "$(dirname "$0")/port-guard.sh"; port_guard "$PORT" <name> || exit 1; fi

port_guard() {
  local port="$1"
  local name="${2:-service}"
  local pid cmd cwd_line

  pid="$(lsof -nP -iTCP:"${port}" -sTCP:LISTEN -t 2>/dev/null || true)"
  if [[ -z "${pid}" ]]; then
    return 0
  fi

  # 多监听时取第一个 PID
  pid="${pid%%$'\n'*}"

  cmd="$(ps -o command= -p "${pid}" 2>/dev/null || true)"
  cwd_line="$(lsof -a -p "${pid}" -d cwd -Fn 2>/dev/null || true)"
  cwd=""
  while IFS= read -r line; do
    if [[ "${line}" == n* ]]; then
      cwd="${line#n}"
    fi
  done <<< "${cwd_line}"

  echo "端口 ${port}（${name}）已被占用，不会自动换端口或杀进程。" >&2
  echo "PID: ${pid}" >&2
  [[ -n "${cmd}" ]] && echo "命令: ${cmd}" >&2
  [[ -n "${cwd}" ]] && echo "cwd: ${cwd}" >&2
  return 1
}
