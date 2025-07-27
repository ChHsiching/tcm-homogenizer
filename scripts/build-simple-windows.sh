#!/bin/bash

# 中药多组分均化分析客户端 - 简化Windows打包脚本

set -e

echo "🪟 开始简化Windows打包..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查环境
echo "🔍 检查打包环境..."

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装或不在PATH中"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装或不在PATH中"
    exit 1
fi

echo "✅ 环境检查通过"

# 创建输出目录
DIST_DIR="$PROJECT_ROOT/dist"
echo "📁 创建输出目录..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# 1. 打包Python后端
echo "🐍 打包Python后端..."

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ Python虚拟环境不存在，正在创建..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 安装PyInstaller
echo "📦 安装PyInstaller..."
pip install pyinstaller

# 执行PyInstaller打包
echo "🔨 执行PyInstaller打包..."
pyinstaller --onefile \
    --name tcm-backend \
    --add-data "api:api" \
    --add-data "algorithms:algorithms" \
    --add-data "utils:utils" \
    --hidden-import flask \
    --hidden-import flask_cors \
    --hidden-import loguru \
    --hidden-import numpy \
    --hidden-import scipy \
    --hidden-import pandas \
    --hidden-import sklearn \
    --hidden-import sympy \
    --hidden-import gplearn \
    --hidden-import pysr \
    --hidden-import matplotlib \
    --hidden-import seaborn \
    --hidden-import plotly \
    --hidden-import openpyxl \
    --hidden-import xlrd \
    --hidden-import python-dotenv \
    --hidden-import pydantic \
    main_packaged.py

# 复制后端exe到输出目录
echo "📋 复制后端文件..."
cp dist/tcm-backend.exe "$DIST_DIR/"

cd ..

# 2. 准备前端文件
echo "⚡ 准备前端文件..."

cd frontend

# 安装依赖
echo "📦 安装前端依赖..."
npm install

# 复制前端文件到输出目录
echo "📋 复制前端文件..."
cp -r * "$DIST_DIR/"

cd ..

# 3. 创建启动脚本
echo "🚀 创建启动脚本..."

cat > "$DIST_DIR/启动程序.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 中药多组分均化分析客户端

echo ========================================
echo    中药多组分均化分析客户端
echo ========================================
echo.

echo 正在启动后端服务...
start /B tcm-backend.exe

echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo 正在启动前端应用...
electron.exe .

echo 正在关闭后端服务...
taskkill /f /im tcm-backend.exe >nul 2>&1

echo 程序已退出
pause
EOF

# 4. 创建README文件
echo "📝 创建说明文件..."

cat > "$DIST_DIR/使用说明.txt" << 'EOF'
中药多组分均化分析客户端 - Windows版本

使用说明：
1. 双击"启动程序.bat"文件启动应用
2. 程序会自动启动后端服务和前端界面
3. 关闭应用窗口后，后端服务会自动停止

系统要求：
- Windows 10/11 (x64)
- 至少2GB内存
- 至少500MB磁盘空间

注意事项：
- 首次启动可能需要较长时间
- 如果杀毒软件报警，请添加信任
- 确保防火墙允许程序访问网络
- 程序会在临时目录创建日志文件

技术支持：
如有问题，请联系开发团队。
EOF

# 5. 创建测试脚本
echo "🧪 创建测试脚本..."

cat > "$DIST_DIR/测试后端.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 测试后端服务

echo 正在启动后端服务...
start /B tcm-backend.exe

echo 等待服务启动...
timeout /t 3 /nobreak >nul

echo 测试API连接...
curl -s http://127.0.0.1:5000/api/health

echo.
echo 按任意键关闭服务...
pause >nul

echo 正在关闭服务...
taskkill /f /im tcm-backend.exe >nul 2>&1

echo 测试完成
pause
EOF

# 6. 创建图标文件（如果不存在）
if [ ! -f "frontend/assets/icon.ico" ]; then
    echo "🎨 创建默认图标..."
    # 这里可以添加创建默认图标的代码
    echo "注意：请手动添加图标文件到 frontend/assets/icon.ico"
fi

echo ""
echo "🎉 Windows 简化打包完成！"
echo "📦 输出目录: $DIST_DIR"
echo "📋 文件列表:"
ls -la "$DIST_DIR"

echo ""
echo "💡 使用说明:"
echo "   1. 将整个 dist 目录复制到Windows机器"
echo "   2. 双击 '启动程序.bat' 启动应用"
echo "   3. 双击 '测试后端.bat' 测试后端服务"
echo "   4. 阅读 '使用说明.txt' 了解详细信息"
echo ""
echo "✅ 打包完成！" 