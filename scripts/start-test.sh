#!/bin/bash

# 中药多组分均化分析客户端 - 测试环境启动脚本

set -e

echo "🚀 启动中药多组分均化分析客户端测试环境..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 停止可能存在的进程
echo "🛑 停止可能存在的进程..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "electron.*frontend" 2>/dev/null || true
sleep 2

# 检查后端虚拟环境
BACKEND_VENV="$PROJECT_ROOT/backend/venv"
if [ ! -d "$BACKEND_VENV" ]; then
    echo "❌ 后端虚拟环境不存在，请先运行 setup-dev.sh"
    exit 1
fi

# 启动后端服务
echo "📡 启动后端服务..."
cd backend

# 检查Python依赖
echo "🔍 检查Python依赖..."
source venv/bin/activate
python -c "import flask, pandas, numpy, requests, loguru" 2>/dev/null || {
    echo "❌ Python依赖不完整，请运行: pip install -r requirements.txt"
    exit 1
}

# 启动Flask后端服务（实时输出日志到控制台）
echo "🚀 启动Flask后端服务..."
python main.py 2>&1 | tee ../backend.log &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端服务是否正常
echo "🔍 检查后端服务状态..."
for i in {1..20}; do
    if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
        echo "✅ 后端服务运行正常"
        break
    else
        echo "⏳ 等待后端服务启动... (尝试 $i/20)"
        sleep 2
    fi
    
    if [ $i -eq 20 ]; then
        echo "❌ 后端服务启动失败，请检查 backend.log"
        echo "📋 后端日志内容:"
        tail -20 ../backend.log
        exit 1
    fi
done

# 保存进程ID
echo $BACKEND_PID > ../.backend.pid

echo ""
echo "🎉 测试环境启动完成！"
echo "📡 后端服务: http://127.0.0.1:5000"
echo ""
echo "💡 提示:"
echo "   - 运行测试: python test_frontend_mock.py"
echo "   - 使用 Ctrl+C 停止服务"
echo "   - 查看后端日志: tail -f backend.log"
echo "   - 停止服务: ./scripts/stop-dev.sh"
echo ""

# 询问是否运行测试
echo "🤔 是否现在运行前端模拟测试？ (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🧪 运行前端模拟测试..."
    cd ..
    python test_frontend_mock.py
fi

# 定义清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    
    # 停止后端服务
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
    fi
    
    # 停止所有相关进程
    echo "🛑 清理相关进程..."
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "tail -f" 2>/dev/null || true
    
    # 删除PID文件
    rm -f ../.backend.pid 2>/dev/null || true
    
    echo "✅ 服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup INT TERM EXIT

# 实时显示日志
echo "📋 实时日志输出 (Ctrl+C 停止):"
echo "=================================="

# 显示后端日志
tail -f ../backend.log &
TAIL_PID=$!

# 等待任意子进程结束
wait 