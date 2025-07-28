#!/bin/bash

# 测试后端启动脚本

set -e

echo "🧪 测试后端启动..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查后端虚拟环境
BACKEND_VENV="$PROJECT_ROOT/backend/venv"
if [ ! -d "$BACKEND_VENV" ]; then
    echo "❌ 后端虚拟环境不存在，请先运行 setup-dev.sh"
    exit 1
fi

# 激活虚拟环境
cd backend
source venv/bin/activate

# 检查Python依赖
echo "📋 检查Python依赖..."
python -c "import flask, pandas, numpy, sklearn, sympy" 2>/dev/null || {
    echo "❌ Python依赖不完整，请运行: pip install -r requirements.txt"
    exit 1
}

echo "✅ Python依赖检查通过"

# 测试后端启动
echo "🚀 测试后端启动..."
timeout 30s python main.py &
BACKEND_PID=$!

# 等待启动
sleep 5

# 检查服务是否正常
if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功"
    kill $BACKEND_PID 2>/dev/null || true
    exit 0
else
    echo "❌ 后端服务启动失败"
    echo "📋 后端日志:"
    tail -n 20 backend.log 2>/dev/null || echo "无日志文件"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi 