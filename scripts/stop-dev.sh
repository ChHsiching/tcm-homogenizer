#!/usr/bin/env bash
# 本草智配客户端 - 停止开发环境脚本

pkill -f "python main.py"
pkill -f "http.server 3000"
echo "🛑 已停止本草智配客户端开发环境" 