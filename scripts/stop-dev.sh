#!/bin/bash

# 中药多组分均化分析客户端 - 停止开发环境脚本

echo "🛑 停止开发环境服务..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 停止后端服务
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "📡 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 1
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "⚠️  强制停止后端服务..."
            kill -9 $BACKEND_PID
        fi
        echo "✅ 后端服务已停止"
    else
        echo "ℹ️  后端服务未运行"
    fi
    rm -f .backend.pid
else
    echo "ℹ️  未找到后端服务PID文件"
fi

# 停止前端服务
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🖥️  停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 1
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "⚠️  强制停止前端服务..."
            kill -9 $FRONTEND_PID
        fi
        echo "✅ 前端服务已停止"
    else
        echo "ℹ️  前端服务未运行"
    fi
    rm -f .frontend.pid
else
    echo "ℹ️  未找到前端服务PID文件"
fi

# 清理可能的残留进程
echo "🧹 清理残留进程..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true

echo "✅ 开发环境已停止" 