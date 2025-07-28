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

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装，请先安装npm"
    exit 1
fi

# 检查前端依赖
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd "$PROJECT_ROOT/frontend"
    npm install
    cd "$PROJECT_ROOT"
fi

# 启动后端服务
echo "📡 启动后端服务..."
cd "$PROJECT_ROOT/backend"

# 激活虚拟环境
source venv/bin/activate

# 检查Python依赖
if ! python -c "import flask" &> /dev/null; then
    echo "📦 安装后端依赖..."
    pip install -r requirements.txt
fi

# 启动后端服务
nohup python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端服务是否正常
for i in {1..10}; do
    if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
        echo "✅ 后端服务运行正常"
        break
    else
        echo "⏳ 等待后端服务启动... (尝试 $i/10)"
        sleep 2
    fi
    
    if [ $i -eq 10 ]; then
        echo "❌ 后端服务启动失败，请检查 backend.log"
        echo "📋 后端日志内容:"
        tail -20 backend.log
        exit 1
    fi
done

# 启动前端服务
echo "🖥️  启动前端服务..."
cd "$PROJECT_ROOT/frontend"

# 启动Electron应用
npm start &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

# 保存进程ID
echo $BACKEND_PID > "$PROJECT_ROOT/.backend.pid"
echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend.pid"

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
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f "$PROJECT_ROOT/.backend.pid" "$PROJECT_ROOT/.frontend.pid"; echo "✅ 服务已停止"; exit 0' INT

wait 