#!/bin/bash

# 中药多组分均化分析客户端开发环境启动脚本

echo "🚀 启动中药多组分均化分析客户端开发环境..."

# 检查是否在项目根目录
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 停止可能存在的进程
echo "🛑 停止可能存在的进程..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "electron.*frontend" 2>/dev/null
sleep 2

# 启动后端服务
echo "📡 启动后端服务..."

# 检查Python虚拟环境
if [ -d "backend/venv" ]; then
    echo "🔍 检查Python依赖..."
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt >/dev/null 2>&1
else
    echo "🔍 检查Python依赖..."
    cd backend
    python -m pip install -r requirements.txt >/dev/null 2>&1
    cd ..
fi

# 启动Flask后端服务
echo "🚀 启动Flask后端服务..."
cd backend
python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端服务状态
echo "🔍 检查后端服务状态..."
if curl -s http://127.0.0.1:5000/health >/dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "❌ 后端服务启动失败，请检查 backend.log"
    echo "📋 后端日志内容:"
    tail -20 backend.log
    exit 1
fi

cd ..

# 启动前端服务
echo "🖥️  启动前端服务..."

# 检查Node.js依赖
echo "🔍 检查Node.js依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 安装Node.js依赖..."
    npm install >/dev/null 2>&1
fi

# 启动Electron前端应用
echo "🚀 启动Electron前端应用..."
npm start >/dev/null 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

cd ..

# 等待服务完全启动
sleep 3

echo "🎉 开发环境启动完成！"
echo "📡 后端服务: http://127.0.0.1:5000"
echo "🖥️  前端应用: Electron 窗口"
echo ""
echo "💡 提示:"
echo "   - 使用 Ctrl+C 停止服务"
echo "   - 查看后端日志: tail -f backend/backend.log"
echo "   - 停止服务: ./scripts/stop-dev.sh"

# 保存PID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止服务..."; ./scripts/stop-dev.sh; exit 0' INT
wait 