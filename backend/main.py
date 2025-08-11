#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中药多组分均化分析后端服务
主入口文件
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.app import create_app
from utils.logger import setup_logger
from utils.config import load_config

def main():
    """主函数"""
    # 设置日志
    logger = setup_logger()
    logger.info("🚀 启动本草智配后端服务...")
    
    # 加载配置
    config = load_config()
    
    # 创建Flask应用
    app = create_app(config)
    
    # 获取运行参数
    host = config.get('host', '127.0.0.1')
    port = config.get('port', 5000)
    debug = config.get('debug', False)
    
    logger.info(f"📡 服务将在 {host}:{port} 启动")
    logger.info(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    
    try:
        # 启动Flask应用
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("👋 服务已停止")
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 