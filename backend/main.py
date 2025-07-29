#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中药多组分均化分析后端服务
"""

import os
import sys
import signal
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from api.app import create_app

# 全局logger变量
logger = None

def signal_handler(signum, frame):
    """信号处理器"""
    if logger:
        logger.info("🛑 收到停止信号，正在关闭服务...")
    sys.exit(0)

def main():
    """主函数"""
    global logger
    
    try:
        # 设置日志
        logger = setup_logger()
        logger.info("🚀 启动中药多组分均化分析后端服务...")
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 创建Flask应用
        logger.info("🔧 创建Flask应用...")
        app = create_app()
        logger.info("✅ Flask应用创建完成")
        
        # 配置
        host = '127.0.0.1'
        port = 5000
        debug = False
        
        logger.info(f"📡 服务将在 {host}:{port} 启动")
        logger.info(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        
        # 启动服务
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # 避免重复启动
        )
        
    except KeyboardInterrupt:
        if logger:
            logger.info("🛑 用户中断，正在关闭服务...")
    except Exception as e:
        if logger:
            logger.error(f"❌ 服务启动失败: {str(e)}")
            logger.error(f"详细错误: {sys.exc_info()}")
        sys.exit(1)

if __name__ == '__main__':
    main() 