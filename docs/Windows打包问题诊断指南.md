# Windows打包问题诊断指南

## 问题描述

Windows虚拟机打包后，应用可以安装和启动，但后端服务启动失败，无法连接。

## 快速诊断步骤

### 1. 检查后端exe文件

```cmd
# 检查后端exe是否存在
dir "C:\Program Files\中药多组分均化分析客户端\resources\tcm-backend.exe"

# 如果不存在，检查安装目录
dir "C:\Program Files\中药多组分均化分析客户端\"
```

### 2. 手动测试后端exe

```cmd
# 以管理员身份打开命令提示符
cd "C:\Program Files\中药多组分均化分析客户端\resources"

# 手动运行后端exe
tcm-backend.exe

# 观察输出信息，特别关注错误信息
```

### 3. 检查端口占用

```cmd
# 检查端口5000是否被占用
netstat -ano | findstr :5000

# 如果有占用，查看是哪个进程
tasklist /fi "pid eq <进程ID>"
```

### 4. 测试API连接

```cmd
# 在另一个命令提示符中测试API
curl http://127.0.0.1:5000/api/health

# 或者使用PowerShell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health"
```

### 5. 检查防火墙设置

```cmd
# 检查Windows防火墙规则
netsh advfirewall firewall show rule name=all | findstr "5000"

# 如果需要，添加防火墙规则
netsh advfirewall firewall add rule name="TCM Backend" dir=in action=allow protocol=TCP localport=5000
```

## 常见问题及解决方案

### 问题1：后端exe文件不存在

**症状**：`resources/tcm-backend.exe` 文件不存在

**原因**：
- PyInstaller打包失败
- 文件路径配置错误
- 安装程序未正确复制文件

**解决方案**：
1. 重新执行PyInstaller打包
2. 检查 `package.json` 中的 `extraResources` 配置
3. 验证打包后的文件结构

### 问题2：后端exe启动失败

**症状**：手动运行后端exe时出现错误

**可能原因**：
- 缺少依赖库
- Python环境问题
- 权限不足

**解决方案**：
1. 检查PyInstaller的 `hiddenimports` 配置
2. 确保所有依赖都已包含
3. 以管理员身份运行

### 问题3：端口被占用

**症状**：后端启动但无法绑定端口5000

**解决方案**：
1. 找到占用端口的进程并关闭
2. 修改后端配置使用其他端口
3. 重启计算机

### 问题4：防火墙阻止

**症状**：后端启动但外部无法连接

**解决方案**：
1. 添加Windows防火墙规则
2. 临时关闭防火墙测试
3. 检查杀毒软件设置

## 详细诊断流程

### 步骤1：环境检查

```cmd
# 检查系统信息
systeminfo | findstr "OS"

# 检查Python版本（如果安装了）
python --version

# 检查Node.js版本（如果安装了）
node --version
```

### 步骤2：文件完整性检查

```cmd
# 检查安装目录结构
tree "C:\Program Files\中药多组分均化分析客户端\" /F

# 检查文件大小
dir "C:\Program Files\中药多组分均化分析客户端\resources\tcm-backend.exe"
```

### 步骤3：进程监控

```cmd
# 启动应用后检查进程
tasklist | findstr "tcm"

# 检查端口监听
netstat -ano | findstr :5000
```

### 步骤4：日志分析

```cmd
# 查看Windows事件日志
eventvwr.msc

# 查看应用程序日志中的错误
```

## 修复建议

### 1. 重新打包后端

如果后端exe有问题，重新执行PyInstaller打包：

```cmd
cd backend
venv\Scripts\activate
pyinstaller --clean --debug tcm-backend.spec
```

### 2. 修改启动逻辑

在 `main.js` 中添加更多调试信息：

```javascript
function startBackend() {
  return new Promise((resolve) => {
    const backendPath = path.join(process.resourcesPath, 'tcm-backend.exe');
    
    // 添加详细日志
    console.log('Resource path:', process.resourcesPath);
    console.log('Backend path:', backendPath);
    console.log('File exists:', fs.existsSync(backendPath));
    console.log('File size:', fs.statSync(backendPath).size);
    
    // ... 其余代码
  });
}
```

### 3. 添加错误处理

```javascript
backendProcess.on('error', (error) => {
  console.error('Backend process error:', error);
  dialog.showErrorBox('后端错误', `启动失败: ${error.message}`);
});

backendProcess.on('exit', (code, signal) => {
  console.log('Backend process exited:', { code, signal });
  if (code !== 0) {
    dialog.showErrorBox('后端退出', `进程异常退出，代码: ${code}`);
  }
});
```

### 4. 使用备用端口

如果端口5000有问题，修改后端配置使用其他端口：

```python
# 在backend/main.py中
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=False)
```

然后更新前端连接地址。

## 预防措施

### 1. 打包前测试

```cmd
# 在打包前先测试后端exe
cd backend\dist
tcm-backend.exe

# 测试API
curl http://127.0.0.1:5000/api/health
```

### 2. 使用开发模式测试

```cmd
# 在build-temp目录中测试
npm start
```

### 3. 添加健康检查

在应用启动时添加健康检查：

```javascript
async function checkBackendHealth() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/health');
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}
```

## 联系支持

如果问题仍然存在，请提供以下信息：

1. Windows版本和架构
2. 错误日志和截图
3. 手动运行后端exe的输出
4. 网络诊断结果
5. 防火墙设置状态

---

**注意**：本指南基于常见的Windows打包问题。具体问题可能需要根据实际情况调整解决方案。 