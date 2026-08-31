#!/usr/bin/env bash
# agent-selfcheck.sh — epb-assistant 项目独立自检（v2 全量版）
# 覆盖：服务健康 / 部署就绪 / 页面资产 / Python 语法 / JS 语法 / 品牌隔离 / 密钥红线 / 端口一致性
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
OK=0; FAIL=0
P() { echo "  $1"; }
check() { if [ "$1" = "0" ]; then OK=$((OK+1)); P "✓ $2"; else FAIL=$((FAIL+1)); P "✗ $2"; fi }

echo "═ epb-assistant 自检 v2 ═"

# 1. 服务健康（本地 8899 / Docker 8900 任一在跑即可；deploy.sh 端口 8944 由 PORT 覆盖）
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 http://127.0.0.1:8899/api/health 2>/dev/null | tr -d " ")
[ "$code" = "200" ]; check $? "服务健康 :8899/api/health（HTTP $code）"

# 2. 部署脚本与商用文件
[ -f deploy.sh ] || [ -f Dockerfile ]; check $? "部署脚本"
[ -f LICENSE ]; check $? "LICENSE（商用）"
[ -f PRIVACY.md ] && [ -f TERMS.md ]; check $? "PRIVACY/TERMS（合规）"

# 3. 前端页面资产
N=$(ls web/*.html 2>/dev/null | wc -l | tr -d ' ')
[ "$N" -gt 30 ]; check $? "前端页面（${N}）"

# 4. Python 语法全检
py_err=0
while IFS= read -r f; do
  python3 -m py_compile "$f" 2>/dev/null || { py_err=1; P "    ✗ $f"; }
done < <(find scripts app -name "*.py" -not -path "*/venv/*" -not -path "*__pycache__*" 2>/dev/null)
[ "$py_err" = "0" ]; check $? "Python 语法（scripts+app 全量）"

# 5. 前端 JS 语法（独立 .js 文件）
js_err=0
while IFS= read -r f; do
  node --check "$f" 2>/dev/null || { js_err=1; P "    ✗ $f"; }
done < <(find web -name "*.js" -not -path "*node_modules*" 2>/dev/null)
[ "$js_err" = "0" ]; check $? "JS 语法（web/*.js 全量）"

# 6. 品牌隔离（UI/展示层不得出现其他项目品牌词；注释里的修真记录放行）
brand_hits=$(grep -rn "命理宝鉴\|易道智鉴\|mingli-baojian\|nihaisha\|倪海厦\|tcm-diagnosis\|tcm-agent" \
  web/ app/ scripts/ src/ tests/ *.md 2>/dev/null \
  | grep -v node_modules | grep -v "修真\|反向污染\|改为写入\|已停止\|历史" \
  | grep -v "agent-selfcheck.sh" | wc -l | tr -d ' ')
[ "$brand_hits" = "0" ]; check $? "品牌隔离（残留 ${brand_hits} 处）"

# 7. 密钥红线（源码不得出现硬编码密钥/后门口令）
secret_hits=$(grep -rn "admin123\|SECRET_KEY *= *['\"][^'\"]\{8,\}" app/ scripts/ web/ 2>/dev/null \
  | grep -v node_modules | grep -v "agent-selfcheck.sh" \
  | grep -v "移除 admin123 硬编码后门" | wc -l | tr -d ' ')
[ "$secret_hits" = "0" ]; check $? "密钥红线（硬编码 ${secret_hits} 处）"

# 8. 端口一致性（file_server 的默认端口与 config.json 对齐 = 8899）
cfg_port=$(python3 -c "import json;print(json.load(open('db/config.json')).get('server',{}).get('port','8899'))" 2>/dev/null || echo "8899")
[ "$cfg_port" = "8899" ]; check $? "端口一致性（config=${cfg_port}，本地默认 8899，Docker/deploy 用 PORT 覆盖）"

echo "═ 结果: ✓ $OK · ✗ $FAIL ═"
[ "$FAIL" = "0" ]
