#!/bin/bash

# 中药多组分均化分析客户端 - Windows便携式打包脚本

set -e

echo "🪟 开始Windows便携式打包..."

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

# 1. 准备Python后端文件
echo "🐍 准备Python后端文件..."

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

# 创建后端目录
BACKEND_DIR="$DIST_DIR/backend"
mkdir -p "$BACKEND_DIR"

# 复制Python文件
echo "📋 复制Python文件..."
cp -r api "$BACKEND_DIR/"
cp -r algorithms "$BACKEND_DIR/"
cp -r utils "$BACKEND_DIR/"
cp main_packaged.py "$BACKEND_DIR/main.py"
cp requirements.txt "$BACKEND_DIR/"

# 创建Python启动脚本
echo "🚀 创建Python启动脚本..."

cat > "$BACKEND_DIR/start_backend.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 中药多组分均化分析后端服务

echo ========================================
echo    中药多组分均化分析后端服务
echo ========================================
echo.

echo 正在启动后端服务...
python main.py

echo 服务已停止
pause
EOF

cd ..

# 2. 准备前端文件
echo "⚡ 准备前端文件..."

cd frontend

# 安装依赖
echo "📦 安装前端依赖..."
npm install

# 创建前端目录
FRONTEND_DIR="$DIST_DIR/frontend"
mkdir -p "$FRONTEND_DIR"

# 复制前端文件
echo "📋 复制前端文件..."
cp -r * "$FRONTEND_DIR/"

cd ..

# 3. 创建主启动脚本
echo "🚀 创建主启动脚本..."

cat > "$DIST_DIR/启动程序.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 中药多组分均化分析客户端

echo ========================================
echo    中药多组分均化分析客户端
echo ========================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请确保已安装Python 3.10+并添加到PATH
    pause
    exit /b 1
)

echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Node.js环境
    echo 请确保已安装Node.js并添加到PATH
    pause
    exit /b 1
)

echo 安装后端依赖...
cd backend
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: 后端依赖安装失败，尝试继续运行...
)

echo 启动后端服务...
start /B python main.py

echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo 启动前端应用...
cd ..\frontend
electron.exe .

echo 正在关闭后端服务...
taskkill /f /im python.exe >nul 2>&1

echo 程序已退出
pause
EOF

# 4. 创建安装脚本
echo "📦 创建安装脚本..."

cat > "$DIST_DIR/安装依赖.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 安装依赖

echo ========================================
echo    安装中药多组分均化分析客户端依赖
echo ========================================
echo.

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请先安装Python 3.10+
    pause
    exit /b 1
)

echo 检查Node.js环境...
node --version
if errorlevel 1 (
    echo ❌ 错误: 未找到Node.js环境
    echo 请先安装Node.js
    pause
    exit /b 1
)

echo 安装后端依赖...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 后端依赖安装失败
    pause
    exit /b 1
)

echo 安装前端依赖...
cd ..\frontend
npm install
if errorlevel 1 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo ✅ 依赖安装完成！
echo 现在可以运行"启动程序.bat"启动应用
pause
EOF

# 5. 创建README文件
echo "📝 创建说明文件..."

cat > "$DIST_DIR/使用说明.txt" << 'EOF'
中药多组分均化分析客户端 - Windows便携版本

系统要求：
- Windows 10/11 (x64)
- Python 3.10+ (需要添加到PATH)
- Node.js (需要添加到PATH)
- 至少2GB内存
- 至少1GB磁盘空间

安装步骤：
1. 确保已安装Python 3.10+和Node.js
2. 双击"安装依赖.bat"安装所需依赖
3. 等待安装完成

使用方法：
1. 双击"启动程序.bat"启动应用
2. 程序会自动启动后端服务和前端界面
3. 关闭应用窗口后，后端服务会自动停止

目录结构：
├── backend/          # Python后端文件
├── frontend/         # Electron前端文件
├── 启动程序.bat      # 主启动脚本
├── 安装依赖.bat      # 依赖安装脚本
└── 使用说明.txt      # 本文件

故障排除：
1. 如果提示找不到Python或Node.js，请确保已正确安装并添加到PATH
2. 如果依赖安装失败，请检查网络连接或使用国内镜像源
3. 如果启动失败，请查看控制台错误信息

技术支持：
如有问题，请联系开发团队。
EOF

# 6. 创建测试脚本
echo "🧪 创建测试脚本..."

cat > "$DIST_DIR/测试后端.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 测试后端服务

echo ========================================
echo    测试后端服务
echo ========================================
echo.

echo 启动后端服务...
cd backend
start /B python main.py

echo 等待服务启动...
timeout /t 3 /nobreak >nul

echo 测试API连接...
curl -s http://127.0.0.1:5000/api/health

echo.
echo 按任意键关闭服务...
pause >nul

echo 正在关闭服务...
taskkill /f /im python.exe >nul 2>&1

echo 测试完成
pause
EOF

echo ""
echo "🎉 Windows 便携式打包完成！"
echo "📦 输出目录: $DIST_DIR"
echo "📋 文件列表:"
ls -la "$DIST_DIR"

echo ""
echo "💡 使用说明:"
echo "   1. 将整个 dist 目录复制到Windows机器"
echo "   2. 确保Windows机器已安装Python 3.10+和Node.js"
echo "   3. 双击 '安装依赖.bat' 安装依赖"
echo "   4. 双击 '启动程序.bat' 启动应用"
echo "   5. 双击 '测试后端.bat' 测试后端服务"
echo "   6. 阅读 '使用说明.txt' 了解详细信息"
echo ""
echo "✅ 打包完成！" 