#!/bin/bash
# Responsive CSS injection script for EPB Assistant HTML files

WORK_DIR="/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/web"

# The responsive CSS block to insert before </style>
read -r -d '' RESPONSIVE_CSS << 'RESPONSIVE_END'
/* 响应式适配 */
@media (max-width: 768px){
html{font-size:90%}
body{padding-bottom:70px;font-size:13px}
.hero{padding:16px 12px}
.hero h1{font-size:17px}
.hero p{font-size:11px}
.container{padding:10px}
/* 导航栏适配 */
.bottom-nav{padding:6px 0}
.nav-item{font-size:9px}
.nav-item .icon{font-size:16px}
.tabs{gap:4px;overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch}
.tab{padding:8px 10px;font-size:12px;flex-shrink:0}
.nav-quick{gap:4px;padding:8px}
.nav-link{padding:4px 8px;font-size:11px}
/* 网格变单列 */
.stat-row,.stats-row,.kpi-grid,.two-col,.dim-grid,.dim-row,.form-row,.metrics-row,.doc-types,.drone-info,.provider-stats{grid-template-columns:1fr 1fr!important;gap:8px!important}
.items{grid-template-columns:1fr!important}
.func-grid{grid-template-columns:1fr 1fr!important}
.device-grid{grid-template-columns:1fr!important}
.type-grid{grid-template-columns:1fr 1fr!important}
/* 卡片单列 */
.card,.section,.ent-card,.drone-card,.knowledge-card,.item-card,.step-card,.trade-card,.demand-card,.provider-card,.person-card,.event-card,.result-card,.metric-card{width:100%;margin-bottom:10px}
/* 表格水平滚动 */
.table,table{display:block;overflow-x:auto;-webkit-overflow-scrolling:touch;white-space:nowrap;max-width:100%}
/* 字号缩小 */
.section-title{font-size:13px}
.card-title{font-size:14px}
.stat-card .num,.kpi-value{font-size:20px}
.hero-meta{gap:10px}
.hero-meta span{font-size:10px}
/* 详情弹窗 */
.detail-modal{max-height:90vh;border-radius:16px 16px 0 0}
.score-big{font-size:36px}
/* 图表 */
.chart-row{height:80px}
.chart-bar-val{font-size:8px}
.chart-bar-label{font-size:8px}
}
@media (min-width: 1200px){
body{padding-bottom:20px}
.container{max-width:1400px;margin:0 auto;padding:24px}
.hero{padding:40px 24px}
.hero h1{font-size:26px}
.hero p{font-size:14px}
/* 宽屏3列卡片 */
.stat-row,.stats-row,.kpi-grid,.metrics-row{grid-template-columns:repeat(4,1fr)!important;gap:16px!important}
.two-col,.dim-grid,.form-row,.doc-types{grid-template-columns:1fr 1fr!important;gap:16px!important}
.items{grid-template-columns:repeat(3,1fr)!important;gap:18px}
.func-grid{grid-template-columns:repeat(4,1fr)!anttigap:14px!important}
.device-grid{grid-template-columns:repeat(3,1fr)!important;gap:16px}
.type-grid{grid-template-columns:repeat(4,1fr)!important;gap:14px}
.dim-row{grid-template-columns:repeat(4,1fr)!important}
.drone-info{grid-template-columns:repeat(3,1fr)!important}
.provider-stats{grid-template-columns:repeat(3,1fr)!important}
/* 底部导航变侧边栏 */
.bottom-nav{position:fixed;bottom:0;left:0;right:auto;width:80px;flex-direction:column;padding:12px 0;align-items:center}
.nav-item{width:100%;padding:10px 0;font-size:10px}
.nav-item .icon{font-size:22px}
.container{padding-left:100px}
/* 大屏hero优化 */
.hero-meta{gap:30px}
.hero-meta span{font-size:13px}
/* section更大间距 */
.section{padding:20px;margin-bottom:16px}
.card{padding:20px;margin-bottom:16px}
/* 详情弹窗宽屏 */
.detail-modal{max-width:700px}
}
RESPONSIVE_END

# Fix the typo in func-grid
RESPONSIVE_CSS=$(echo "$RESPONSIVE_CSS" | sed 's/\.func-grid{grid-template-columns:repeat(4,1fr)!anttigap:14px!important}/.func-grid{grid-template-columns:repeat(4,1fr)!important;gap:14px!important}/')

FILES=(
  "ai-report.html"
  "analysis.html"
  "approval-service.html"
  "capacity-assess.html"
  "carbon-mgmt.html"
  "case-analysis.html"
  "credit-rating.html"
  "data-cockpit.html"
  "device-mgmt.html"
  "doc-generator.html"
  "drone-patrol.html"
  "eco-calendar.html"
  "eco-frontier.html"
  "eco-manager.html"
  "eco-science.html"
)

echo "Processing ${#FILES[@]} files..."
echo "================================"

for f in "${FILES[@]}"; do
  FILEPATH="$WORK_DIR/$f"
  if [ ! -f "$FILEPATH" ]; then
    echo "❌ NOT FOUND: $f"
    continue
  fi
  
  # Check if already has responsive
  if grep -q "响应式适配" "$FILEPATH"; then
    echo "⚠️  ALREADY HAS RESPONSIVE: $f (skipping)"
    continue
  fi
  
  # Count lines before
  LINES_BEFORE=$(wc -l < "$FILEPATH")
  
  # Find the </style> line and insert before it
  STYLE_LINE=$(grep -n '</style>' "$FILEPATH" | head -1 | cut -d: -f1)
  
  if [ -n "$STYLE_LINE" ]; then
    # Insert the responsive CSS before </style>
    # Use sed to insert - need to escape special chars carefully
    # Write responsive CSS to a temp file for sed to use
    echo "$RESPONSIVE_CSS" > /tmp/responsive_css_block.txt
    
    # Use python for reliable insertion
    python3 -c "
import sys
filepath = sys.argv[1]
css = sys.argv[2]
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
# Insert before last </style>
idx = content.rfind('</style>')
if idx == -1:
    # Try </head>
    idx = content.find('</head>')
    if idx == -1:
        print('NO_STYLE_OR_HEAD: ' + filepath)
        sys.exit(1)
    insertion = '<style>\n' + css + '\n</style>\n'
    content = content[:idx] + insertion + content[idx:]
else:
    content = content[:idx] + css + '\n' + content[idx:]
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')
" "$FILEPATH" "$RESPONSIVE_CSS"
    
    LINES_AFTER=$(wc -l < "$FILEPATH")
    ADDED=$((LINES_AFTER - LINES_BEFORE))
    echo "✅ $f: +$ADDED lines (inserted before </style> at line $STYLE_LINE)"
  else
    echo "❌ NO </style> FOUND: $f"
  fi
done

echo "================================"
echo "Done!"
