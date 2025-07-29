#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用配置
"""

from flask import Flask, jsonify
from flask_cors import CORS
from loguru import logger
import os

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    from .routes import symbolic_regression_bp, monte_carlo_bp, data_bp
    
    app.register_blueprint(symbolic_regression_bp)
    app.register_blueprint(monte_carlo_bp)
    app.register_blueprint(data_bp)
    
    # 健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查端点"""
        return jsonify({
            'status': 'healthy',
            'service': '中药多组分均化分析后端服务',
            'version': '1.0.0'
        })
    
    # 根路径
    @app.route('/', methods=['GET'])
    def root():
        """根路径"""
        return jsonify({
            'message': '中药多组分均化分析后端服务',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'symbolic_regression': '/api/regression/symbolic-regression',
                'monte_carlo': '/api/monte-carlo/analyze',
                'data_upload': '/api/data/upload'
            }
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '接口不存在',
            'message': '请求的API接口不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'message': '服务器发生内部错误，请稍后重试'
        }), 500
    
    logger.info("✅ Flask应用创建完成")
    return app 