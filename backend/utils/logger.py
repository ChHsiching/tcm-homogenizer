#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
"""

import sys
from pathlib import Path
from loguru import logger

def setup_logger():
    """设置日志配置"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 控制台日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level="INFO",
        colorize=True
    )
    
    # 添加文件处理器（所有级别）
    logger.add(
        log_dir / "app.log",
        format=file_format,
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # 添加错误日志文件
    logger.add(
        log_dir / "error.log",
        format=file_format,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("📝 日志系统初始化完成")
    return logger 