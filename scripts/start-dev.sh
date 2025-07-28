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

# 检查前端依赖
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "❌ 前端依赖未安装，请先运行 setup-dev.sh"
    exit 1
fi

# 清理旧的PID文件
rm -f .backend.pid .frontend.pid

# 启动后端服务
echo "📡 启动后端服务..."
cd backend

# 激活虚拟环境
source venv/bin/activate

# 检查Python依赖
if ! python -c "import flask, pandas, numpy, sklearn" 2>/dev/null; then
    echo "❌ 后端Python依赖不完整，请先运行 setup-dev.sh"
    exit 1
fi

# 启动后端服务
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
    echo "💡 可能的解决方案:"
    echo "   - 检查端口5000是否被占用: lsof -i :5000"
    echo "   - 重新安装依赖: ./scripts/setup-dev.sh"
    echo "   - 检查Python环境: python --version"
    exit 1
fi

# 启动前端服务
echo "🖥️  启动前端服务..."
cd ../frontend

# 检查Node.js版本
NODE_VERSION=$(node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js版本过低，需要Node.js 16+，当前版本: $(node --version 2>/dev/null || echo '未安装')"
    echo "💡 请手动激活Node.js 20 LTS环境:"
    echo "   nvm use 20"
    exit 1
fi

# 启动前端服务
npm start &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 3

# 保存进程ID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

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
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo "✅ 服务已停止"; exit 0' INT

wait 