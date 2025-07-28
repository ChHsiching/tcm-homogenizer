#!/bin/bash

# 中药多组分均化分析客户端 - 开发环境启动脚本

set -e

echo "🚀 启动中药多组分均化分析客户端开发环境..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查后端虚拟环境
BACKEND_VENV="$PROJECT_ROOT/backend/venv"
if [ ! -d "$BACKEND_VENV" ]; then
    echo "❌ 后端虚拟环境不存在，请先运行 setup-dev.sh"
    exit 1
fi

# 检查前端node_modules
FRONTEND_NODE_MODULES="$PROJECT_ROOT/frontend/node_modules"
if [ ! -d "$FRONTEND_NODE_MODULES" ]; then
    echo "❌ 前端依赖不存在，请先运行 setup-dev.sh"
    exit 1
fi

# 清理旧的PID文件
rm -f .backend.pid .frontend.pid

# 启动后端服务
echo "📡 启动后端服务..."
cd backend

# 激活虚拟环境
echo "🔧 激活Python虚拟环境..."
source venv/bin/activate

# 检查Python依赖
echo "📦 检查Python依赖..."
python -c "import flask, pandas, numpy, sklearn" 2>/dev/null || {
    echo "❌ Python依赖不完整，请运行: pip install -r requirements.txt"
    exit 1
}

# 启动后端服务
echo "🚀 启动Flask后端服务..."
nohup python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端服务是否正常
echo "🔍 检查后端服务状态..."
if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "❌ 后端服务启动失败"
    echo "📋 检查后端日志:"
    tail -n 10 backend.log
    echo ""
    echo "🔧 可能的解决方案:"
    echo "   1. 检查端口5000是否被占用: lsof -i :5000"
    echo "   2. 检查Python依赖: pip install -r requirements.txt"
    echo "   3. 检查虚拟环境: source venv/bin/activate"
    exit 1
fi

# 启动前端服务
echo "🖥️  启动前端服务..."
cd ../frontend

# 检查Node.js版本
echo "🔧 检查Node.js环境..."
NODE_VERSION=$(node --version 2>/dev/null || echo "not found")
echo "📦 Node.js版本: $NODE_VERSION"

# 检查npm依赖
echo "📦 检查npm依赖..."
if [ ! -f "package-lock.json" ]; then
    echo "❌ 前端依赖未安装，请运行: npm install"
    exit 1
fi

# 启动前端服务
echo "🚀 启动Electron前端应用..."
npm start &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

# 保存进程ID
echo $BACKEND_PID > ../.backend.pid
echo $FRONTEND_PID > ../.frontend.pid

echo ""
echo "🎉 开发环境启动完成！"
echo "📡 后端服务: http://127.0.0.1:5000"
echo "🖥️  前端应用: Electron 窗口"
echo ""
echo "💡 提示:"
echo "   - 使用 Ctrl+C 停止服务"
echo "   - 查看后端日志: tail -f backend/backend.log"
echo "   - 停止服务: ./scripts/stop-dev.sh"
echo ""

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f ../.backend.pid ../.frontend.pid; echo "✅ 服务已停止"; exit 0' INT

wait 