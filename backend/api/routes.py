#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

from flask import Blueprint, request, jsonify
from algorithms.symbolic_regression import analyze_symbolic_regression
from algorithms.monte_carlo import perform_monte_carlo_analysis
from loguru import logger
import pandas as pd
import numpy as np

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局变量存储当前模型
current_model = None
current_data = None

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend service is running'
    })

@api_bp.route('/symbolic-regression', methods=['POST'])
def symbolic_regression():
    """符号回归分析端点"""
    global current_model, current_data
    
    try:
        data = request.get_json()
        logger.info("收到符号回归分析请求")
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要参数: {field}'
                }), 400
        
        # 获取参数
        df_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        
        # 可选参数
        population_size = data.get('population_size', 100)
        generations = data.get('generations', 50)
        test_ratio = data.get('test_ratio', 0.3)
        operators = data.get('operators', ['add', 'sub', 'mul', 'div'])
        
        logger.info(f"参数: population_size={population_size}, generations={generations}, test_ratio={test_ratio}")
        logger.info(f"运算符: {operators}")
        
        # 数据预处理
        df = pd.DataFrame(df_data)
        
        # 检查列是否存在
        if target_column not in df.columns:
            return jsonify({
                'success': False,
                'error': f'目标变量列 "{target_column}" 不存在'
            }), 400
        
        for col in feature_columns:
            if col not in df.columns:
                return jsonify({
                    'success': False,
                    'error': f'特征变量列 "{col}" 不存在'
                }), 400
        
        # 数据质量检查
        if len(df) < 10:
            return jsonify({
                'success': False,
                'error': '数据样本数量太少，至少需要10个样本'
            }), 400
        
        # 检查数值类型
        for col in [target_column] + feature_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return jsonify({
                    'success': False,
                    'error': f'列 "{col}" 不是数值类型'
                }), 400
        
        # 处理缺失值
        df = df.fillna(0)
        
        # 执行符号回归分析
        result = analyze_symbolic_regression(
            data=df,
            target_column=target_column,
            feature_columns=feature_columns,
            test_ratio=test_ratio,
            population_size=population_size,
            generations=generations,
            operators=operators
        )
        
        if result is None:
            return jsonify({
                'success': False,
                'error': '符号回归分析失败，无法找到有效解'
            }), 500
        
        # 保存当前模型和数据
        current_model = result
        current_data = {
            'data': df_data,
            'target_column': target_column,
            'feature_columns': feature_columns
        }
        
        # 格式化特征重要性
        feature_importance = []
        for var, importance in result['feature_importance'].items():
            # 将变量名映射回原始特征名
            var_idx = int(var.replace('x', ''))
            if var_idx < len(feature_columns):
                feature_name = feature_columns[var_idx]
                feature_importance.append({
                    'feature': feature_name,
                    'importance': float(importance)
                })
        
        # 按重要性排序
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        response = {
            'success': True,
            'expression': result['expression'],
            'r2': result['test_r2'],
            'mse': result['test_mse'],
            'mae': result['test_mae'],
            'rmse': np.sqrt(result['test_mse']),
            'r2_train': result['train_r2'],
            'mse_train': result['train_mse'],
            'mae_train': result['train_mae'],
            'feature_importance': feature_importance,
            'tree_structure': result['tree_structure'],
            'parameters': {
                'population_size': population_size,
                'generations': generations,
                'test_ratio': test_ratio,
                'operators': operators
            }
        }
        
        logger.info(f"符号回归分析完成，R² = {result['test_r2']:.3f}, MSE = {result['test_mse']:.3f}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"符号回归分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'符号回归分析失败: {str(e)}'
        }), 500

@api_bp.route('/monte-carlo', methods=['POST'])
def monte_carlo():
    """蒙特卡罗分析端点"""
    global current_model, current_data
    
    try:
        data = request.get_json()
        logger.info("收到蒙特卡罗分析请求")
        
        if current_model is None or current_data is None:
            return jsonify({
                'success': False,
                'error': '请先完成符号回归分析'
            }), 400
        
        # 获取参数
        iterations = data.get('iterations', 10000)
        target_efficacy = data.get('target_efficacy', None)
        tolerance = data.get('tolerance', 0.1)
        
        # 执行蒙特卡罗分析
        result = perform_monte_carlo_analysis(
            model=current_model,
            data=current_data,
            iterations=iterations,
            target_efficacy=target_efficacy,
            tolerance=tolerance
        )
        
        if result is None:
            return jsonify({
                'success': False,
                'error': '蒙特卡罗分析失败'
            }), 500
        
        logger.info("蒙特卡罗分析完成")
        return jsonify({
            'success': True,
            'results': result
        })
        
    except Exception as e:
        logger.error(f"蒙特卡罗分析失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'蒙特卡罗分析失败: {str(e)}'
        }), 500

@api_bp.route('/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    global current_model
    
    models = []
    if current_model:
        models.append({
            'id': 'current',
            'expression': current_model['expression'],
            'r2': current_model['test_r2'],
            'mse': current_model['test_mse']
        })
    
    return jsonify({
        'success': True,
        'models': models
    }) 