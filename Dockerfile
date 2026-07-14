FROM python:3.9-slim

LABEL maintainer="EPB Assistant"
LABEL description="环保智慧执法平台 - 开源版"

WORKDIR /app

# 复制项目文件
COPY scripts/ ./scripts/
COPY web/ ./web/
COPY db/ ./db/
COPY api-data/ ./api-data/
COPY scraper/ ./scraper/
COPY docs/ ./docs/

# 安装依赖
RUN pip install --no-cache-dir

# 暴露端口
EXPOSE 8900

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8900
ENV HOST=0.0.0.0

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8900/api/health')" || exit 1

# 启动命令
CMD ["python3", "scripts/file_server.py"]
