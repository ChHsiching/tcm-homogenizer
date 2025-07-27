#!/bin/bash

# 中药多组分均化分析客户端 - 项目状态检查脚本

echo "🔍 检查项目状态..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 项目根目录: $PROJECT_ROOT"
echo ""

# 检查Git状态
echo "📋 Git状态:"
if [ -d ".git" ]; then
    echo "   ✅ Git仓库已初始化"
    echo "   📍 当前分支: $(git branch --show-current)"
    echo "   🔄 未提交更改: $(git status --porcelain | wc -l | tr -d ' ') 个文件"
else
    echo "   ❌ Git仓库未初始化"
fi
echo ""

# 检查后端状态
echo "🐍 后端状态:"
if [ -d "backend/venv" ]; then
    echo "   ✅ Python虚拟环境存在"
    
    # 检查后端服务是否运行
    if curl -s http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
        echo "   ✅ 后端服务运行中 (http://127.0.0.1:5000)"
    else
        echo "   ❌ 后端服务未运行"
    fi
else
    echo "   ❌ Python虚拟环境不存在"
fi
echo ""

# 检查前端状态
echo "⚡ 前端状态:"
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ Node.js依赖已安装"
    
    # 检查Electron进程
    if pgrep -f "electron" > /dev/null; then
        echo "   ✅ Electron应用运行中"
    else
        echo "   ❌ Electron应用未运行"
    fi
else
    echo "   ❌ Node.js依赖未安装"
fi
echo ""

# 检查端口占用
echo "🔌 端口占用情况:"
if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "   ✅ 端口 5000 被占用 (后端服务)"
else
    echo "   ❌ 端口 5000 未被占用"
fi
echo ""

# 检查磁盘空间
echo "💾 磁盘空间:"
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}')
echo "   📊 当前目录使用率: $DISK_USAGE"
echo ""

# 检查最近日志
echo "📝 最近日志:"
if [ -f "backend/backend.log" ]; then
    echo "   📄 后端日志: $(tail -1 backend/backend.log 2>/dev/null | cut -c1-50)..."
else
    echo "   📄 后端日志: 无"
fi
echo ""

echo "✅ 状态检查完成" 