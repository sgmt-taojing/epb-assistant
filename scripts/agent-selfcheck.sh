#!/usr/bin/env bash
# agent-selfcheck.sh — epb-assistant 项目独立自检
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
OK=0; FAIL=0
P() { echo "  $1"; }
check() { if [ "$1" = "0" ]; then OK=$((OK+1)); P "✓ $2"; else FAIL=$((FAIL+1)); P "✗ $2"; fi }
echo "═ epb-assistant 自检 ═"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 http://127.0.0.1:8944/ 2>/dev/null | tr -d " ")
[ "$code" = "200" ]; check $? "app :8944/"
# 部署脚本存在
[ -f deploy.sh ] || [ -f Dockerfile ]; check $? "部署脚本"
# LICENSE
[ -f LICENSE ]; check $? "LICENSE（商用）"
# 页面数
N=$(ls app/*.html web/*.html 2>/dev/null | wc -l | tr -d ' ')
[ "$N" -gt 0 ]; check $? "前端页面（$N）"
echo "═ 结果: ✓ $OK · ✗ $FAIL ═"
[ "$FAIL" = "0" ]
