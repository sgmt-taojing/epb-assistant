#!/usr/bin/env bash
# epb-assistant 独立部署脚本（商用就绪 S1）
# 用法: bash deploy.sh [start|stop|status]
set -uo pipefail
PORT="${PORT:-8944}"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"

start() {
  echo "▶ 启动 epb-assistant @ :${PORT}"
  # 统一入口：scripts/file_server.py（支持 PORT 环境变量；绑定 127.0.0.1）
  (cd "$APP_DIR" && PORT="$PORT" nohup python3 scripts/file_server.py > logs/server.log 2>&1 &)
  sleep 1
  status
}

stop() {
  echo "⏹ 停止 epb-assistant"
  pkill -f "$APP_DIR" 2>/dev/null || true
}

status() {
  if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PORT}/" 2>/dev/null | grep -q 200; then
    echo "✓ epb-assistant @ :${PORT} 运行中"
  else
    echo "⚠ epb-assistant @ :${PORT} 未响应"
  fi
}

mkdir -p "$APP_DIR/logs"
case "${1:-start}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  restart) stop; sleep 1; start ;;
  *) echo "用法: $0 [start|stop|status|restart]" ;;
esac
