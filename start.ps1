# start.ps1 - 启动本草智配客户端的后端和前端服务

Write-Host "正在启动本草智配客户端..."

# --- 启动后端 ---
Write-Host "步骤 1: 启动 Python 后端服务..."
$backendCommand = {
    $host.UI.RawUI.WindowTitle = "本草智配客户端 - 后端"
    cd .\backend
    & ".\venv\Scripts\activate.ps1"
    python main.py
}
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $backendCommand

# --- 启动前端 ---
Write-Host "步骤 2: 启动 Electron 前端..."
$frontendCommand = {
    $host.UI.RawUI.WindowTitle = "本草智配客户端 - 前端"
    cd .\frontend
    npm start
}
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host ""
Write-Host "应用程序已在新的终端窗口中启动。"
Write-Host "后端和前端服务正在分别运行。"
Write-Host "要停止所有服务, 请运行 'stop.ps1' 脚本。"
