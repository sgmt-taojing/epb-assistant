# epb-assistant · 项目智能体工作台（AGENT.md）

> 2026-08-17 项目 agent 化体系 · 总指挥：主 agent（AutoClaw）

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

## 三、服务
| 端口 | 服务 | 说明 |
|------|------|------|
| 8944 静态服务（Dockerfile） | 独立部署（deploy.sh / Dockerfile） |

## 四、自检命令
```bash
bash scripts/agent-selfcheck.sh
```

## 五、建设规范
1. 独立品牌/数据/部署（独立商用五要素 READY）
2. 知识单向获取（禁止逆向覆盖源头）
3. 敏感数据 gitignore 本地保留
4. 场景隔离（能力复用矩阵红线）
5. 验收纳入 capability-acceptance / KPI【2.7】
