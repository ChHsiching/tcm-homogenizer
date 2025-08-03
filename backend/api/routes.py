#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

from flask import Blueprint, request, jsonify
from loguru import logger
import traceback

from algorithms.symbolic_regression import SymbolicRegression
from algorithms.monte_carlo import MonteCarloAnalysis
from utils.data_loader import DataLoader

# 创建蓝图
symbolic_regression_bp = Blueprint('symbolic_regression', __name__)
monte_carlo_bp = Blueprint('monte_carlo', __name__)
data_bp = Blueprint('data', __name__)

# 全局实例
regression_engine = SymbolicRegression()
monte_carlo_engine = MonteCarloAnalysis()
data_loader = DataLoader()

# 符号回归路由
@symbolic_regression_bp.route('/analyze', methods=['POST'])
def analyze():
    """符号回归分析"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': '参数缺失',
                    'message': f'缺少必要参数: {field}'
                }), 400
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        population_size = data.get('population_size', 100)
        generations = data.get('generations', 50)
        
        logger.info(f"开始符号回归分析，目标变量: {target_column}")
        logger.info(f"特征变量: {feature_columns}")
        
        # 执行符号回归
        result = regression_engine.analyze(
            data=input_data,
            target_column=target_column,
            feature_columns=feature_columns,
            population_size=population_size,
            generations=generations
        )
        
        logger.info("符号回归分析完成")
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"符号回归分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '分析失败',
            'message': str(e)
        }), 500

@symbolic_regression_bp.route('/models', methods=['GET'])
def get_models():
    """获取已保存的模型列表"""
    try:
        models = regression_engine.get_saved_models()
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

@symbolic_regression_bp.route('/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """获取特定模型详情"""
    try:
        model = regression_engine.get_model(model_id)
        if model:
            return jsonify({
                'success': True,
                'model': model
            })
        else:
            return jsonify({
                'error': '模型不存在',
                'message': f'模型ID {model_id} 不存在'
            }), 404
    except Exception as e:
        logger.error(f"获取模型详情失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

# 蒙特卡罗分析路由
@monte_carlo_bp.route('/analyze', methods=['POST'])
def monte_carlo_analyze():
    """蒙特卡罗配比分析"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['model_id', 'target_efficacy', 'iterations']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': '参数缺失',
                    'message': f'缺少必要参数: {field}'
                }), 400
        
        # 获取参数
        model_id = data['model_id']
        target_efficacy = data['target_efficacy']
        iterations = data['iterations']
        tolerance = data.get('tolerance', 0.1)
        component_ranges = data.get('component_ranges', {})
        
        logger.info(f"开始蒙特卡罗分析，模型ID: {model_id}")
        logger.info(f"目标药效: {target_efficacy}, 模拟次数: {iterations}")
        
        # 执行蒙特卡罗分析
        result = monte_carlo_engine.analyze(
            model_id=model_id,
            target_efficacy=target_efficacy,
            iterations=iterations,
            tolerance=tolerance,
            component_ranges=component_ranges
        )
        
        logger.info("蒙特卡罗分析完成")
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"蒙特卡罗分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '分析失败',
            'message': str(e)
        }), 500

@monte_carlo_bp.route('/results/<analysis_id>', methods=['GET'])
def get_monte_carlo_result(analysis_id):
    """获取蒙特卡罗分析结果"""
    try:
        result = monte_carlo_engine.get_result(analysis_id)
        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'error': '结果不存在',
                'message': f'分析ID {analysis_id} 不存在'
            }), 404
    except Exception as e:
        logger.error(f"获取蒙特卡罗结果失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

# 数据处理路由
@data_bp.route('/upload', methods=['POST'])
def upload_data():
    """上传数据文件"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': '文件缺失',
                'message': '请选择要上传的文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': '文件缺失',
                'message': '请选择要上传的文件'
            }), 400
        
        # 处理文件上传
        result = data_loader.upload_file(file)
        
        logger.info(f"文件上传成功: {file.filename}")
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'error': '上传失败',
            'message': str(e)
        }), 500

@data_bp.route('/validate', methods=['POST'])
def validate_data():
    """验证数据格式"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': '数据缺失',
                'message': '请提供要验证的数据'
            }), 400
        
        # 验证数据
        validation_result = data_loader.validate_data(data['data'])
        
        return jsonify({
            'success': True,
            'result': validation_result
        })
        
    except Exception as e:
        logger.error(f"数据验证失败: {str(e)}")
        return jsonify({
            'error': '验证失败',
            'message': str(e)
        }), 500

@data_bp.route('/preview', methods=['POST'])
def preview_data():
    """预览数据"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': '数据缺失',
                'message': '请提供要预览的数据'
            }), 400
        
        # 生成数据预览
        preview = data_loader.generate_preview(data['data'])
        
        return jsonify({
            'success': True,
            'result': preview
        })
        
    except Exception as e:
        logger.error(f"数据预览失败: {str(e)}")
        return jsonify({
            'error': '预览失败',
            'message': str(e)
        }), 500 