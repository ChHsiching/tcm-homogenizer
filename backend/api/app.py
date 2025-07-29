#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用配置和路由
"""

from flask import Flask, request
from flask_cors import CORS
import traceback
from loguru import logger

def create_app():
    """创建Flask应用"""
    try:
        logger.info("🔧 开始创建Flask应用...")
        
        # 创建Flask应用
        app = Flask(__name__)
        
        # 配置CORS
        logger.info("🔧 配置CORS...")
        CORS(app, resources={
            r"/api/*": {
                "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
        
        # 注册蓝图
        logger.info("🔧 注册API蓝图...")
        from .routes import symbolic_regression_bp, monte_carlo_bp, data_bp
        
        app.register_blueprint(symbolic_regression_bp)
        app.register_blueprint(monte_carlo_bp)
        app.register_blueprint(data_bp)
        
        # 添加健康检查路由
        @app.route('/api/health', methods=['GET'])
        def health_check():
            """全局健康检查"""
            return {
                'status': 'healthy',
                'service': 'tcm-homogenizer-backend',
                'version': '1.0.0'
            }
        
        # 添加错误处理器
        @app.errorhandler(404)
        def not_found(error):
            logger.error(f"❌ 404错误: {request.url}")
            return {'error': '接口不存在', 'message': '请求的API接口不存在'}, 404
        
        @app.errorhandler(500)
        def internal_error(error):
            logger.error(f"❌ 500错误: {str(error)}")
            return {'error': '服务器内部错误', 'message': '服务器处理请求时发生错误'}, 500
        
        @app.errorhandler(Exception)
        def handle_exception(e):
            logger.error(f"❌ 未处理的异常: {str(e)}")
            logger.error(f"详细错误: {traceback.format_exc()}")
            return {'error': '服务器错误', 'message': '服务器发生未知错误'}, 500
        
        logger.info("✅ Flask应用创建完成")
        return app
        
    except Exception as e:
        logger.error(f"❌ Flask应用创建失败: {str(e)}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        raise 