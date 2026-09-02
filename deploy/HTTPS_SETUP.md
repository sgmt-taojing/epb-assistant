# HTTPS 部署方案（商用必补④）

## 方案：Caddy 反向代理（自动 TLS，零配置证书）

### 1. 安装
```bash
brew install caddy          # macOS
# Linux: apt install caddy
```

### 2. Caddyfile 配置

内网自签（无域名）：
```
:8443 {
    reverse_proxy 127.0.0.1:8899
    tls internal
}
```

公网域名（自动 Let's Encrypt）：
```
epb.example.com {
    reverse_proxy 127.0.0.1:8899
    encode gzip
    header Strict-Transport-Security "max-age=31536000"
}
```

### 3. 启动
```bash
caddy start --config Caddyfile
```

### 4. 语音能力增强说明
Web Speech API 在 HTTP 下仅 localhost 可用；HTTPS 后全域名解锁，语音教练/实时交互随之增强。

### 5. 上线检查单
- [ ] curl https://127.0.0.1:8443/api/health 通过
- [ ] 前端已全站相对路径（无硬编码 http:// ✓）
- [ ] TTS 8912 / face-ocr 8913 保持内网，不暴露公网
- [ ] caddy 交 launchd 守护
