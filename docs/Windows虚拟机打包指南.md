# Windows虚拟机打包指南

## 概述

本指南详细说明如何在Windows虚拟机中将中药多组分均化分析客户端打包成独立的exe安装程序。

## 准备工作

### 1. Windows虚拟机环境要求

- **操作系统**：Windows 10/11 (x64)
- **内存**：至少4GB
- **磁盘空间**：至少10GB可用空间
- **网络**：需要稳定的网络连接下载依赖

### 2. 必需软件安装

#### Python环境
1. 下载Python 3.10+：https://www.python.org/downloads/
2. 安装时勾选：
   - ✅ Add Python to PATH
   - ✅ Install pip
   - ✅ Install for all users

#### Node.js环境
1. 下载Node.js LTS：https://nodejs.org/
2. 安装时选择：
   - ✅ Add to PATH
   - ✅ Install additional tools

#### Git
1. 下载Git：https://git-scm.com/download/win
2. 安装时选择默认选项即可

#### 开发工具（可选）
- Visual Studio Code：https://code.visualstudio.com/
- 或使用系统自带的记事本

## 项目部署

### 1. 获取项目代码

```cmd
# 方法一：从Git仓库克隆
git clone <repository-url>
cd tcm-homogenizer

# 方法二：直接复制项目文件夹
# 将整个项目文件夹复制到虚拟机中
```

### 2. 验证环境

```cmd
# 检查Python版本
python --version

# 检查Node.js版本
node --version

# 检查npm版本
npm --version

# 检查Git版本
git --version
```

## 后端打包

### 1. 准备Python环境

```cmd
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 安装PyInstaller
pip install pyinstaller
```

### 2. 创建打包配置

创建文件 `backend/tcm-backend.spec`：

```python
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
```

### 3. 执行后端打包

```cmd
# 确保在虚拟环境中
venv\Scripts\activate

# 执行打包
pyinstaller --clean tcm-backend.spec

# 检查生成的文件
dir dist\
```

## 前端打包

### 1. 准备前端环境

```cmd
cd frontend

# 安装依赖
npm install

# 安装electron-builder
npm install --save-dev electron-builder
```

### 2. 创建Electron应用

创建临时工作目录：

```cmd
cd ..
mkdir build-temp
cd build-temp
```

创建 `package.json`：

```json
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
      "output": "../dist"
    },
    "files": [
      "main.js",
      "preload.js",
      "index.html",
      "styles/**/*",
      "scripts/**/*",
      "assets/**/*",
      "node_modules/**/*",
      "tcm-backend.exe"
    ],
    "extraResources": [
      {
        "from": "../backend/dist/tcm-backend.exe",
        "to": "tcm-backend.exe"
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
```

### 3. 创建主进程文件

创建 `main.js`：

```javascript
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
  const backendPath = path.join(process.resourcesPath, 'tcm-backend.exe');
  
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
```

### 4. 创建预加载脚本

创建 `preload.js`：

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onMenuImportData: (callback) => ipcRenderer.on('menu-import-data', callback),
  onMenuExportResults: (callback) => ipcRenderer.on('menu-export-results', callback),
  onMenuSymbolicRegression: (callback) => ipcRenderer.on('menu-symbolic-regression', callback),
  onMenuMonteCarlo: (callback) => ipcRenderer.on('menu-monte-carlo', callback),
  onMenuAbout: (callback) => ipcRenderer.on('menu-about', callback),
});
```

### 5. 复制前端文件

```cmd
# 复制前端文件到构建目录
xcopy /E /I /Y ..\frontend\* .

# 复制后端exe
copy ..\backend\dist\tcm-backend.exe .
```

### 6. 创建图标文件

在 `assets/` 目录下放置 `icon.ico` 文件（可选）。

### 7. 执行前端打包

```cmd
# 安装依赖
npm install

# 执行打包
npm run build:win
```

## 打包结果

### 生成的文件

打包完成后，在 `dist/` 目录下会生成：

- `中药多组分均化分析客户端 Setup.exe` - Windows安装程序
- `win-unpacked/` - 解压版本（用于测试）

### 测试安装程序

1. 双击安装程序进行安装
2. 从开始菜单或桌面快捷方式启动应用
3. 验证功能是否正常

## 故障排除

### 常见问题

#### 1. PyInstaller打包失败
- 检查Python虚拟环境是否正确激活
- 确保所有依赖已安装
- 检查spec文件配置是否正确

#### 2. Electron Builder打包失败
- 检查Node.js版本是否兼容
- 确保所有依赖已安装
- 检查package.json配置是否正确

#### 3. 后端exe无法启动
- 检查是否包含所有必要的文件
- 验证依赖是否正确打包
- 查看控制台错误信息

#### 4. 安装程序创建失败
- 检查图标文件是否存在
- 验证文件路径是否正确
- 确保有足够的磁盘空间

### 调试技巧

- 使用 `--debug` 参数获取详细日志
- 在开发模式下测试应用
- 检查临时文件和日志

## 优化建议

### 性能优化
- 使用UPX压缩exe文件
- 排除不必要的依赖
- 优化资源文件大小

### 用户体验
- 添加启动画面
- 优化安装界面
- 提供卸载功能

---

**注意**：本指南适用于Windows 10/11环境。在其他Windows版本上可能需要调整配置。 