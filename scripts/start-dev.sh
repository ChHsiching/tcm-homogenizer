#!/usr/bin/env bash
# 本草智配客户端 - 开发环境启动脚本

set -e

echo "🚀 启动本草智配客户端开发环境..."

# 启动后端
source backend/venv/bin/activate || true
cd backend && python main.py &
cd - >/dev/null

# 启动前端
cd frontend && npm start &
cd - >/dev/null

wait 