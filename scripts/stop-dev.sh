#!/usr/bin/env bash
# 本草智配客户端 - 停止开发环境脚本

set -e

echo "🛑 停止本草智配客户端开发环境..."

pkill -f "python main.py" || true
pkill -f electron || true 