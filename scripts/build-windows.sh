#!/bin/bash

# 中药多组分均化分析客户端 - Windows 打包脚本

set -e

echo "🪟 开始打包 Windows 版本..."

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

# 检查npm环境
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装或不在PATH中"
    exit 1
fi

echo "✅ 环境检查通过"

# 创建临时目录
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
TEMP_DIR="$BUILD_DIR/temp"

echo "📁 创建构建目录..."
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR" "$TEMP_DIR"

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

# 创建spec文件
echo "📝 创建PyInstaller配置..."
cat > main.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
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
pyinstaller --clean main.spec

# 复制打包结果
echo "📋 复制后端文件..."
cp -r dist/tcm-backend "$TEMP_DIR/"

cd ..

# 2. 准备前端文件
echo "⚡ 准备前端文件..."

cd frontend

# 安装依赖
echo "📦 安装前端依赖..."
npm install

# 复制前端文件到临时目录
echo "📋 复制前端文件..."
cp -r * "$TEMP_DIR/"

cd ..

# 3. 创建启动脚本
echo "🚀 创建启动脚本..."

cat > "$TEMP_DIR/start.bat" << 'EOF'
@echo off
chcp 65001 >nul
echo 启动中药多组分均化分析客户端...

REM 启动后端服务
start /B tcm-backend.exe

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端应用
electron.exe .

REM 清理进程
taskkill /f /im tcm-backend.exe >nul 2>&1
EOF

# 4. 创建安装程序配置
echo "📦 创建安装程序..."

cd frontend

# 更新package.json的build配置
cat > package.json << 'EOF'
{
  "name": "tcm-homogenizer-frontend",
  "version": "1.0.0",
  "description": "中药多组分均化分析客户端 - 前端应用",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dev": "NODE_ENV=development electron .",
    "build": "electron-builder",
    "build:win": "electron-builder --win",
    "build:linux": "electron-builder --linux",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": ["electron", "tcm", "中药", "配比", "分析"],
  "author": "TCM Homogenizer Team",
  "license": "MIT",
  "type": "commonjs",
  "build": {
    "appId": "com.tcm.homogenizer",
    "productName": "中药多组分均化分析客户端",
    "directories": {
      "output": "../../dist",
      "buildResources": "assets"
    },
    "files": [
      "main.js",
      "preload.js",
      "index.html",
      "styles/**/*",
      "scripts/**/*",
      "assets/**/*",
      "node_modules/**/*",
      "../build/temp/tcm-backend/**/*",
      "../build/temp/start.bat"
    ],
    "extraResources": [
      {
        "from": "../build/temp/tcm-backend",
        "to": "tcm-backend"
      }
    ],
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ],
      "icon": "assets/icon.ico",
      "requestedExecutionLevel": "asInvoker"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "中药多组分均化分析客户端"
    }
  },
  "devDependencies": {
    "electron": "^37.2.4",
    "electron-builder": "^26.0.12"
  }
}
EOF

# 5. 执行Electron Builder打包
echo "🔨 执行Electron Builder打包..."
npm run build:win

cd ..

# 6. 清理临时文件
echo "🧹 清理临时文件..."
rm -rf "$BUILD_DIR"

echo ""
echo "🎉 Windows 打包完成！"
echo "📦 安装程序位置: $DIST_DIR"
echo "📋 文件列表:"
ls -la "$DIST_DIR"

echo ""
echo "💡 安装说明:"
echo "   1. 运行 $DIST_DIR 中的安装程序"
echo "   2. 按照安装向导完成安装"
echo "   3. 从开始菜单或桌面快捷方式启动应用"
echo ""
echo "✅ 打包完成！" 