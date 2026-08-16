# 🌿 环保智慧执法平台 (EPB Assistant)

> 知识驱动 · AI闭环 · 天地一体 · 开源开放 — 面向公众·企业·政府·监管·执法五位一体

## 平台概览

| 指标 | 数值 |
|------|------|
| 功能页面 | 32 |
| API端点 | 19 |
| Python脚本 | 14 |
| 执法案例 | 101 |
| 环保法规 | 28 |
| 设备产品 | 14 |
| 环保领域 | 7 |
| 部署通道 | 3 |

## 快速开始

### 方式一：本地运行（最简单）

```bash
cd epb-assistant
python3 scripts/file_server.py
# 访问 http://127.0.0.1:8900
```

### 方式二：Docker部署

```bash
cd epb-assistant
docker build -t epb-assistant .
docker run -d -p 8900:8900 --name epb-assistant epb-assistant
# 访问 http://localhost:8900
```

### 方式三：Docker Compose

```bash
cd epb-assistant
docker-compose up -d
# 访问 http://localhost:8900
```

### 方式四：GitHub Pages（静态只读）

访问 https://sgmt-taojing.github.io/epb-assistant/

## 功能模块

### 核心模块（22个基础页面）

| 模块 | 页面 | 说明 |
|------|------|------|
| 平台首页 | index.html | 六位一体总入口 |
| 仪表盘 | dashboard.html | 数据总览 |
| 现场执法终端 | field-terminal.html | AI场景识别+文书生成 |
| 知识库 | knowledge.html | 法规+案例+标准 |
| IoT监测 | iot.html | 物联感知 |
| 设备管理 | device-mgmt.html | 设备台账 |
| 管理后台 | admin.html | 系统管理 |
| 举报入口 | report.html | 群众举报 |
| 企业EHS | ehs.html | 企业环保管理 |
| 监管预警 | supervision.html | 非现场监管 |
| 协同平台 | collaboration.html | 政企协查闭环 |
| 合规自查 | self-check.html | 企业自查 |
| AI分析 | analysis.html | 智能案件分析 |
| 培训学院 | training.html | 环保培训 |
| 视频工作台 | video-studio.html | AI视频生成 |
| 工作空间 | workspace.html | 日常管理 |
| 登录注册 | login.html | 用户管理 |
| 微信H5 | wechat-h5.html | 微信入口 |
| 移动工作台 | m-workspace.html | 移动执法 |
| 移动举报 | m-report.html | 手机举报 |
| 移动案例 | m-cases.html | 案例查询 |
| 移动自查 | m-self-check.html | 移动合规 |

### 扩展模块（10个新增页面）

| 模块 | 页面 | 阶段 | 说明 |
|------|------|------|------|
| 设备商城 | equipment-mall.html | 一阶段 | 案例驱动·降本增效 |
| 自由裁量计算 | penalty-calculator.html | 一阶段 | 处罚金额自动计算 |
| 企业风险画像 | risk-profile.html | 一阶段 | 多维度风险评估 |
| 执法文书AI | doc-generator.html | 一阶段 | 4种文书自动生成 |
| AI周报月报 | ai-report.html | 二阶段 | 自动汇总+智能分析 |
| 非现场执法 | remote-enforcement.html | 二阶段 | 在线监测分析 |
| 环保信用评级 | credit-rating.html | 二阶段 | 绿蓝黄红标 |
| 天地一体感知 | sensor-dashboard.html | 三阶段 | 多源数据融合 |
| 智能预警系统 | smart-alert.html | 三阶段 | 规则引擎+AI研判 |
| 无人机巡查 | drone-patrol.html | 三阶段 | 航线+AI识别 |
| 平台总览看板 | overview.html | 四阶段 | 32模块总入口 |

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/health | GET | 健康检查 |
| /api/cases | GET | 案例列表 |
| /api/law_index | GET | 法规索引 |
| /api/law_mapping | GET | 法规映射 |
| /api/knowledge_graph | GET | 知识图谱 |
| /api/tasks | GET | 任务列表 |
| /api/task | POST | 创建任务 |
| /api/task/:id | GET/PUT | 任务详情/更新 |
| /api/roles | GET | 角色列表 |
| /api/users | GET | 用户列表 |
| /api/enterprises | GET | 企业名录 |
| /api/devices | GET | 设备列表 |
| /api/device_types | GET | 设备类型 |
| /api/tenant | GET | 租户配置 |
| /api/config | GET | 系统配置 |
| /api/search | GET | 全文搜索 |
| /api/report | GET/POST | 举报查询/提交 |
| /api/equipment | GET | 设备商城产品 |
| /api/equipment/:id | GET | 产品详情 |
| /api/equipment/categories | GET | 产品分类 |
| /api/fusion_alert | POST | 多源融合预警 |

## 技术栈

- **后端**: Python 3.9+ (标准库 HTTPServer)
- **数据库**: SQLite (epb.db)
- **前端**: 原生HTML + CSS + JavaScript (无框架依赖)
- **部署**: Docker / Docker Compose / GitHub Pages
- **开源协议**: MIT

## 项目结构

```
epb-assistant/
├── scripts/          # Python后端
│   ├── file_server.py    # 主服务器
│   ├── db_layer.py       # 数据库层
│   ├── init_db.py        # 数据库初始化
│   ├── equipment_data.py # 设备商城数据
│   └── smart_analyzer.py # AI分析引擎
├── web/              # 前端页面 (32个HTML)
├── db/               # SQLite数据库
├── api-data/         # 静态JSON数据 (GitHub Pages用)
├── scraper/          # 数据抓取
├── docs/             # 文档
├── Dockerfile        # Docker构建文件
├── docker-compose.yml# Docker Compose
└── README.md         # 本文件
```

## 开源协议

MIT License - 可自由使用、修改、分发
