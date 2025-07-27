#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中药多组分均化分析后端服务 - 打包版本
主入口文件
"""

import os
import sys
import tempfile
from pathlib import Path

def get_resource_path(relative_path):
    """获取资源文件路径，兼容打包后的环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包环境，使用当前文件所在目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 添加项目根目录到Python路径
if getattr(sys, 'frozen', False):
    # 打包后的环境
    project_root = Path(sys.executable).parent
else:
    # 开发环境
    project_root = Path(__file__).parent

sys.path.insert(0, str(project_root))

from api.app import create_app
from utils.logger import setup_logger
from utils.config import load_config

def setup_packaged_environment():
    """设置打包后的运行环境"""
    # 创建临时目录用于日志
    temp_dir = tempfile.gettempdir()
    log_dir = os.path.join(temp_dir, 'tcm-homogenizer', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置环境变量
    os.environ['LOG_DIR'] = log_dir
    os.environ['TEMP_DIR'] = temp_dir
    
    return log_dir

def main():
    """主函数"""
    # 设置打包环境
    log_dir = setup_packaged_environment()
    
    # 设置日志
    logger = setup_logger()
    logger.info("🚀 启动中药多组分均化分析后端服务 (打包版本)...")
    
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
    logger.info(f"📁 日志目录: {log_dir}")
    
    try:
        # 启动Flask应用
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False  # 打包后禁用重载器
        )
    except KeyboardInterrupt:
        logger.info("👋 服务已停止")
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        # 在Windows上保持窗口打开
        if os.name == 'nt':
            input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main() 