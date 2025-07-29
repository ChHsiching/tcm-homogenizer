#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

from flask import Blueprint, request, jsonify
from loguru import logger
import traceback
import pandas as pd

from algorithms.symbolic_regression import perform_symbolic_regression_gplearn
from algorithms.monte_carlo import MonteCarloAnalysis
from utils.data_loader import DataLoader

# 创建蓝图
symbolic_regression_bp = Blueprint('symbolic_regression', __name__, url_prefix='/api/regression')
monte_carlo_bp = Blueprint('monte_carlo', __name__, url_prefix='/api/monte-carlo')
data_bp = Blueprint('data', __name__, url_prefix='/api/data')

# 全局实例
monte_carlo_engine = MonteCarloAnalysis()
data_loader = DataLoader()

# 符号回归分析路由
@symbolic_regression_bp.route('/symbolic-regression', methods=['POST'])
def symbolic_regression():
    """符号回归分析"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False, 
                    'error': f'缺少必要参数: {field}',
                    'message': '请检查数据格式是否正确'
                })
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        population_size = data.get('population_size', 100)
        generations = data.get('generations', 50)
        test_ratio = data.get('test_ratio', 0.3)
        operators = data.get('operators', ['+', '-', '*', '/'])
        
        logger.info(f"开始符号回归分析，目标变量: {target_column}, 特征数量: {len(feature_columns)}")
        
        # 数据预处理
        df = pd.DataFrame(input_data)
        
        # 检查列是否存在
        if target_column not in df.columns:
            return jsonify({
                'success': False, 
                'error': f'目标变量列 "{target_column}" 不存在',
                'message': '请检查目标变量列名是否正确'
            })
        
        for col in feature_columns:
            if col not in df.columns:
                return jsonify({
                    'success': False, 
                    'error': f'特征变量列 "{col}" 不存在',
                    'message': '请检查特征变量列名是否正确'
                })
        
        # 提取数据
        X = df[feature_columns]
        y = df[target_column]
        
        # 数据质量检查
        if len(y) < 10:
            return jsonify({
                'success': False, 
                'error': '数据样本数量太少，至少需要10个样本',
                'message': '请上传更多数据样本'
            })
        
        if y.std() < 1e-6:
            return jsonify({
                'success': False, 
                'error': '目标变量没有变化，无法进行回归分析',
                'message': '请检查目标变量是否有足够的变化'
            })
        
        # 检查数据长度一致性
        if len(X) != len(y):
            return jsonify({
                'success': False, 
                'error': '数据长度不一致',
                'message': '请检查CSV文件中的数据列长度是否一致'
            })
        
        # 检查NaN值
        if X.isnull().any().any() or y.isnull().any():
            return jsonify({
                'success': False, 
                'error': '数据包含NaN值',
                'message': '请检查数据中是否有缺失值或无效数据'
            })
        
        # 执行符号回归（使用新的HeuristicLab算法）
        result = perform_symbolic_regression_gplearn(
            data=df,
            target_column=target_column,
            population_size=population_size,
            generations=generations,
            operators=operators,
            test_ratio=test_ratio
        )
        
        if result['success']:
            logger.info(f"符号回归分析完成，R² = {result['metrics']['r2_test']:.3f}")
            return jsonify(result)
        else:
            return jsonify({
                'success': False, 
                'error': result['error'],
                'message': '符号回归分析失败，请检查数据质量或调整参数'
            })
            
    except Exception as e:
        logger.error(f"符号回归分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': '符号回归分析失败，请检查数据格式和参数设置'
        })

@symbolic_regression_bp.route('/models', methods=['GET'])
def get_models():
    """获取已保存的模型列表"""
    try:
        return jsonify({
            'success': True,
            'models': []
        })
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取模型列表失败'
        })

@symbolic_regression_bp.route('/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """获取特定模型详情"""
    try:
        return jsonify({
            'success': False,
            'error': '模型不存在',
            'message': f'模型ID {model_id} 不存在'
        })
    except Exception as e:
        logger.error(f"获取模型详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取模型详情失败'
        })

# 蒙特卡罗分析路由
@monte_carlo_bp.route('/analyze', methods=['POST'])
def monte_carlo_analysis():
    """蒙特卡罗分析"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要参数: {field}',
                    'message': '请检查数据格式是否正确'
                })
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        n_simulations = data.get('n_simulations', 1000)
        confidence_level = data.get('confidence_level', 0.95)
        
        logger.info(f"开始蒙特卡罗分析，目标变量: {target_column}, 特征数量: {len(feature_columns)}")
        
        # 数据预处理
        df = pd.DataFrame(input_data)
        
        # 检查列是否存在
        if target_column not in df.columns:
            return jsonify({
                'success': False,
                'error': f'目标变量列 "{target_column}" 不存在',
                'message': '请检查目标变量列名是否正确'
            })
        
        for col in feature_columns:
            if col not in df.columns:
                return jsonify({
                    'success': False,
                    'error': f'特征变量列 "{col}" 不存在',
                    'message': '请检查特征变量列名是否正确'
                })
        
        # 提取数据
        X = df[feature_columns]
        y = df[target_column]
        
        # 数据质量检查
        if len(y) < 10:
            return jsonify({
                'success': False,
                'error': '数据样本数量太少，至少需要10个样本',
                'message': '请上传更多数据样本'
            })
        
        # 检查数据长度一致性
        if len(X) != len(y):
            return jsonify({
                'success': False,
                'error': '数据长度不一致',
                'message': '请检查CSV文件中的数据列长度是否一致'
            })
        
        # 检查NaN值
        if X.isnull().any().any() or y.isnull().any():
            return jsonify({
                'success': False,
                'error': '数据包含NaN值',
                'message': '请检查数据中是否有缺失值或无效数据'
            })
        
        # 执行蒙特卡罗分析
        result = monte_carlo_engine.analyze(
            data={'data': input_data},
            target_column=target_column,
            feature_columns=feature_columns,
            n_simulations=n_simulations,
            confidence_level=confidence_level
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"蒙特卡罗分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '蒙特卡罗分析失败，请检查数据格式和参数设置'
        })

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
                'success': False,
                'error': f'分析ID {analysis_id} 不存在',
                'message': '未找到指定的分析结果'
            })
    except Exception as e:
        logger.error(f"获取蒙特卡罗结果失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取分析结果失败'
        })

# 数据处理路由
@data_bp.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '请选择要上传的文件',
                'message': '请选择CSV文件进行上传'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '请选择要上传的文件',
                'message': '请选择CSV文件进行上传'
            })
        
        # 处理文件上传
        result = data_loader.upload_file(file)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': '文件上传失败，请检查文件格式'
            })
            
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '文件上传失败，请检查文件格式和网络连接'
        })

@data_bp.route('/validate', methods=['POST'])
def validate_data():
    """数据验证接口"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'success': False,
                'error': '请提供要验证的数据',
                'message': '请提供要验证的数据'
            })
        
        # 验证数据
        result = data_loader.validate_data(data['data'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': '数据验证失败，请检查数据格式'
            })
            
    except Exception as e:
        logger.error(f"数据验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '数据验证失败，请检查数据格式'
        })

@data_bp.route('/preview', methods=['POST'])
def preview_data():
    """数据预览接口"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'success': False,
                'error': '请提供要预览的数据',
                'message': '请提供要预览的数据'
            })
        
        # 生成数据预览
        result = data_loader.preview_data(data['data'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': '数据预览失败，请检查数据格式'
            })
            
    except Exception as e:
        logger.error(f"数据预览失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '数据预览失败，请检查数据格式'
        }) 