#!/usr/bin/env bash
# jdp-python 本地开发：后台启动课程站点（VitePress dev 或构建后 preview）。
# 登记端口：site ${JDP_PYTHON_SITE_PORT:-5180}（id：jdp-python.site）
#
# 用法：scripts/dev.sh start|stop|status|restart|logs
#       scripts/dev.sh explain start|stop|status
# 可选：JDP_PYTHON_SITE_MODE=preview（默认 dev）；start 时可用 --preview
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd -- "${script_dir}/.." && pwd)"
run_dir="${project_dir}/.run"
log_dir="${project_dir}/logs"
site_dir="${project_dir}/site"

# shellcheck source=port-guard.sh
. "${script_dir}/port-guard.sh"

JDP_PYTHON_SITE_PORT="${JDP_PYTHON_SITE_PORT:-5180}"
SITE_PORT="${SERVER_PORT:-${PORT:-${JDP_PYTHON_SITE_PORT}}}"
HOST="${HOST:-127.0.0.1}"
JDP_DEV_WAIT="${JDP_DEV_WAIT:-60}"
JDP_PYTHON_SITE_MODE="${JDP_PYTHON_SITE_MODE:-dev}"

export JDP_PYTHON_SITE_PORT SITE_PORT HOST PORT="${SITE_PORT}"

SITE_PID_FILE="${run_dir}/site.pid"
SITE_LOG="${log_dir}/site.log"
EXPLAIN_PID_FILE="${run_dir}/explain.pid"
EXPLAIN_LOG="${log_dir}/explain.log"
JDP_PYTHON_EXPLAIN_PORT="${JDP_PYTHON_EXPLAIN_PORT:-8031}"

port_pids() {
  lsof -ti tcp:"$1" -sTCP:LISTEN 2>/dev/null | sort -u || true
}

process_cwd() {
  local pid="$1" line cwd=""
  while IFS= read -r line; do
    if [[ "${line}" == n* ]]; then
      cwd="${line#n}"
    fi
  done < <(lsof -a -p "${pid}" -d cwd -Fn 2>/dev/null || true)
  printf '%s' "$cwd"
}

process_cmd() {
  ps -o command= -p "$1" 2>/dev/null || true
}

port_check() {
  local service_id="$1" port="$2" name="$3" rc=0
  if command -v jdp-os >/dev/null 2>&1; then
    jdp-os port check "${service_id}" --port "${port}" || rc=$?
    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi
    if [[ "${rc}" -eq 3 || "${rc}" -eq 4 ]]; then
      echo "尚未迁移到登记端口（check 退出码 ${rc}），改用 port_guard 检查"
      port_guard "${port}" "${name}" || exit 1
      return 0
    fi
    exit 1
  fi
  port_guard "${port}" "${name}" || exit 1
}

belongs_to_python_repo() {
  local pid="$1" cwd cmd
  kill -0 "${pid}" 2>/dev/null || return 1
  cwd="$(process_cwd "$pid")"
  cmd="$(process_cmd "$pid")"
  [[ "${cwd}" == "${project_dir}"* ]] && return 0
  [[ "${cmd}" == *"${project_dir}"* ]] && return 0
  return 1
}

port_is_listening() {
  [[ -n "$(port_pids "$1" | tr -d '[:space:]')" ]]
}

collect_tree_pids() {
  local root="$1" child collected=""
  collected="${root}"
  for child in $(pgrep -P "${root}" 2>/dev/null || true); do
    collected+=" $(collect_tree_pids "${child}")"
  done
  printf '%s' "${collected}"
}

wait_port_listen() {
  local port="$1" name="$2" log_file="$3" i max_half
  max_half=$((JDP_DEV_WAIT * 2))
  for i in $(seq 1 "${max_half}"); do
    if port_is_listening "${port}"; then
      return 0
    fi
    sleep 0.5
  done
  echo "错误：${name} 在 ${JDP_DEV_WAIT} 秒内未在端口 ${port} 监听。" >&2
  if [[ -f "${log_file}" ]]; then
    echo "--- ${log_file} 末尾 ---" >&2
    tail -n 40 "${log_file}" >&2 || true
  fi
  return 1
}

try_skip_from_pid_file() {
  local pid_file="$1" label="$2"
  local pid p

  [[ -f "${pid_file}" ]] || return 1
  pid="$(<"${pid_file}")"
  if [[ -z "${pid}" ]]; then
    rm -f "${pid_file}"
    return 1
  fi
  if ! kill -0 "${pid}" 2>/dev/null; then
    rm -f "${pid_file}"
    return 1
  fi
  for p in $(collect_tree_pids "${pid}"); do
    if belongs_to_python_repo "${p}"; then
      echo "${label} 已在运行或正在启动（PID ${pid}）"
      return 0
    fi
  done
  return 1
}

ensure_dirs() {
  mkdir -p "${run_dir}" "${log_dir}"
}

require_site_deps() {
  if [[ ! -d "${site_dir}/node_modules" ]]; then
    echo "错误：缺少 site/node_modules，请先执行：cd site && npm install" >&2
    exit 1
  fi
}

start_site() {
  local mode="$1"
  if try_skip_from_pid_file "${SITE_PID_FILE}" "jdp-python 课程站"; then
    return 0
  fi
  port_check "jdp-python.site" "${SITE_PORT}" "jdp-python 课程站"
  ensure_dirs
  : >"${SITE_LOG}"
  if [[ "${mode}" == "preview" ]]; then
    (
      cd "${site_dir}"
      npm run build
      nohup env JDP_PYTHON_SITE_PORT="${SITE_PORT}" PORT="${SITE_PORT}" HOST="${HOST}" \
        npm run preview >>"${SITE_LOG}" 2>&1 &
      echo $! >"${SITE_PID_FILE}"
    )
  else
    (
      cd "${site_dir}"
      nohup env JDP_PYTHON_SITE_PORT="${SITE_PORT}" PORT="${SITE_PORT}" HOST="${HOST}" \
        npm run dev >>"${SITE_LOG}" 2>&1 &
      echo $! >"${SITE_PID_FILE}"
    )
  fi
  if ! wait_port_listen "${SITE_PORT}" "jdp-python 课程站" "${SITE_LOG}"; then
    return 1
  fi
  echo "jdp-python 课程站（${mode}）：http://${HOST}:${SITE_PORT}/"
}

cmd_start() {
  local mode="${JDP_PYTHON_SITE_MODE}"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --preview) mode="preview" ;;
      --dev) mode="dev" ;;
      *)
        echo "未知 start 参数: $1" >&2
        exit 2
        ;;
    esac
    shift
  done
  require_site_deps
  start_site "${mode}"
}

kill_pids_gracefully() {
  local label="$1"
  shift
  local pid still alive=() i
  local -a targets=()
  for pid in "$@"; do
    [[ -n "${pid}" ]] || continue
    if kill -0 "${pid}" 2>/dev/null; then
      targets+=("${pid}")
    fi
  done
  if [[ ${#targets[@]} -eq 0 ]]; then
    return 0
  fi
  echo "停止 ${label}（PID: ${targets[*]}）..."
  kill "${targets[@]}" 2>/dev/null || true
  for i in $(seq 1 20); do
    still=()
    for pid in "${targets[@]}"; do
      kill -0 "${pid}" 2>/dev/null && still+=("${pid}")
    done
    if [[ ${#still[@]} -eq 0 ]]; then
      echo "${label} 已停。"
      return 0
    fi
    sleep 0.5
  done
  alive=()
  for pid in "${targets[@]}"; do
    kill -0 "${pid}" 2>/dev/null && alive+=("${pid}")
  done
  if [[ ${#alive[@]} -gt 0 ]]; then
    echo "${label} 10 秒内未退出，发送 KILL。" >&2
    kill -9 "${alive[@]}" 2>/dev/null || true
  fi
  echo "${label} 已强杀。"
}

stop_service() {
  local name="$1" port="$2" pid_file="$3"
  local pid candidate_pids="" skipped=0

  if [[ -f "${pid_file}" ]]; then
    pid="$(<"${pid_file}")"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      if belongs_to_python_repo "${pid}"; then
        candidate_pids+=" $(collect_tree_pids "${pid}")"
      else
        echo "跳过 PID 文件 ${pid_file} 中的 ${pid}：不属于本仓库进程。" >&2
        skipped=1
      fi
    fi
  fi

  for pid in $(port_pids "${port}"); do
    if belongs_to_python_repo "${pid}"; then
      candidate_pids+=" $(collect_tree_pids "${pid}")"
    elif [[ -n "${pid}" ]]; then
      echo "跳过端口 ${port} 上的 PID ${pid}：不属于本仓库，未杀进程。" >&2
      skipped=1
    fi
  done

  local -a unique=() seen u
  for pid in ${candidate_pids}; do
    [[ -z "${pid}" ]] && continue
    seen=0
    for u in "${unique[@]:-}"; do
      [[ "${u}" == "${pid}" ]] && seen=1 && break
    done
    [[ "${seen}" -eq 0 ]] && unique+=("${pid}")
  done

  if [[ ${#unique[@]} -eq 0 ]]; then
    if [[ "${skipped}" -eq 1 ]]; then
      echo "${name}（:${port}）无本仓库进程可停。"
    else
      echo "${name}（:${port}）没在跑。"
    fi
    rm -f "${pid_file}"
    return 0
  fi

  kill_pids_gracefully "${name}（:${port}）" "${unique[@]}"
  rm -f "${pid_file}"
}

cmd_stop() {
  stop_service "jdp-python 课程站" "${SITE_PORT}" "${SITE_PID_FILE}"
}

pid_file_state() {
  local pid_file="$1" port="$2"
  if [[ ! -f "${pid_file}" ]]; then
    echo "无"
    return 0
  fi
  local file_pid
  file_pid="$(<"${pid_file}")"
  if [[ -z "${file_pid}" ]]; then
    echo "过期（空文件）"
    return 0
  fi
  if ! kill -0 "${file_pid}" 2>/dev/null; then
    echo "过期（进程不存在）"
    return 0
  fi
  if ! belongs_to_python_repo "${file_pid}"; then
    echo "过期（非本仓库进程）"
    return 0
  fi
  if port_is_listening "${port}"; then
    echo "有效（PID ${file_pid}）"
    return 0
  fi
  if kill -0 "${file_pid}" 2>/dev/null; then
    echo "有效（PID ${file_pid}，端口尚未监听或子进程监听）"
    return 0
  fi
  echo "过期"
}

cmd_status() {
  local listen listeners state primary_pid
  if port_is_listening "${SITE_PORT}"; then
    listen="是"
    listeners="$(port_pids "${SITE_PORT}" | tr '\n' ',' | sed 's/,$//')"
  else
    listen="否"
    listeners="-"
  fi
  state="$(pid_file_state "${SITE_PID_FILE}" "${SITE_PORT}")"
  primary_pid="-"
  if [[ -f "${SITE_PID_FILE}" ]]; then
    primary_pid="$(<"${SITE_PID_FILE}")"
  fi
  echo "jdp-python 课程站: 端口 ${SITE_PORT} | 监听: ${listen} | 监听 PID: ${listeners} | PID 文件: ${primary_pid} | 状态: ${state}"
}

cmd_logs() {
  if [[ ! -f "${SITE_LOG}" ]]; then
    echo "尚无日志文件（先执行 scripts/dev.sh start）。"
    exit 0
  fi
  exec tail -f "${SITE_LOG}"
}

start_explain() {
  if try_skip_from_pid_file "${EXPLAIN_PID_FILE}" "jdp-python AI 讲解"; then
    return 0
  fi
  ensure_dirs
  : >"${EXPLAIN_LOG}"
  (
    cd "${project_dir}"
    nohup env JDP_PYTHON_EXPLAIN_PORT="${JDP_PYTHON_EXPLAIN_PORT}" \
      uv run python scripts/explain_server.py >>"${EXPLAIN_LOG}" 2>&1 &
    echo $! >"${EXPLAIN_PID_FILE}"
  )
  if ! wait_port_listen "${JDP_PYTHON_EXPLAIN_PORT}" "jdp-python AI 讲解" "${EXPLAIN_LOG}"; then
    return 1
  fi
  echo "jdp-python AI 讲解：http://127.0.0.1:${JDP_PYTHON_EXPLAIN_PORT}/v1/health"
}

cmd_explain() {
  local sub="${1:-status}"
  shift || true
  case "${sub}" in
    start) start_explain ;;
    stop) stop_service "jdp-python AI 讲解" "${JDP_PYTHON_EXPLAIN_PORT}" "${EXPLAIN_PID_FILE}" ;;
    status)
      local listen listeners state primary_pid
      if port_is_listening "${JDP_PYTHON_EXPLAIN_PORT}"; then listen="是"; listeners="$(port_pids "${JDP_PYTHON_EXPLAIN_PORT}" | tr '\n' ',' | sed 's/,$//')"; else listen="否"; listeners="-"; fi
      state="$(pid_file_state "${EXPLAIN_PID_FILE}" "${JDP_PYTHON_EXPLAIN_PORT}")"
      primary_pid="-"
      [[ -f "${EXPLAIN_PID_FILE}" ]] && primary_pid="$(<"${EXPLAIN_PID_FILE}")"
      echo "jdp-python AI 讲解: 端口 ${JDP_PYTHON_EXPLAIN_PORT} | 监听: ${listen} | 监听 PID: ${listeners} | PID 文件: ${primary_pid} | 状态: ${state}"
      ;;
    *)
      echo "用法: scripts/dev.sh explain start|stop|status" >&2
      exit 2
      ;;
  esac
}

usage() {
  cat <<EOF
用法: scripts/dev.sh start|stop|status|restart|logs

  端口（环境变量，默认 5180）:
    JDP_PYTHON_SITE_PORT  SERVER_PORT  PORT  HOST（默认 127.0.0.1）
  模式: JDP_PYTHON_SITE_MODE=dev|preview（默认 dev）；start 可加 --preview / --dev
  启动等待（秒，默认 60）: JDP_DEV_WAIT

  start   — 后台启动课程站（日志 logs/site.log，PID .run/site.pid）
  stop    — 仅停止属于本仓库的进程
  status  — 查看端口与进程状态
  restart — stop 后 start
  logs    — tail -f site 日志
EOF
}

main() {
  local cmd="${1:-}"
  if [[ -z "${cmd}" ]]; then
    usage
    return 0
  fi
  case "${cmd}" in
    start)
      shift
      cmd_start "$@"
      ;;
    stop) cmd_stop ;;
    status) cmd_status ;;
    restart)
      cmd_stop || true
      shift
      cmd_start "$@"
      ;;
    logs) cmd_logs ;;
    explain)
      shift
      cmd_explain "$@"
      ;;
    -h|--help|help) usage ;;
    *)
      echo "未知子命令: ${cmd}" >&2
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
