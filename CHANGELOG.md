# epb-assistant 更新日志

## 2026-08-31 · 全量盘点修真（从第一行代码级审查）
- **修复致命 BUG**：web/field-terminal.html 第二个 script 块未闭合，浮动面板 HTML 被吞进脚本（整块 JS 语法错误，页面核心分析功能全失效）
- **安全修真**：移除 auth.py 硬编码后门（admin123）与硬编码 SECRET_KEY；改为 SHA-256 加盐哈希 + 环境变量密钥；登录失败统一文案防账号枚举
- **上传加固**：50MB 大小限制 + 扩展名白名单 + 文件名路径穿越防护（multipart 与 JSON 双通道）
- **端口统一**：file_server 支持 PORT 环境变量（本地 8899 / Docker 8900 / deploy 8944 一套代码三种部署）
- **部署修复**：Dockerfile 断裂命令（pip install 缺包名）补齐；deploy.sh 改指向真实入口 file_server.py
- **品牌隔离**：清除 4 处 mingli 残留（canonical/footer/两处 JS 契约注释）
- **测试链路**：venv 补 pytest+flask，测试用例适配新认证（29/29 通过）
- **自检升级**：agent-selfcheck.sh v2（10 项：健康/部署/页面/Py语法/JS语法/品牌/密钥/端口）
- **文档对齐**：AGENT.md 移除虚假目录约定（training-data/models/knowledge 实不存在），补真实资产清单与端口表

## 2026-08-16 · v1.0.0（商用就绪基线）
- 新增 LICENSE（专有软件许可 · 商用授权）
- 新增 COMPLIANCE.md（第三方依赖合规清单）
- 新增 DISCLAIMER.md（服务边界免责声明）
- 商用就绪度评分卡首评（详见 check-commercial-readiness.py）

## 2026-09-02 · 全面 AI 化（AI 现场教练 · 外行变专业）

### 新增核心能力
- **coach_engine.py 指导引擎**：把 33 类专业检查项翻译成外行 5 步闭环指令（去哪看→看什么→怎么判断→拍什么→问什么），法条自动匹配（同义归一：危险废物→危废等）
- **POST /api/coach/point**：单项 → 手把手指导卡（高风险项加急提示）
- **POST /api/coach/checklist**：整单 → 逐项指导 + 高风险优先路线
- **POST /api/voice_coach**：实时语音意图识别（7 类意图：coach/next_step/how_to/what_to_shoot/whom_to_ask/law/emergency），支持上下文模式（当前检查项感知）
- **voice-coach.js 全局教练层**：69 页全站注入——连续聆听 + /api/voice_coach + 本地 TTS 播报 + 断网本地兜底
- **inspection-workbench 指导卡**：每个检查项可展开「🧭 手把手指导」（位置/查法/拍照/话术/法条/异常处置 6 段式）+ 🔊 语音播报
- **realtime-assistant 教练入口**：AI 现场教练主入口卡（启动教练/检查工作台/智能问答/应急指导）

### 顺手修真
- my-certificates.html：document.write 内嵌套 </script> 提前截断内联脚本（历史遗留语法错误）
- admin.html：loadMonitorStats then 链缺闭合括号（历史遗留）
- 全站 69 页 JS 语法 100% 全绿（含历史遗留 2 处修复）

## 2026-09-02 · 断尾闭环（前序任务全部收口）

- **① 详情端点关联注入修真**：路由 key 单复数不一致（'case' vs 'cases'）导致关联永不触发 + laws 表列名错误（code→law_name）——修复后 cases 详情带关联任务 1 条 + 关联法条 4 条；tasks 三级企业名匹配（全片段→去地名核心词→标题兜底）；m-cases.html 详情面板接 API 异步渲染关联数据
- **② monitor-overview 业务流水卡**：案件/任务/举报三列实时数据（cases/recent + tasks/recent + reports/recent）
- **③ landing 真数据入口**：案件库/任务池/举报台三卡（120 案例·14 任务·12 举报）
- **④ kb_seed_v4_glasses 幂等入库确认**：5/6 条已在库（第 6 条为标准条目已在 formal），跳过确认
- **⑥ 眼镜教练同步投送**：voice_coach 支持 push_to_speaker → 8912 TTS 真合成播报（实测 102-237KB 音频）；voice-coach.js 加「同步推音箱/眼镜」开关，音箱已推则浏览器不重复播（防双声）

## 2026-09-02 · 商用必补四件套（审计后续任务闭环）

1. **Token 鉴权**：sessions 表（12h 过期）+ login 签发 + 7 个高危写操作 API 强制 Bearer token（无/假 token 401，浏览/问答保持开放）；前端 auth-guard 自动附 token
2. **角色脱敏**：/api/enterprises 联系人信息——匿名「林** / 150****0202」、执法角色完整可见（contact_masked 标志）
3. **问答质量监控**：/api/qa/health（miss 率 + 24h 窗口 + top miss 问题 + 阈值告警）；qa_log 增 tier 列；历史脏数据归档后基线 healthy 0%
4. **HTTPS 方案**：deploy/HTTPS_SETUP.md（Caddy 反代自动 TLS + 上线检查单）
