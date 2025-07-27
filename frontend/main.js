const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// 禁用SSL证书验证（仅用于开发环境）
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

// 全局变量
let mainWindow;
let backendProcess = null;
const backendPort = 5000;

function createWindow() {
    // 创建浏览器窗口
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: false, // 允许跨域请求
            allowRunningInsecureContent: true // 允许不安全内容
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        show: false,
        titleBarStyle: 'default'
    });

    // 加载应用
    mainWindow.loadFile('index.html');

    // 当窗口准备好时显示
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // 启动后端服务
        startBackendService();
    });

    // 当窗口关闭时
    mainWindow.on('closed', () => {
        mainWindow = null;
        stopBackendService();
    });

    // 开发环境打开开发者工具
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
}

// 当 Electron 完成初始化并准备创建浏览器窗口时调用此方法
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    // 在 macOS 上，当点击 dock 图标并且没有其他窗口打开时，
    // 通常在应用程序中重新创建一个窗口。
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// 当所有窗口都被关闭时退出
app.on('window-all-closed', () => {
  // 在 macOS 上，除非用户用 Cmd + Q 确定地退出，
  // 否则绝大部分应用及其菜单栏会保持激活。
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 在这个文件中，你可以续写应用剩下主进程代码。
// 也可以拆分成几个文件，然后用 require 导入。

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

// 创建菜单
createMenu();

// IPC 通信处理
ipcMain.handle('start-backend', async () => {
  try {
    // 启动Python后端服务
    const pythonProcess = spawn('python', ['../backend/main.py'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    return { success: true, pid: pythonProcess.pid };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stop-backend', async () => {
  // 停止后端服务的逻辑
  return { success: true };
}); 

// 启动后端服务
function startBackendService() {
    if (backendProcess) {
        console.log('Backend service already running');
        return;
    }

    console.log('Starting backend service...');
    
    // 启动Python后端服务
    backendProcess = spawn('python', ['../backend/main.py'], {
        cwd: path.join(__dirname, '..', 'backend'),
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
        backendProcess = null;
    });

    backendProcess.on('error', (error) => {
        console.error('Backend process error:', error);
        dialog.showErrorBox('后端服务错误', `启动后端服务失败: ${error.message}`);
    });

    // 等待后端服务启动
    setTimeout(() => {
        checkBackendHealth();
    }, 2000);
}

// 停止后端服务
function stopBackendService() {
    if (backendProcess) {
        console.log('Stopping backend service...');
        backendProcess.kill();
        backendProcess = null;
    }
}

// 检查后端服务健康状态
async function checkBackendHealth() {
    try {
        const response = await fetch(`http://localhost:${backendPort}/api/health`);
        if (response.ok) {
            console.log('Backend service is healthy');
            if (mainWindow) {
                mainWindow.webContents.send('backend-status', { connected: true });
            }
        } else {
            console.log('Backend service health check failed');
            if (mainWindow) {
                mainWindow.webContents.send('backend-status', { connected: false });
            }
        }
    } catch (error) {
        console.log('Backend service not available:', error.message);
        if (mainWindow) {
            mainWindow.webContents.send('backend-status', { connected: false });
        }
    }
}

// 等待后端服务启动
async function waitForBackend() {
    const maxAttempts = 10;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
        try {
            const response = await fetch(`http://localhost:${backendPort}/api/health`);
            if (response.ok) {
                console.log('Backend service is ready');
                return true;
            }
        } catch (error) {
            console.log(`Backend not ready, attempt ${attempts + 1}/${maxAttempts}`);
        }
        
        attempts++;
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log('Backend service failed to start');
    return false;
} 