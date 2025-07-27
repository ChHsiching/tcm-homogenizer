#!/bin/bash

# 中药多组分均化分析客户端 - Electron Windows安装程序打包脚本

set -e

echo "🪟 开始Electron Windows安装程序打包..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 检查环境
echo "🔍 检查打包环境..."

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

# 创建临时工作目录
WORK_DIR="$PROJECT_ROOT/build-temp"
DIST_DIR="$PROJECT_ROOT/dist"
echo "📁 创建临时工作目录..."
rm -rf "$WORK_DIR" "$DIST_DIR"
mkdir -p "$WORK_DIR" "$DIST_DIR"

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

cd ..

# 2. 创建Electron应用
echo "⚡ 创建Electron应用..."

cd "$WORK_DIR"

# 初始化package.json
cat > package.json << 'EOF'
{
  "name": "tcm-homogenizer",
  "version": "1.0.0",
  "description": "中药多组分均化分析客户端",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "build:win": "electron-builder --win",
    "pack": "electron-builder --dir"
  },
  "keywords": ["electron", "tcm", "中药", "配比", "分析"],
  "author": "TCM Homogenizer Team",
  "license": "MIT",
  "devDependencies": {
    "electron": "^37.2.4",
    "electron-builder": "^26.0.12"
  },
  "build": {
    "appId": "com.tcm.homogenizer",
    "productName": "中药多组分均化分析客户端",
    "directories": {
      "output": "../../dist"
    },
    "files": [
      "main.js",
      "preload.js",
      "index.html",
      "styles/**/*",
      "scripts/**/*",
      "assets/**/*",
      "node_modules/**/*",
      "tcm-backend"
    ],
    "extraResources": [
      {
        "from": "../backend/dist/tcm-backend",
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
      "shortcutName": "中药多组分均化分析客户端",
      "installerIcon": "assets/icon.ico",
      "uninstallerIcon": "assets/icon.ico",
      "installerHeaderIcon": "assets/icon.ico"
    }
  }
}
EOF

# 复制后端exe
cp ../backend/dist/tcm-backend ./tcm-backend

# 3. 创建主进程文件
echo "📝 创建主进程文件..."

cat > main.js << 'EOF'
const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets/icon.png'),
    title: '中药多组分均化分析客户端',
    show: false
  });

  mainWindow.loadFile('index.html');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startBackend() {
  const backendPath = path.join(process.resourcesPath, 'tcm-backend');
  
  if (!fs.existsSync(backendPath)) {
    console.error('Backend executable not found:', backendPath);
    return false;
  }

  backendProcess = spawn(backendPath, [], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  backendProcess.stdout.on('data', (data) => {
    console.log('Backend stdout:', data.toString());
  });

  backendProcess.stderr.on('data', (data) => {
    console.log('Backend stderr:', data.toString());
  });

  backendProcess.on('close', (code) => {
    console.log('Backend process exited with code:', code);
  });

  return true;
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

app.whenReady().then(() => {
  // 启动后端服务
  if (startBackend()) {
    console.log('Backend service started');
  } else {
    console.error('Failed to start backend service');
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

// 设置应用菜单
function createMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '导入数据',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow.webContents.send('menu-import-data');
          }
        },
        {
          label: '导出结果',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('menu-export-results');
          }
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: '分析',
      submenu: [
        {
          label: '符号回归',
          click: () => {
            mainWindow.webContents.send('menu-symbolic-regression');
          }
        },
        {
          label: '蒙特卡罗分析',
          click: () => {
            mainWindow.webContents.send('menu-monte-carlo');
          }
        }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于',
          click: () => {
            mainWindow.webContents.send('menu-about');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

createMenu();
EOF

# 4. 创建预加载脚本
cat > preload.js << 'EOF'
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onMenuImportData: (callback) => ipcRenderer.on('menu-import-data', callback),
  onMenuExportResults: (callback) => ipcRenderer.on('menu-export-results', callback),
  onMenuSymbolicRegression: (callback) => ipcRenderer.on('menu-symbolic-regression', callback),
  onMenuMonteCarlo: (callback) => ipcRenderer.on('menu-monte-carlo', callback),
  onMenuAbout: (callback) => ipcRenderer.on('menu-about', callback),
});
EOF

# 5. 复制前端文件
echo "📋 复制前端文件..."
cp -r ../frontend/* .

# 6. 创建默认图标（如果不存在）
if [ ! -f "assets/icon.ico" ]; then
    echo "🎨 创建默认图标..."
    mkdir -p assets
    # 这里可以添加创建默认图标的代码
    echo "注意：请手动添加图标文件到 assets/icon.ico"
fi

# 7. 安装依赖并打包
echo "📦 安装依赖..."
npm install

echo "🔨 开始打包..."
npm run build:win

cd ..

# 8. 清理临时文件
echo "🧹 清理临时文件..."
rm -rf "$WORK_DIR"

echo ""
echo "🎉 Electron Windows安装程序打包完成！"
echo "📦 输出目录: $DIST_DIR"
echo "📋 文件列表:"
ls -la "$DIST_DIR"

echo ""
echo "💡 使用说明:"
echo "   1. 将 dist 目录中的安装程序传输到Windows机器"
echo "   2. 双击安装程序进行安装"
echo "   3. 从桌面或开始菜单启动应用"
echo ""
echo "✅ 打包完成！" 