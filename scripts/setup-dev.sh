#!/usr/bin/env bash
# 本草智配客户端 - 开发环境设置脚本

set -e

echo "🚀 开始设置本草智配客户端开发环境..."

# 检查必要的工具
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 错误: $1 未安装，请先安装 $1"
        exit 1
    fi
}

echo "📋 检查必要工具..."
check_command "git"
check_command "node"
check_command "npm"
check_command "python3"

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 项目根目录: $PROJECT_ROOT"

# 设置前端环境
echo "🔧 设置前端环境..."
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
else
    echo "📦 前端依赖已存在，跳过安装"
fi

# 设置后端环境
echo "🐍 设置后端环境..."
cd "$PROJECT_ROOT/backend"

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p logs models monte_carlo_results uploads

# 设置权限
echo "🔐 设置文件权限..."
chmod +x "$PROJECT_ROOT/scripts/start-dev.sh"
chmod +x "$PROJECT_ROOT/scripts/build.sh"

echo "✅ 开发环境设置完成！"
echo ""
echo "📝 使用说明:"
echo "1. 启动开发环境: ./scripts/start-dev.sh"
echo "2. 构建应用: ./scripts/build.sh"
echo "3. 运行测试: ./scripts/test.sh"
echo ""
echo "🎉 开始开发吧！" 