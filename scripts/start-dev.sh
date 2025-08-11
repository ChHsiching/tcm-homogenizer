#!/usr/bin/env bash
# 本草智配客户端 - 开发环境启动脚本

# 启动提示
echo "🚀 启动本草智配客户端开发环境..."

# 启动后端
cd backend && nohup python main.py > ../backend/backend.log 2>&1 &
cd - >/dev/null

# 启动前端（静态服务）
cd frontend && nohup python -m http.server 3000 > ../frontend/http.log 2>&1 &
cd - >/dev/null

echo "✅ 本草智配客户端开发环境已启动" 