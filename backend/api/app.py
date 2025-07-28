#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用配置和路由
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import time
from loguru import logger

from .routes import symbolic_regression_bp, monte_carlo_bp, data_bp

def create_app(config=None):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 应用配置
    if config:
        app.config.update(config)
    
    # 注册蓝图
    app.register_blueprint(symbolic_regression_bp, url_prefix='/api/regression')
    app.register_blueprint(monte_carlo_bp, url_prefix='/api/monte-carlo')
    app.register_blueprint(data_bp, url_prefix='/api/data')
    
    # 全局错误处理
    @app.errorhandler(Exception)
    def handle_exception(e):
        """全局异常处理"""
        logger.error(f"未处理的异常: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'message': str(e)
        }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({
            'success': False,
            'error': '接口不存在',
            'message': '请求的API接口不存在'
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        """400错误处理"""
        return jsonify({
            'success': False,
            'error': '请求参数错误',
            'message': '请检查请求参数'
        }), 400
    
    # 健康检查接口
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': '中药多组分均化分析后端',
            'version': '1.0.0',
            'timestamp': time.time()
        })
    
    # 根路径
    @app.route('/', methods=['GET'])
    def root():
        """根路径"""
        return jsonify({
            'success': True,
            'message': '中药多组分均化分析后端服务',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'regression': '/api/regression',
                'monte_carlo': '/api/monte-carlo',
                'data': '/api/data'
            }
        })
    
    logger.info("✅ Flask应用创建完成")
    return app 