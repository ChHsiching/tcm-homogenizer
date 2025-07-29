#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中药多组分均化分析后端服务主程序
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from api.app import create_app
from loguru import logger

def main():
    """主函数"""
    # 设置日志
    setup_logger()
    
    # 创建Flask应用
    app = create_app()
    
    # 获取配置
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 启动服务
    logger.info(f"📡 服务将在 {host}:{port} 启动")
    logger.info(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False  # 避免重复启动
    )

if __name__ == '__main__':
    main() 