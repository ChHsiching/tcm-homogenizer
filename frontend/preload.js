const { contextBridge, ipcRenderer } = require('electron');

// 暴露受保护的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 后端服务管理
  startBackend: () => ipcRenderer.invoke('start-backend'),
  stopBackend: () => ipcRenderer.invoke('stop-backend'),
  
  // 菜单事件监听
  onMenuImportData: (callback) => ipcRenderer.on('menu-import-data', callback),
  onMenuExportResults: (callback) => ipcRenderer.on('menu-export-results', callback),
  onMenuSymbolicRegression: (callback) => ipcRenderer.on('menu-symbolic-regression', callback),
  onMenuMonteCarlo: (callback) => ipcRenderer.on('menu-monte-carlo', callback),
  onMenuAbout: (callback) => ipcRenderer.on('menu-about', callback),
  
  // 移除事件监听器
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // 文件操作
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: () => ipcRenderer.invoke('dialog:saveFile'),
  
  // 通知
  showNotification: (title, body) => ipcRenderer.invoke('notification:show', title, body),
  
  // 系统信息
  getPlatform: () => process.platform,
  getVersion: () => process.versions.electron
}); 