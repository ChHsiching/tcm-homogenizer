# stop.ps1 - 停止所有与本草智配客户端相关的进程

Write-Host "正在停止本草智配客户端服务..."

# --- 停止后端进程 ---
Write-Host "正在查找并停止 Python 后端进程 (main.py)..."
$pythonProcesses = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*python*main.py*" }
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Host "- 正在停止进程 ID: $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force
    }
    Write-Host "Python 后端进程已停止。"
} else {
    Write-Host "未找到正在运行的 Python 后端进程。"
}

# --- 停止前端进程 ---
Write-Host "正在查找并停止 Electron/Node.js 前端进程..."
# 查找主 Electron 进程
$electronProcesses = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "本草智配客户端.exe" -or ($_.Name -eq "node.exe" -and $_.CommandLine -like "*electron*") }
if ($electronProcesses) {
    $electronProcesses | ForEach-Object {
        Write-Host "- 正在停止进程 ID: $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force
    }
    Write-Host "Electron 前端进程已停止。"
} else {
    Write-Host "未找到正在运行的 Electron 前端进程。"
}

Write-Host ""
Write-Host "所有相关服务已停止。"
