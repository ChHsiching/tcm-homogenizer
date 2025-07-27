#!/bin/bash

# 中药多组分均化分析客户端 - 开发环境启动脚本

set -e

echo "🚀 启动中药多组分均化分析客户端开发环境..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 项目根目录: $PROJECT_ROOT"

# 函数：清理后台进程
cleanup() {
    echo "🧹 清理后台进程..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 启动后端服务
echo "🐍 启动后端服务..."
cd "$PROJECT_ROOT/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: Python虚拟环境不存在，请先运行 ./scripts/setup-dev.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 启动后端服务（后台运行）
echo "📡 启动Flask后端服务..."
python main.py &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端服务是否正常启动
if ! curl -s http://localhost:5000/api/health > /dev/null; then
    echo "❌ 后端服务启动失败"
    cleanup
    exit 1
fi

echo "✅ 后端服务运行正常"

# 启动前端服务
echo "⚡ 启动前端服务..."
cd "$PROJECT_ROOT/frontend"

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "❌ 错误: 前端依赖不存在，请先运行 ./scripts/setup-dev.sh"
    cleanup
    exit 1
fi

# 启动Electron应用（开发模式）
echo "🖥️ 启动Electron应用..."
NODE_ENV=development npm start &
FRONTEND_PID=$!
echo "✅ 前端应用已启动 (PID: $FRONTEND_PID)"

echo ""
echo "🎉 开发环境启动完成！"
echo ""
echo "📝 服务信息:"
echo "   - 后端API: http://localhost:5000"
echo "   - 健康检查: http://localhost:5000/api/health"
echo "   - 前端应用: Electron窗口"
echo ""
echo "🔧 开发提示:"
echo "   - 后端代码修改后需要重启后端服务"
echo "   - 前端代码修改后Electron会自动重载"
echo "   - 按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
echo "⏳ 等待用户中断..."
wait 