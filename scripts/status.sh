#!/usr/bin/env bash
# 本草智配客户端 - 项目状态检查脚本

ps aux | grep -E "python main.py|http.server 3000" | grep -v grep 