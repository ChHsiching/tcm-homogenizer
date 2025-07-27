#!/bin/bash

# 中药多组分均化分析客户端 - 独立Windows exe打包脚本

set -e

echo "🪟 开始独立Windows exe打包..."

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

# 1. 打包Python后端为独立exe
echo "🐍 打包Python后端为独立exe..."

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

# 创建spec文件用于Windows交叉编译
echo "📝 创建PyInstaller配置..."
cat > tcm-backend.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_packaged.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('api', 'api'),
        ('algorithms', 'algorithms'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'loguru',
        'numpy',
        'scipy',
        'pandas',
        'sklearn',
        'sympy',
        'gplearn',
        'pysr',
        'matplotlib',
        'seaborn',
        'plotly',
        'openpyxl',
        'xlrd',
        'python-dotenv',
        'pydantic',
        'werkzeug',
        'jinja2',
        'markupsafe',
        'itsdangerous',
        'click',
        'blinker',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tcm-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
EOF

# 执行PyInstaller打包
echo "🔨 执行PyInstaller打包..."
pyinstaller --clean tcm-backend.spec

cd ..

# 2. 准备前端文件
echo "⚡ 准备前端文件..."

cd frontend

# 安装依赖
echo "📦 安装前端依赖..."
npm install

cd ..

# 3. 创建Windows批处理文件来模拟exe行为
echo "🚀 创建Windows启动文件..."

# 创建主启动脚本
cat > "$DIST_DIR/中药多组分均化分析客户端.bat" << 'EOF'
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
EOF

# 创建隐藏的启动脚本（模拟exe）
cat > "$DIST_DIR/启动程序.vbs" << 'EOF'
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "中药多组分均化分析客户端.bat", 0, False
EOF

# 4. 复制所有必要文件
echo "📋 复制文件..."

# 复制后端exe
cp backend/dist/tcm-backend "$DIST_DIR/tcm-backend.exe"

# 复制前端文件
cp -r frontend/* "$DIST_DIR/"

# 5. 创建Windows安装包脚本
echo "📦 创建安装包..."

cat > "$DIST_DIR/安装程序.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 中药多组分均化分析客户端 - 安装程序

echo ========================================
echo    中药多组分均化分析客户端安装程序
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

# 6. 创建卸载程序
cat > "$DIST_DIR/卸载程序.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 中药多组分均化分析客户端 - 卸载程序

echo ========================================
echo    中药多组分均化分析客户端卸载程序
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

# 7. 创建README文件
echo "📝 创建说明文件..."

cat > "$DIST_DIR/使用说明.txt" << 'EOF'
中药多组分均化分析客户端 - 独立运行版本

这是一个完全独立的Windows应用程序，无需安装Python或Node.js。

使用方法：
1. 双击"启动程序.vbs"启动应用（推荐）
2. 或双击"中药多组分均化分析客户端.bat"启动应用

安装到系统（可选）：
1. 双击"安装程序.bat"进行系统安装
2. 安装后可从桌面或开始菜单启动
3. 使用"卸载程序.bat"可完全卸载

系统要求：
- Windows 10/11 (x64)
- 至少2GB内存
- 至少500MB磁盘空间

注意事项：
- 首次启动可能需要较长时间
- 如果杀毒软件报警，请添加信任
- 程序会在临时目录创建日志文件

技术支持：
如有问题，请联系开发团队。
EOF

# 8. 创建压缩包
echo "📦 创建压缩包..."

cd "$DIST_DIR"
tar -czf "../tcm-homogenizer-standalone-windows.tar.gz" *
cd ..

echo ""
echo "🎉 独立Windows exe打包完成！"
echo "📦 输出目录: $DIST_DIR"
echo "📦 压缩包: tcm-homogenizer-standalone-windows.tar.gz"
echo "📋 文件列表:"
ls -la "$DIST_DIR"

echo ""
echo "💡 使用说明:"
echo "   1. 将 tcm-homogenizer-standalone-windows.tar.gz 传输到Windows机器"
echo "   2. 解压到任意目录"
echo "   3. 双击 '启动程序.vbs' 启动应用"
echo "   4. 或双击 '安装程序.bat' 安装到系统"
echo ""
echo "✅ 打包完成！" 