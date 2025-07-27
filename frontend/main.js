const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// 保持对窗口对象的全局引用，如果不这么做的话，当JavaScript对象被
// 垃圾回收的时候，窗口会被自动地关闭
let mainWindow;

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets/icon.png'), // 可选：应用图标
    title: '中药多组分均化分析客户端',
    show: false // 先不显示，等准备好再显示
  });

  // 加载应用的 index.html
  mainWindow.loadFile('index.html');

  // 当窗口准备好显示时显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 当窗口被关闭时发出
  mainWindow.on('closed', () => {
    // 取消引用 window 对象，如果你的应用支持多窗口的话，
    // 通常会把多个 window 对象存放在一个数组里面，
    // 与此同时，你应该删除相应的元素。
    mainWindow = null;
  });

  // 开发环境下打开开发者工具
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