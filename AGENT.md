# epb-assistant · 项目智能体工作台（AGENT.md）

> 2026-08-17 项目 agent 化体系 · 2026-08-31 全量盘点修真（对齐真实资产） · 总指挥：主 agent（AutoClaw）

## 一、身份与职责
- **角色**：环保智慧执法
- **核心功能**：执法助手/案例检索/知识库
- **场景边界**：仅环保执法场景

## 二、知识获取（按规范 V1.0 单一源头）
| 通道 | 说明 |
|------|------|
| 蒸馏知识 | 按蒸馏 SOP v4.1 单向获取（溯源标记 source_project/source_id） |
| 共享组件 | `projects/_shared/`（MASTER-SPEC/规范/复用矩阵） |
| 本地数据 | 自有 KB（distill 修真后写自有库） |

## 三、服务（2026-08-31 核实）
| 入口 | 端口 | 说明 |
|------|------|------|
| `scripts/file_server.py`（生产主入口） | 8899（config.json） | launchd 常驻：`com.epb.assistant.http`；绑 127.0.0.1 |
| 同上，PORT 环境变量覆盖 | 8900（Docker）/ 8944（deploy.sh） | Dockerfile ENV PORT=8900；deploy.sh PORT=8944 |
| `app/server.py`（Flask 完整版） | 8900 | venv 内运行；file_server 会自动挂载其蓝图路由 |

## 四、自检命令
```bash
bash scripts/agent-selfcheck.sh          # 10 项全量自检（语法/品牌/密钥/端口/健康）
venv/bin/python -m pytest tests/ -q      # API 测试（29 用例）
```

## 五、建设规范
1. 独立品牌/数据/部署（独立商用五要素 READY）
2. 知识单向获取（禁止逆向覆盖源头）
3. 敏感数据 gitignore 本地保留
4. 场景隔离（能力复用矩阵红线）
5. 验收纳入 capability-acceptance / KPI【2.7】

## 训练资产现状（2026-08-31 盘点 · 以实际存在为准）

- **自有 KB**：`db/epb.db` → `kb_formal` 表（70 条，module=epb-assistant）+ 101 案例 + 28 法规
- **蒸馏脚本**：`scripts/distill-epb-to-kb.py`（EPB 案例单向蒸馏入自有 kb_formal，R118-G3 修真后不再写 mingli 主库）
- **业务培训**：`scripts/training_content.py`（执法人员课程内容，非模型训练）
- **未建**：`training-data/`（SFT 数据）、`models/`（微调权重）暂不存在——如未来启动环保领域模型微调，按蒸馏红线 v2 + 学习三化 SOP 走：自有 KB → SFT/DPO 构建 → 本地微调 → 评估达标 → 上生产

## 关键路径速查（2026-08-31 核实修正）

- **生产服务**：`scripts/file_server.py`（端口 8899，launchd 常驻）
- **Flask 路由层**：`app/routes/`（auth/api/diagnostic/case_workflow）
- **前端入口**：`web/`（62 页面）
- **蒸馏脚本**：`scripts/distill-epb-to-kb.py`（外部法规 → 自有 KB）
- **部署**：`deploy.sh`（PORT=8944）/ `Dockerfile`（PORT=8900）/ GitHub Pages（api-data 静态回退）
