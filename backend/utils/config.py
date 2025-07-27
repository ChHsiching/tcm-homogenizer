#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    """加载配置"""
    # 加载环境变量
    load_dotenv()
    
    # 默认配置
    config = {
        'host': os.getenv('HOST', '127.0.0.1'),
        'port': int(os.getenv('PORT', 5000)),
        'debug': os.getenv('DEBUG', 'False').lower() == 'true',
        
        # 数据库配置
        'database': {
            'url': os.getenv('DATABASE_URL', 'sqlite:///tcm_homogenizer.db')
        },
        
        # 算法配置
        'algorithm': {
            'max_population_size': int(os.getenv('MAX_POPULATION_SIZE', 1000)),
            'max_generations': int(os.getenv('MAX_GENERATIONS', 100)),
            'max_monte_carlo_iterations': int(os.getenv('MAX_MONTE_CARLO_ITERATIONS', 100000))
        },
        
        # 文件上传配置
        'upload': {
            'max_file_size': int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024)),  # 10MB
            'allowed_extensions': os.getenv('ALLOWED_EXTENSIONS', 'csv,xlsx,json').split(','),
            'upload_folder': os.getenv('UPLOAD_FOLDER', 'uploads')
        },
        
        # 日志配置
        'logging': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'file': os.getenv('LOG_FILE', 'logs/app.log')
        }
    }
    
    return config

def get_config_value(key, default=None):
    """获取配置值"""
    config = load_config()
    
    # 支持嵌套键，如 'algorithm.max_population_size'
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value 