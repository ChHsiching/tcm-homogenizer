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

# 启动后端服务
echo "📡 启动后端服务..."
cd backend
source venv/bin/activate

# 检查后端依赖
echo "🔍 检查后端依赖..."
python -c "import flask, pandas, numpy, sklearn, loguru" 2>/dev/null || {
    echo "❌ 后端依赖不完整，请运行: cd backend && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
}

# 确保端口5000没有被占用
echo "🔍 检查端口5000..."
if lsof -ti:5000 > /dev/null 2>&1; then
    echo "⚠️  端口5000被占用，正在停止占用进程..."
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# 启动后端服务（使用nohup后台运行）
echo "🚀 启动后端服务..."
nohup python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端服务是否正常
echo "🔍 检查后端服务状态..."
for i in {1..15}; do
    if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
        echo "✅ 后端服务运行正常"
        break
    else
        echo "⏳ 等待后端服务启动... (尝试 $i/15)"
        sleep 2
    fi
    
    if [ $i -eq 15 ]; then
        echo "❌ 后端服务启动失败，请检查 backend.log"
        echo "📋 后端日志:"
        tail -20 backend.log
        echo ""
        echo "🔧 尝试手动启动后端服务:"
        echo "cd backend && source venv/bin/activate && python main.py"
        exit 1
    fi
done

# 启动前端服务
echo "🖥️  启动前端服务..."
cd ../frontend

# 检查前端依赖
echo "🔍 检查前端依赖..."
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端服务
echo "🚀 启动前端服务..."
npm start &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

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