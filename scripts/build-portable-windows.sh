#!/bin/bash

# 中药多组分均化分析客户端 - 便携式Windows打包脚本

set -e

echo "🪟 开始便携式Windows打包..."

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

# 1. 准备Python后端
echo "🐍 准备Python后端..."

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

# 3. 创建便携式启动器
echo "🚀 创建便携式启动器..."

# 创建主启动脚本
cat > "$DIST_DIR/启动程序.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 中药多组分均化分析客户端

echo ========================================
echo    中药多组分均化分析客户端
echo ========================================
echo.

REM 检查Python环境
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 正在尝试使用内置Python...
    if exist "python\python.exe" (
        set "PYTHON_CMD=python\python.exe"
        echo ✅ 找到内置Python
    ) else (
        echo ❌ 未找到内置Python，请安装Python 3.10+
        pause
        exit /b 1
    )
) else (
    set "PYTHON_CMD=python"
    echo ✅ 找到系统Python
)

REM 检查Node.js环境
echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Node.js环境
    echo 正在尝试使用内置Node.js...
    if exist "nodejs\node.exe" (
        set "NODE_CMD=nodejs\node.exe"
        echo ✅ 找到内置Node.js
    ) else (
        echo ❌ 未找到内置Node.js，请安装Node.js
        pause
        exit /b 1
    )
) else (
    set "NODE_CMD=node"
    echo ✅ 找到系统Node.js
)

REM 安装后端依赖
echo 安装后端依赖...
cd backend
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ⚠️  警告: 后端依赖安装失败，尝试继续运行...
)

REM 启动后端服务
echo 启动后端服务...
start /B %PYTHON_CMD% main.py

REM 等待后端服务启动
echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 启动前端应用
echo 启动前端应用...
cd ..\frontend
%NODE_CMD% node_modules\electron\dist\electron.exe .

REM 清理进程
echo 正在关闭后端服务...
taskkill /f /im python.exe >nul 2>&1

echo 程序已退出
pause
EOF

# 创建VBS启动脚本（隐藏控制台）
cat > "$DIST_DIR/启动程序.vbs" << 'EOF'
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "启动程序.bat", 0, False
EOF

# 4. 创建安装脚本
echo "📦 创建安装脚本..."

cat > "$DIST_DIR/安装到系统.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 安装到系统

echo ========================================
echo    安装中药多组分均化分析客户端
echo ========================================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\中药多组分均化分析客户端"

echo 正在安装到: %INSTALL_DIR%

REM 创建安装目录
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM 复制文件
xcopy /E /I /Y . "%INSTALL_DIR%"

REM 创建桌面快捷方式
echo 创建桌面快捷方式...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\中药多组分均化分析客户端.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\启动程序.vbs'; $Shortcut.Save()"

REM 创建开始菜单快捷方式
echo 创建开始菜单快捷方式...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\中药多组分均化分析客户端" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\中药多组分均化分析客户端"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\中药多组分均化分析客户端\中药多组分均化分析客户端.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\启动程序.vbs'; $Shortcut.Save()"

echo.
echo ✅ 安装完成！
echo 您可以从桌面或开始菜单启动程序
pause
EOF

# 5. 创建卸载脚本
cat > "$DIST_DIR/卸载程序.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 卸载程序

echo ========================================
echo    卸载中药多组分均化分析客户端
echo ========================================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\中药多组分均化分析客户端"

echo 正在卸载...

REM 删除桌面快捷方式
if exist "%USERPROFILE%\Desktop\中药多组分均化分析客户端.lnk" del "%USERPROFILE%\Desktop\中药多组分均化分析客户端.lnk"

REM 删除开始菜单快捷方式
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\中药多组分均化分析客户端" rmdir /S /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\中药多组分均化分析客户端"

REM 删除安装目录
if exist "%INSTALL_DIR%" rmdir /S /Q "%INSTALL_DIR%"

echo ✅ 卸载完成！
pause
EOF

# 6. 创建README文件
echo "📝 创建说明文件..."

cat > "$DIST_DIR/使用说明.txt" << 'EOF'
中药多组分均化分析客户端 - 便携版本

这是一个便携式Windows应用程序，支持以下两种运行方式：

方式一：便携运行（推荐）
1. 双击"启动程序.vbs"启动应用（无控制台窗口）
2. 或双击"启动程序.bat"启动应用（显示控制台）

方式二：安装到系统
1. 双击"安装到系统.bat"进行安装
2. 安装后可从桌面或开始菜单启动
3. 使用"卸载程序.bat"可完全卸载

系统要求：
- Windows 10/11 (x64)
- Python 3.10+ (如果未安装，程序会提示)
- Node.js (如果未安装，程序会提示)
- 至少2GB内存
- 至少1GB磁盘空间

注意事项：
- 首次启动会自动安装依赖
- 如果杀毒软件报警，请添加信任
- 程序会在临时目录创建日志文件

目录结构：
├── backend/              # Python后端文件
├── frontend/             # Electron前端文件
├── 启动程序.bat          # 主启动脚本
├── 启动程序.vbs          # 隐藏启动脚本
├── 安装到系统.bat        # 安装脚本
├── 卸载程序.bat          # 卸载脚本
└── 使用说明.txt          # 本文件

技术支持：
如有问题，请联系开发团队。
EOF

# 7. 创建测试脚本
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
python main.py

echo 测试完成
pause
EOF

# 8. 创建压缩包
echo "📦 创建压缩包..."

cd "$DIST_DIR"
tar -czf "../tcm-homogenizer-portable-windows.tar.gz" *
cd ..

echo ""
echo "🎉 便携式Windows打包完成！"
echo "📦 输出目录: $DIST_DIR"
echo "📦 压缩包: tcm-homogenizer-portable-windows.tar.gz"
echo "📋 文件列表:"
ls -la "$DIST_DIR"

echo ""
echo "💡 使用说明:"
echo "   1. 将 tcm-homogenizer-portable-windows.tar.gz 传输到Windows机器"
echo "   2. 解压到任意目录"
echo "   3. 双击 '启动程序.vbs' 启动应用（推荐）"
echo "   4. 或双击 '安装到系统.bat' 安装到系统"
echo ""
echo "✅ 打包完成！" 