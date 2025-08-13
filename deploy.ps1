# deploy.ps1 - 用于在 Windows 上设置本草智配客户端开发环境的脚本。

# 检查是否以管理员权限运行
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "请以管理员权限运行此脚本!"
    Break
}

# 遇到任何错误则停止
$ErrorActionPreference = "Stop"

Write-Host "正在开始部署本草智配客户端..."
Write-Host "本脚本将配置 Python 后端和 Node.js 前端。"

# --- 预检环境 ---
Write-Host "步骤 1: 检查环境依赖 (Python 和 Node.js)..."

# 检查并安装 Python
$pythonVersion = try { python --version 2>&1 } catch { $null }
if ($null -eq $pythonVersion -or $pythonVersion -notmatch "Python 3") {
    Write-Host "未检测到 Python 3，准备安装..." -ForegroundColor Yellow
    
    # 下载 Python 安装程序
    $pythonVer = "3.13.0"
    $pythonUrl = "https://www.python.org/ftp/python/$pythonVer/python-$pythonVer-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-$pythonVer-amd64.exe"
    
    Write-Host "正在下载 Python $pythonVer..."
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    
    # 安装 Python
    Write-Host "正在安装 Python..."
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
    
    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # 等待一下让系统完成环境变量更新
    Start-Sleep -Seconds 2
    
    # 验证安装
    $pythonVersion = try { python --version 2>&1 } catch { $null }
    if ($null -eq $pythonVersion) {
        Write-Error "Python 安装似乎失败了。请尝试重启终端后重新运行脚本。"
        exit 1
    }
    Write-Host "- Python 安装完成：$pythonVersion"
} else {
    Write-Host "- 已找到 Python: $pythonVersion"
}

# 检查并安装 Node.js
$nodeVersion = try { node --version 2>&1 } catch { $null }
if ($null -eq $nodeVersion) {
    Write-Host "未检测到 Node.js，准备安装..." -ForegroundColor Yellow
    
    # 下载 Node.js 安装程序
    $nodeVer = "20.11.1"  # LTS版本
    $nodeUrl = "https://nodejs.org/dist/v$nodeVer/node-v$nodeVer-x64.msi"
    $nodeInstaller = "$env:TEMP\node-v$nodeVer-x64.msi"
    
    Write-Host "正在下载 Node.js $nodeVer..."
    Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller
    
    # 安装 Node.js
    Write-Host "正在安装 Node.js..."
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", $nodeInstaller, "/quiet", "/norestart" -Wait
    
    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # 等待一下让系统完成环境变量更新
    Start-Sleep -Seconds 2
    
    # 验证安装
    $nodeVersion = try { node --version 2>&1 } catch { $null }
    if ($null -eq $nodeVersion) {
        Write-Error "Node.js 安装似乎失败了。请尝试重启终端后重新运行脚本。"
        exit 1
    }
    Write-Host "- Node.js 安装完成：$nodeVersion"
} else {
    Write-Host "- 已找到 Node.js: $nodeVersion"
}

# 检查 npm
$npmVersion = try { npm --version 2>&1 } catch { $null }
if ($null -eq $npmVersion) {
    Write-Error "错误: 未找到 npm 或未将其添加到系统 PATH。npm 通常随 Node.js 一起安装。"
    exit 1
} else {
    Write-Host "- 已找到 npm: $npmVersion"
}

Write-Host "环境预检通过。"
Write-Host ""

# --- 后端配置 ---
Write-Host "步骤 2: 配置 Python 后端..."

$backendDir = ".\backend"
if (-not (Test-Path $backendDir)) {
    Write-Error "错误: 在当前目录下未找到后端文件夹 '$backendDir'。"
    exit 1
}

Push-Location $backendDir

$venvDir = ".\venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "- 正在创建 Python 虚拟环境于 '$venvDir'..."
    python -m venv $venvDir
    Write-Host "- 虚拟环境已创建。"
} else {
    Write-Host "- Python 虚拟环境已存在。"
}

Write-Host "- 正在激活虚拟环境并从 requirements.txt 安装依赖..."
# 注意: 激活仅对当前脚本会话有效
try {
    # 使用直接路径调用 python 和 pip，而不是激活虚拟环境
    $pythonPath = Join-Path -Path $venvDir -ChildPath "Scripts\python.exe"
    $pipPath = Join-Path -Path $venvDir -ChildPath "Scripts\pip.exe"
    
    if (-not (Test-Path $pythonPath) -or -not (Test-Path $pipPath)) {
        Write-Error "虚拟环境中未找到 Python 或 pip 可执行文件"
        exit 1
    }
    
    Write-Host "- 正在升级 pip..."
    & $pythonPath -m pip install --upgrade pip
    
    Write-Host "- 正在安装 Python 依赖..."
    & $pythonPath -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Python 依赖安装失败"
        exit 1
    }
} catch {
    Write-Error "Python 环境配置失败: $_"
    exit 1
}

Write-Host "后端配置完成。"
Pop-Location
Write-Host ""

# --- 前端配置 ---
Write-Host "步骤 3: 配置 Node.js 前端..."

$frontendDir = ".\frontend"
if (-not (Test-Path $frontendDir)) {
    Write-Error "错误: 在当前目录下未找到前端文件夹 '$frontendDir'。"
    exit 1
}

Push-Location $frontendDir

Write-Host "- 正在安装 npm 依赖..."
try {
    # 清理 node_modules（如果存在）
    if (Test-Path "node_modules") {
        Write-Host "- 清理现有 node_modules..."
        Remove-Item -Recurse -Force "node_modules"
    }
    
    # 清理 package-lock.json（如果存在）
    if (Test-Path "package-lock.json") {
        Remove-Item -Force "package-lock.json"
    }
    
    # 设置npm镜像（可选，如果需要加速可以取消注释）
    # npm config set registry https://registry.npmmirror.com
    
    # 安装依赖
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "npm 依赖安装失败"
        exit 1
    }
} catch {
    Write-Error "前端配置失败: $_"
    exit 1
}

Write-Host "前端配置完成。"
Pop-Location
Write-Host ""

Write-Host "部署成功!"
Write-Host "要启动应用程序, 请从项目根目录运行 'start.ps1' 脚本。"
