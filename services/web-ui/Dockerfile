# Web UI Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY web-ui/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制 session_manager 模块
COPY session_manager/ /app/session_manager/

# 复制应用代码
COPY web-ui/ .

# 创建数据目录
RUN mkdir -p /app/data/sessions

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
