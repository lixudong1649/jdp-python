#!/usr/bin/env bash
# 后台启动课程站点（构建后预览），仅监听本机：http://127.0.0.1:${PORT:-5180}/
# 用法：bash site/scripts/serve-bg.sh [--no-build]    停止：bash site/scripts/serve-bg.sh --stop
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${PORT:-5180}"
LOG=".vitepress/preview.log"
PIDFILE=".vitepress/preview.pid"

stop() {
  if [[ -f "${PIDFILE}" ]] && kill -0 "$(cat "${PIDFILE}")" 2>/dev/null; then
    kill -- "-$(cat "${PIDFILE}")" 2>/dev/null || kill "$(cat "${PIDFILE}")" || true
    echo "已停止（PID $(cat "${PIDFILE}")）"
  fi
  rm -f "${PIDFILE}"
}

if [[ "${1:-}" == "--stop" ]]; then stop; exit 0; fi
[[ -d node_modules ]] || npm install
[[ "${1:-}" == "--no-build" ]] || npm run build
stop
# setsid 让进程脱离当前终端会话，关闭终端后仍继续运行
# macOS 没有 setsid 命令，用 perl 的 POSIX::setsid 实现同样效果
if command -v setsid >/dev/null; then
  SETSID=(setsid)
else
  SETSID=(perl -MPOSIX=setsid -e 'setsid(); exec @ARGV or die "exec: $!"')
fi
nohup "${SETSID[@]}" node scripts/serve.mjs --host 127.0.0.1 --port "${PORT}" > "${LOG}" 2>&1 < /dev/null &
echo $! > "${PIDFILE}"
for _ in $(seq 1 30); do
  if curl -fs -o /dev/null "http://127.0.0.1:${PORT}/"; then
    echo "课程站点已启动：http://127.0.0.1:${PORT}/ （日志 site/${LOG}）"; exit 0
  fi
  sleep 1
done
echo "启动超时，请查看 site/${LOG}" >&2; exit 1
