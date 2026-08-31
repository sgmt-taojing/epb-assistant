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
