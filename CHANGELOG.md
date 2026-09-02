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

## 2026-09-02 · 角色级商用诊断（六族全链路测试）

**测试矩阵**：执法/企业/公众/监督四账号登录实测 + 新角色注册链 + 匿名边界 = 六族覆盖

**发现并修真 4 处**：
1. **RBAC 缺失（P1）**：高危写操作只验 token 不验角色——企业/公众 token 可处置执法告警。补角色白名单门（403 权限不足）
2. **roleName 兜底**：API 直调注册/历史用户 role_name 空 → db_layer 注册与登录双兜底（roles 表回查回写）
3. **脱敏白名单不一致**：脱敏白名单（5角色）与 RBAC 白名单不同步——监督角色看不了联系人。统一为 16 角色集
4. **KB 缺口**：「怎么举报偷排」miss（公众高频问题）→ 补《环境违法举报指南》入库（KB 274 条）

**终验 12/12 全绿**：执法四步链（清单→教练→落库→文书）/ 企业自检（快检+风险画像）/ 公众举报问答 direct / 监督监控双端点 / 检测标准库 / 科研目录 / 运维设备通道

**权限矩阵实测**：
| 角色 | 登录 | 浏览 | 高危写 | 联系人 |
|------|------|------|--------|--------|
| 执法 | ✓ | ✓ | ✓ | 完整 |
| 监督 | ✓ | ✓ | ✓ | 完整 |
| 企业 | ✓ | ✓ | 403 | 掩码 |
| 公众 | ✓ | ✓ | 403 | 掩码 |
| 运维 | ✓ | ✓ | 403 | 掩码 |
| 匿名 | — | ✓ | 401 | 掩码 |

## 2026-09-03 · 规划任务全面完成

- **科研数据集目录**：8 套平台真实脱敏资产（iot 112万条时序/案例120/法规35/标准37/企业50画像/KB 274/违法映射33/预警记录）入库 + /api/research/datasets + research-data 页真数据接入
- **landing.html 截断损坏修复**：发现文件在历史提交中被截断（26KB 无闭合）——git 恢复 + 二进制安全重写（37KB 完整，真数据入口保留）
- **sys-console/eco-manager 真值化**：控制台统计接 /api/health（81 API/69 页实时）；环保管家演示数据标注 + 任务/告警两卡真数据
- **voice-coach 69/69 全站覆盖**
- **终态**：81 API · 69 页 · 问答 direct P95<10ms · RBAC 六族实测 · 商用三要素闭环

## 2026-09-03 · 全角色闭环建设（入企采集 + 专业报告 + KB 补库）

1. **企业环保 KB 补库 6 条**（280 条）：台账体系/自行监测/危废全流程/许可执行报告/应急预案演练/环评三同时——每条含法条依据+操作规范+执法检查要点
2. **入企语音采集引擎**（intake_engine.py）：口语 → 结构化台账（药剂投加/水量/监测数据/设备启停/异常事件/危废转移 6 类），时段识别；POST /api/voice_intake 解析+落库；GET /api/ledger/recent 查询
3. **env-ledger.html 重建**：语音采集工作台（麦克风连续聆听 + 文字输入 + 解析预览 + 一键记台账 + 台账实时列表）
4. **企业环保运行报告**（POST /api/enterprise_report）：台账汇总/监测达标评估（联动排放标准限值）/合规风险/整改建议四部分 + docx 下载
5. **role-hub.html 角色工作台**：四族 17 个闭环工具入口 + 登录态感知；login 默认落地改为 role-hub
6. **问答评分修真**：企业管理/公众服务类别加权 + 核心词标题命中加成——7/7 问题命中（5 direct）
