# 🏥 环保执法助手系统 — 迁移体检报告

> 审查日期：2026-06-23 | 审查员：AutoClaw | 项目路径：`projects/epb-assistant/`

---

## 一、系统概述

**系统名称：** 环保智慧执法平台（EPB Assistant v2.0）

**定位：** 面向基层环保执法人员的智能执法支持系统，覆盖案件分析、法规查询、文书生成、培训学习、物联感知、成果展示等8大模块。

**技术栈：**
- 前端：原生 HTML + CSS + JS（9个页面，总计约 6,069 行）
- 后端：Python `http.server`（端口 8899）
- 数据：JSON 文件存储（无数据库依赖）
- 脚本：Python（文书生成、智能分析、视频生成等）+ Node.js（爬虫）
- 总体积：约 1.2 MB

**从旧路径迁移：** `~/.qclaw/workspace/skills/epb-assistant/` → `projects/epb-assistant/`

---

## 二、文件清单和完整性检查

### 2.1 根目录文档（4 文件）

| 文件 | 大小 | 状态 |
|------|------|------|
| `SKILL.md` | 3.9 KB | ✅ 存在，内容完整 |
| `REQUIREMENTS_DESIGN.md` | 11.8 KB | ✅ 存在，v3.1 设计文档完整 |
| `UPGRADE_PLAN.md` | 8.7 KB | ✅ 存在，架构规划完整 |
| `prompt.md` | 5.1 KB | ✅ 存在，AI 系统提示词完整 |

### 2.2 知识库 Markdown（2 文件）

| 文件 | 大小 | 状态 |
|------|------|------|
| `环保执法案例库.md` | 25.4 KB | ✅ 存在 |
| `环保局知识库.md` | 6.8 KB | ✅ 存在 |

### 2.3 web/ 目录（10 文件 + 1 备份 + 1 文档 + 1 脚本）

| 文件 | 行数 | 大小 | 状态 |
|------|------|------|------|
| `index.html` | 1,212 | 93 KB | ✅ 平台首页，7模块导航+8科室+全局搜索 |
| `field-terminal.html` | 1,812 | 74 KB | ✅ 现场执法终端，场景AI+语音+证据 |
| `admin.html` | 1,041 | 41 KB | ✅ 行政管理页面 |
| `knowledge.html` | 577 | 41 KB | ✅ 知识库页面 |
| `video-studio.html` | 306 | 21 KB | ✅ AI视频工作台 |
| `iot.html` | 268 | 25 KB | ✅ 物联感知页面 |
| `workspace.html` | 487 | 24 KB | ✅ 工作台页面 |
| `training.html` | 281 | 15 KB | ✅ 培训学院页面 |
| `analysis.html` | 85 | 7 KB | ✅ AI分析页面 |
| `field-terminal.html.bak` | — | 45 KB | ⚠️ 备份文件，建议清理 |
| `KNOWLEDGE_OPTIMIZE_README.md` | — | 6 KB | ⚠️ 优化说明文档，含旧路径 |
| `optimize_knowledge.py` | — | 15 KB | ⚠️ 一次性优化脚本，含旧硬编码路径 |

### 2.4 db/ 目录（8 数据文件 + 1 日志 + 1 知识库）

| 文件 | 大小 | 数据量 | JSON 校验 | 状态 |
|------|------|--------|-----------|------|
| `cases.json` | 41 KB | 40 条案例 | ✅ 通过 | 主案例库 |
| `law_index.json` | 43 KB | 21 部法律、30 关联案例 | ✅ 通过 | 法规索引 |
| `knowledge_graph.json` | 14 KB | 9 分类 | ✅ 通过 | 知识图谱 |
| `law_mapping.json` | 12 KB | 8 违法类型、3 风险等级 | ✅ 通过 | 法条映射 |
| `cases_new_20260527.json` | 13 KB | — | ❌ **JSON 语法错误** | 第230行逗号缺失 |
| `cases_new_20260527_fixed.json` | 13 KB | 10 条案例 | ✅ 通过 | 修复版 |
| `case-id-counter.txt` | 10 B | `20260420,1` | — | ✅ 案件编号计数器 |
| `scraper-log.txt` | 5.2 KB | 30+ 条日志 | — | ✅ 抓取日志 |
| `移动源监管知识库_20260421.md` | 13 KB | — | — | ✅ 专项知识库 |

### 2.5 scripts/ 目录（7 脚本 + 1 日志）

| 文件 | 行数 | 大小 | 状态 |
|------|------|------|------|
| `file_server.py` | 1,095 | 55 KB | ✅ 核心服务器，24个API端点 |
| `doc_generator.py` | 577 | 26 KB | ✅ 文书生成器（Word） |
| `training_content.py` | 541 | 27 KB | ✅ 培训内容库 |
| `ppt_generator.py` | 405 | 19 KB | ✅ PPT生成器 |
| `smart_analyzer.py` | 380 | 13 KB | ✅ 智能案件分析器 |
| `video_generator.py` | 275 | 9.5 KB | ✅ 视频脚本生成器 |
| `pdf_generator.py` | 229 | 13 KB | ✅ PDF生成器 |
| `server.log` | — | 5.6 KB | ⚠️ 旧运行日志，建议清理 |

### 2.6 scraper/ 目录（2 文件）

| 文件 | 大小 | 状态 |
|------|------|------|
| `run.js` | 9.5 KB | ✅ Node.js 抓取脚本，239行 |
| `sources.json` | 3.4 KB | ⚠️ 含7个本地 file:// PDF路径（旧机器路径） |

### 2.7 outputs/ 目录（13 文件）

| 类型 | 数量 | 状态 |
|------|------|------|
| PDF | 6 个 | ✅ 均为有效 PDF v1.4 |
| DOCX | 2 个 | ✅ 有效 OOXML |
| PPT/PPTX | 4 个 | ✅ 有效 OOXML |
| JSON | 1 个 (videos/) | ✅ 视频脚本数据 |

### 2.8 docs/ 目录（11 文档）

| 文档 | 日期 | 状态 |
|------|------|------|
| `epb-frontend-optimization_20260420.md` | 04-20 | ✅ 前端优化记录 |
| `epb-optimization-plan_20260518.md` | 05-18 | ✅ 优化计划 |
| `epb-optimization-completed_20260518.md` | 05-18 | ✅ 优化完成报告 |
| `epb-homepage-20260526.md` | 05-26 | ✅ 首页重构记录 |
| `epb-portal-optimize_20260526.md` | 05-26 | ✅ 门户优化 |
| `epb-admin-optimize_20260526.md` | 05-26 | ✅ 行政管理优化 |
| `epb-enhancement-20260526.md` | 05-26 | ✅ 功能增强 |
| `epb-scene-recognition-implementation_20260526.md` | 05-26 | ✅ 场景识别实现 |
| `epb-scraper-daily_20260618.md` | 06-18 | ✅ 爬虫日报 |
| `epb-scraper-daily-report_2026-06-20.md` | 06-20 | ✅ 爬虫日报 |
| `epb-scraper-daily_20260621.md` | 06-21 | ✅ 爬虫日报 |

### 2.9 空目录

| 目录 | 状态 |
|------|------|
| `analyzer/` | ⚠️ 空目录，无任何文件 |
| `uploads/` | ⚠️ 空目录（运行时自动生成上传文件） |

### 2.10 knowledge/ 目录

❌ **不存在**。`REQUIREMENTS_DESIGN.md` 和 `UPGRADE_PLAN.md` 中规划了开源知识库模块，但 `knowledge/` 目录尚未创建。当前知识库以根目录的 Markdown 文件和 `db/` 下的 JSON 文件代替。

---

## 三、发现的问题（按严重程度分级）

### 🔴 严重问题（3 项）

#### P1-1. SKILL.md 中硬编码旧绝对路径

**文件：** `SKILL.md` 第19行、第29行

**问题：**
```
法规体系库：/Users/tom/.qclaw/workspace/环保执法案例库.md
cd ~/Library/Application\ Support/QClaw/openclaw/workspace/skills/epb-assistant/scripts
```

**影响：** 系统提示词引用了旧路径 `/Users/tom/.qclaw/workspace/`，AI 助手按照此路径将无法找到文件。启动命令也指向旧路径 `~/Library/Application Support/QClaw/...`。

**修复：**
- 路径改为相对路径或当前项目路径：`../环保执法案例库.md`（相对于 `db/` 目录）或 `环保执法案例库.md`（相对于项目根目录）
- 启动命令改为：`cd projects/epb-assistant/scripts && python3 file_server.py`

---

#### P1-2. prompt.md 中多处硬编码旧绝对路径

**文件：** `prompt.md` 第15-17行

**问题：**
```
法规体系库：/Users/tom/.qclaw/workspace/环保执法案例库.md
案例数据库：/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/db/cases.json
辅助知识库：/Users/tom/.qclaw/workspace/环保局知识库.md
```

**影响：** AI 系统提示词中引用的三个核心知识库路径全部指向旧路径，将导致运行时文件找不到。

**修复：** 改为相对路径：
```
法规体系库：环保执法案例库.md
案例数据库：db/cases.json
辅助知识库：环保局知识库.md
```

---

#### P1-3. web/optimize_knowledge.py 硬编码旧绝对路径

**文件：** `web/optimize_knowledge.py` 第10行、第298行、第309行

**问题：**
```python
with open('/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/web/knowledge.html', 'r', encoding='utf-8') as f:
```

**影响：** 此脚本运行将直接报 `FileNotFoundError`。

**修复：** 改为相对路径 `os.path.join(os.path.dirname(__file__), 'knowledge.html')` 或直接 `'knowledge.html'`。考虑到此为一次性优化脚本，建议标记为归档或删除。

---

### 🟡 中等问题（5 项）

#### P2-1. cases_new_20260527.json JSON 语法错误

**文件：** `db/cases_new_20260527.json` 第230行

**问题：** JSON 解析失败，第230行附近存在未转义的双引号或逗号缺失。具体位置在 `"fact"` 字段值中的中文引号 `"绿水青山就是金山银山"` 内嵌了未转义的英文双引号。

**影响：** 任何尝试加载此文件的程序将崩溃。已有修复版 `cases_new_20260527_fixed.json`，但原文件仍保留。

**修复：** 删除 `cases_new_20260527.json`，保留 `_fixed` 版本并重命名；或修复原文件中的 JSON 语法。

---

#### P2-2. scraper/sources.json 含本地 file:// 绝对路径

**文件：** `scraper/sources.json` 第57-99行

**问题：** 7个数据源使用了 `file:///Users/tom/Desktop/标准/...` 格式的本地路径，指向旧机器桌面上的 PDF 文件。

**影响：** 迁移后这些路径不存在，爬虫抓取这些源将失败。从日志看，自4月底起这些源已持续失败。

**修复：**
- 将相关 PDF 文件迁移到项目 `db/standards/` 目录下，更新路径为相对路径
- 或删除这些本地源，仅保留在线源
- 日志显示在线源也多数不可达，建议审查 sources.json 中所有数据源的有效性

---

#### P2-3. SKILL.md 中 cron ID 引用可能失效

**文件：** `SKILL.md` 第32行

**问题：** `cron ID: 72a873ac-7e71-4503-a3b8-7be1aba76f47` 引用了旧系统中的定时任务ID。

**影响：** 迁移后旧 cron 任务可能已失效，需在当前环境重新配置。

**修复：** 确认旧 cron 是否仍在运行；如已失效，使用 `im_remind` 工具重新创建每天 09:00 的抓取定时任务，并更新 SKILL.md 中的 cron ID。

---

#### P2-4. docs/ 文档中大量旧路径引用

**涉及文件：** `docs/` 下至少 6 个文档文件

**问题：** 文档中多处引用 `/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/...` 和 `~/.qclaw/workspace/skills/epb-assistant/...`。

**影响：** 文档作为历史记录，不影响运行时，但会误导开发者。

**修复：** 在文档头部添加迁移说明注释，或批量替换路径。低优先级。

---

#### P2-5. SKILL.md 中知识库路径引用 `skills/epb-assistant/` 相对路径

**文件：** `SKILL.md` 第20-26行

**问题：**
```
案例数据库：skills/epb-assistant/db/cases.json
智能分析模块：skills/epb-assistant/scripts/smart_analyzer.py
Web界面：skills/epb-assistant/web/index.html
```

**影响：** 这些路径假设从 workspace 根目录执行，迁移后项目位于 `projects/epb-assistant/`，旧相对路径不再正确。

**修复：** 统一改为 `projects/epb-assistant/db/cases.json` 等正确相对路径。

---

### 🟢 轻微问题（6 项）

#### P3-1. field-terminal.html.bak 备份文件残留

**文件：** `web/field-terminal.html.bak`（45 KB）

**说明：** 旧版本备份，不影响运行，但增加项目体积。

**修复：** 删除或移到 `docs/archive/`。

---

#### P3-2. scripts/server.log 旧日志文件

**文件：** `scripts/server.log`（5.6 KB）

**说明：** 最后一条日志为 2026-04-21，迁移后无意义。

**修复：** 清空或删除，运行时自动生成。

---

#### P3-3. analyzer/ 空目录

**说明：** 目录存在但无任何文件，可能是规划中的模块。

**修复：** 如暂不使用，删除目录；如规划中，添加 `README.md` 说明用途。

---

#### P3-4. knowledge/ 目录缺失

**说明：** `UPGRADE_PLAN.md` 规划了开源知识库模块，但 `knowledge/` 目录未创建。根目录的 `环保局知识库.md` 和 `环保执法案例库.md` 作为临时替代。

**修复：** 创建 `knowledge/` 目录，将两个 Markdown 文件移入，按规划建立结构化知识库。

---

#### P3-5. field-terminal.html 中存在冗余 fetch 调用

**文件：** `web/field-terminal.html` 第1273行

**问题：**
```javascript
const caseData = await lawResp.ok ? await fetch('/api/search_cases', {
```
此处用 `lawResp.ok` 判断是否搜索案例，逻辑上应该用 `lawData.ok` 或独立判断。此外第1268行已获取了 `caseResp`，第1273行又重复 fetch 了一次相同的接口。

**影响：** 不影响功能（结果正确），但产生了一次冗余 HTTP 请求。

**修复：** 统一使用第一次 fetch 的 `caseResp` 结果。

---

#### P3-6. PDF 输出文件均为 1 页且体积很小（~2 KB）

**说明：** `outputs/` 目录下 6 个 PDF 文件均为 1 页、约 2 KB，疑似为测试生成或模板占位文件。

**修复：** 确认是否为有效产出。如为测试文件，可清理。

---

## 四、修复建议（按优先级）

### 立即修复（阻断运行）

| # | 操作 | 文件 |
|---|------|------|
| 1 | 将 `SKILL.md` 中 `/Users/tom/.qclaw/workspace/环保执法案例库.md` 改为 `环保执法案例库.md` | `SKILL.md` |
| 2 | 将 `SKILL.md` 中启动命令改为 `cd projects/epb-assistant/scripts && python3 file_server.py` | `SKILL.md` |
| 3 | 将 `SKILL.md` 中 `skills/epb-assistant/` 前缀全部改为 `projects/epb-assistant/` | `SKILL.md` |
| 4 | 将 `prompt.md` 中三个绝对路径改为相对路径 | `prompt.md` |
| 5 | 修复或删除 `web/optimize_knowledge.py` 中的硬编码路径 | `web/optimize_knowledge.py` |

### 尽快修复（数据一致性）

| # | 操作 | 文件 |
|---|------|------|
| 6 | 删除损坏的 `cases_new_20260527.json`，将 `_fixed` 版本重命名 | `db/` |
| 7 | 清理 `scraper/sources.json` 中的 `file:///Users/tom/Desktop/...` 路径 | `scraper/sources.json` |
| 8 | 确认 cron 定时任务状态，必要时重新创建 | `SKILL.md` + cron |

### 优化清理（非紧急）

| # | 操作 | 文件 |
|---|------|------|
| 9 | 删除 `web/field-terminal.html.bak` | `web/` |
| 10 | 清空 `scripts/server.log` | `scripts/` |
| 11 | 删除或归档 `web/optimize_knowledge.py` 和 `web/KNOWLEDGE_OPTIMIZE_README.md` | `web/` |
| 12 | 删除空目录 `analyzer/` 或添加 README | 根目录 |
| 13 | 审查 `outputs/` 中的小 PDF 是否为有效产出 | `outputs/` |

---

## 五、优化建议（按专业系统标准）

### 架构层面

1. **路径管理统一化** — 在 `file_server.py` 顶部已使用 `os.path.dirname(__file__)` 做相对路径（✅ 良好），但 `SKILL.md` 和 `prompt.md` 仍使用硬编码路径。建议创建 `config.py` 统一管理路径常量，所有脚本和文档引用配置文件。

2. **前端模块化** — 当前 9 个 HTML 文件均为内联 CSS+JS，`index.html` 达 93 KB / 1212 行。建议：
   - 提取公共 CSS 到 `web/css/common.css`
   - 提取公共 JS 到 `web/js/common.js`
   - 长期按 `UPGRADE_PLAN.md` 规划迁移至 Vue3 + Arco Design

3. **API 方法一致性** — `search_cases` 和 `search_laws` 在 `file_server.py` 中注册在 `do_POST`，但 `REQUIREMENTS_DESIGN.md` 标注为 `GET` 方法。建议统一文档与实现。

4. **数据层升级** — 当前使用 JSON 文件存储，案例增长后查询性能受限。建议按 `UPGRADE_PLAN.md` 规划迁移至 SQLite（轻量）或 PostgreSQL（生产）。

### 安全层面

5. **路径穿越防护** — `file_server.py` 第69行直接拼接用户输入的路径 `rel` 到 `WEB_DIR`，存在路径穿越风险。建议添加 `os.path.realpath()` 检查和 `..` 过滤。

6. **CORS 配置** — 当前 `Access-Control-Allow-Origin: *`，本地服务可接受，但如部署到网络环境需收紧为 `localhost` 或特定域名。

7. **文件上传安全** — 上传文件名仅做了 `safe_name` 处理（第175行），建议增加文件类型白名单校验和文件大小限制。

### 运维层面

8. **日志轮转** — `server.log` 无大小限制，长期运行会持续增长。建议使用 Python `logging.handlers.RotatingFileHandler`，限制单文件 1 MB、保留 3 个备份。

9. **健康检查端点** — 建议添加 `/api/health` 端点，返回服务状态、数据文件完整性、案例数量等，便于监控。

10. **进程管理** — 当前使用 `HTTPServer` 直接运行，建议添加 `launchd` 或 `systemd` 服务管理，实现开机自启和崩溃自动重启。

11. **爬虫维护** — 从日志看，自 4 月中旬起抓取成功率极低（几乎全部失败）。建议：
   - 审查 `sources.json` 中所有 URL 的可达性
   - 更新页面解析逻辑以适应网站改版
   - 添加失败告警通知机制

### 数据层面

12. **案例库去重与合并** — 存在 `cases.json`（40条）、`cases_new_20260527_fixed.json`（10条）两个数据源。建议合并去重为一个权威数据文件。

13. **知识库结构化** — 按规划创建 `knowledge/` 目录，将 Markdown 知识库结构化为 JSON/SQLite，支持全文检索和关联查询。

14. **数据备份** — `db/` 目录下的 JSON 文件是核心资产，建议添加 Git 版本控制和定期备份机制。

---

## 六、迁移路径适配总结

| 旧路径 | 新路径 | 需修改文件数 |
|--------|--------|-------------|
| `/Users/tom/.qclaw/workspace/环保执法案例库.md` | `环保执法案例库.md`（项目根） | 2 (SKILL.md, prompt.md) |
| `/Users/tom/.qclaw/workspace/环保局知识库.md` | `环保局知识库.md`（项目根） | 1 (prompt.md) |
| `/Users/tom/.openclaw-autoclaw/workspace/projects/epb-assistant/...` | `projects/epb-assistant/...` | 4 (SKILL.md, prompt.md, optimize_knowledge.py, docs/*) |
| `~/Library/Application Support/QClaw/openclaw/workspace/skills/epb-assistant/scripts` | `projects/epb-assistant/scripts` | 1 (SKILL.md) |
| `file:///Users/tom/Desktop/标准/*.pdf` | 迁移 PDF 文件或删除源 | 1 (scraper/sources.json) |

**需修改的运行时关键文件：3 个**（SKILL.md、prompt.md、optimize_knowledge.py）
**需修改的文档文件：6+ 个**（docs/ 下的旧路径引用）

---

## 七、总体评价

| 维度 | 评分 | 说明 |
|------|------|------|
| 文件完整性 | ⭐⭐⭐⭐ | 核心文件齐全，1个JSON损坏，2个空目录 |
| 路径适配 | ⭐⭐ | **主要扣分项**，3个运行时文件含旧硬编码路径 |
| 代码质量 | ⭐⭐⭐⭐ | Python 脚本使用了 `os.path.dirname(__file__)` 相对路径，架构清晰 |
| 前端完整性 | ⭐⭐⭐⭐⭐ | 9个页面全部存在，内联CSS/JS无外部依赖，引用路径正确 |
| 数据完整性 | ⭐⭐⭐⭐ | 主数据文件均有效，1个辅助文件损坏（有修复版） |
| 文档完整性 | ⭐⭐⭐⭐ | 11个优化文档完整记录迭代历史 |
| 安全性 | ⭐⭐⭐ | 本地使用可接受，部署前需加强 |

**总结：** 系统文件迁移基本完整，核心资产（代码、数据、前端页面）均已到位。**最紧急的问题是 3 个运行时文件中的旧硬编码绝对路径**，不修复将导致 AI 助手无法定位知识库文件和启动服务。修复工作量约 15 分钟，修改 3 个文件即可恢复运行。

---

_报告生成：2026-06-23 14:51 | AutoClaw 系统迁移审查_
