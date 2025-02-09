#!/bin/bash

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export UVICORN_PORT=8000
export UVICORN_HOST="0.0.0.0"

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 启动FastAPI服务
uvicorn podcast_agent.web.api:app \
    --host $UVICORN_HOST \
    --port $UVICORN_PORT \
    --reload \
    --log-level info
