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
from algorithms.monte_carlo import MonteCarloAnalyzer
from utils.data_loader import DataLoader

# 创建蓝图
symbolic_regression_bp = Blueprint('symbolic_regression', __name__)
monte_carlo_bp = Blueprint('monte_carlo', __name__)
data_bp = Blueprint('data', __name__)

# 符号回归分析
@symbolic_regression_bp.route('/symbolic-regression', methods=['POST'])
def symbolic_regression():
    """符号回归分析"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必要参数: {field}'})
        
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
            return jsonify({'success': False, 'error': f'目标变量列 "{target_column}" 不存在'})
        
        for col in feature_columns:
            if col not in df.columns:
                return jsonify({'success': False, 'error': f'特征变量列 "{col}" 不存在'})
        
        # 提取数据
        X = df[feature_columns]
        y = df[target_column]
        
        # 数据质量检查
        if len(y) < 10:
            return jsonify({'success': False, 'error': '数据样本数量太少，至少需要10个样本'})
        
        if y.std() < 1e-6:
            return jsonify({'success': False, 'error': '目标变量没有变化，无法进行回归分析'})
        
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
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        logger.error(f"符号回归分析失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 蒙特卡罗分析
@monte_carlo_bp.route('/analyze', methods=['POST'])
def monte_carlo_analyze():
    """蒙特卡罗分析"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必要参数: {field}'})
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        model_id = data.get('model_id')
        iterations = data.get('iterations', 1000)
        target_efficacy = data.get('target_efficacy', 0.8)
        tolerance = data.get('tolerance', 0.1)
        
        logger.info(f"开始蒙特卡罗分析，迭代次数: {iterations}")
        
        # 数据预处理
        df = pd.DataFrame(input_data)
        
        # 检查列是否存在
        if target_column not in df.columns:
            return jsonify({'success': False, 'error': f'目标变量列 "{target_column}" 不存在'})
        
        for col in feature_columns:
            if col not in df.columns:
                return jsonify({'success': False, 'error': f'特征变量列 "{col}" 不存在'})
        
        # 执行蒙特卡罗分析
        analyzer = MonteCarloAnalyzer()
        result = analyzer.analyze(
            data=df,
            target_column=target_column,
            feature_columns=feature_columns,
            model_id=model_id,
            iterations=iterations,
            target_efficacy=target_efficacy,
            tolerance=tolerance
        )
        
        if result['success']:
            logger.info(f"蒙特卡罗分析完成，有效样本率: {result['result']['valid_rate']:.2%}")
            return jsonify(result)
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        logger.error(f"蒙特卡罗分析失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 数据上传
@data_bp.route('/upload', methods=['POST'])
def upload_data():
    """数据上传接口"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({'success': False, 'error': '缺少数据参数'})
        
        # 验证数据格式
        df = pd.DataFrame(data['data'])
        
        if df.empty:
            return jsonify({'success': False, 'error': '数据为空'})
        
        # 返回数据信息
        result = {
            'success': True,
            'columns': df.columns.tolist(),
            'rows': len(df),
            'data': data['data']
        }
        
        logger.info(f"数据上传成功，列数: {len(df.columns)}, 行数: {len(df)}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"数据上传失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 获取模型列表
@symbolic_regression_bp.route('/models', methods=['GET'])
def get_models():
    """获取模型列表"""
    try:
        # 这里应该从数据库或文件系统获取模型列表
        # 目前返回空列表
        models = []
        
        return jsonify({
            'success': True,
            'models': models
        })
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 获取模型详情
@symbolic_regression_bp.route('/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """获取模型详情"""
    try:
        # 这里应该从数据库或文件系统获取模型详情
        # 目前返回空数据
        model = None
        
        if model is None:
            return jsonify({'success': False, 'error': '模型不存在'})
        
        return jsonify({
            'success': True,
            'model': model
        })
        
    except Exception as e:
        logger.error(f"获取模型详情失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}) 