#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

from flask import Blueprint, request, jsonify
from loguru import logger
import traceback
import pandas as pd
import numpy as np
from algorithms.symbolic_regression import perform_symbolic_regression_gplearn
from algorithms.monte_carlo import MonteCarloAnalysis

# 创建蓝图
symbolic_regression_bp = Blueprint('symbolic_regression', __name__, url_prefix='/api/regression')
monte_carlo_bp = Blueprint('monte_carlo', __name__, url_prefix='/api/monte-carlo')
data_bp = Blueprint('data', __name__, url_prefix='/api/data')

@data_bp.route('/upload', methods=['POST'])
def upload_data():
    """上传数据文件"""
    try:
        logger.info("📁 开始处理数据上传请求")
        
        data = request.get_json()
        if not data or 'data' not in data:
            logger.error("❌ 数据上传失败：请求数据格式错误")
            return jsonify({'success': False, 'error': '数据格式错误：请检查上传的CSV文件'})
        
        # 验证数据
        df = pd.DataFrame(data['data'])
        logger.info(f"📊 数据验证完成，形状: {df.shape}")
        
        # 检查数据质量
        if df.empty:
            logger.error("❌ 数据上传失败：CSV文件为空")
            return jsonify({'success': False, 'error': 'CSV文件为空，请检查文件内容'})
        
        # 检查数据类型
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            logger.error("❌ 数据上传失败：数值列数量不足")
            return jsonify({'success': False, 'error': 'CSV文件至少需要2个数值列（1个目标变量，1个特征变量）'})
        
        # 检查缺失值
        missing_values = df.isnull().sum().sum()
        if missing_values > 0:
            logger.warning(f"⚠️  发现 {missing_values} 个缺失值，将自动填充为0")
            df = df.fillna(0)
        
        # 检查数据长度一致性
        if df.isnull().any().any():
            logger.error("❌ 数据上传失败：数据列长度不一致")
            return jsonify({'success': False, 'error': '数据格式错误：请检查CSV文件中的数据列长度是否一致'})
        
        logger.info(f"✅ 数据上传成功，列数: {len(df.columns)}, 行数: {len(df)}")
        
        return jsonify({
            'success': True,
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'numeric_columns': numeric_columns,
            'data': df.to_dict('records')
        })
        
    except Exception as e:
        logger.error(f"❌ 数据上传异常: {str(e)}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'数据上传失败: {str(e)}'})

@symbolic_regression_bp.route('/symbolic-regression', methods=['POST'])
def symbolic_regression():
    """符号回归分析"""
    try:
        logger.info("🔬 开始符号回归分析")
        
        data = request.get_json()
        logger.info(f"📋 接收到的参数: {list(data.keys()) if data else 'None'}")
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                logger.error(f"❌ 缺少必要参数: {field}")
                return jsonify({'success': False, 'error': f'缺少必要参数: {field}'})
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        population_size = data.get('population_size', 100)
        generations = data.get('generations', 50)
        test_ratio = data.get('test_ratio', 0.3)
        operators = data.get('operators', ['+', '-', '*', '/'])
        
        logger.info(f"🎯 目标变量: {target_column}")
        logger.info(f"📊 特征变量: {feature_columns}")
        logger.info(f"🔧 参数设置: 种群大小={population_size}, 代数={generations}, 测试比例={test_ratio}")
        
        # 数据预处理
        df = pd.DataFrame(input_data)
        logger.info(f"📊 数据形状: {df.shape}")
        
        # 检查列是否存在
        if target_column not in df.columns:
            logger.error(f"❌ 目标变量列 '{target_column}' 不存在")
            return jsonify({'success': False, 'error': f'目标变量列 "{target_column}" 不存在，请检查数据文件'})
        
        for col in feature_columns:
            if col not in df.columns:
                logger.error(f"❌ 特征变量列 '{col}' 不存在")
                return jsonify({'success': False, 'error': f'特征变量列 "{col}" 不存在，请检查数据文件'})
        
        # 提取数据
        X = df[feature_columns]
        y = df[target_column]
        
        logger.info(f"📊 特征数据形状: {X.shape}")
        logger.info(f"📊 目标数据形状: {y.shape}")
        
        # 数据质量检查
        if len(y) < 10:
            logger.error("❌ 数据样本数量太少")
            return jsonify({'success': False, 'error': '数据样本数量太少，至少需要10个样本'})
        
        if y.std() < 1e-6:
            logger.error("❌ 目标变量没有变化")
            return jsonify({'success': False, 'error': '目标变量没有变化，无法进行回归分析'})
        
        # 检查NaN值
        if X.isnull().any().any() or y.isnull().any():
            logger.error("❌ 数据包含NaN值")
            return jsonify({'success': False, 'error': '数据包含NaN值，请检查数据文件'})
        
        # 检查数据长度一致性
        if len(X) != len(y):
            logger.error("❌ 特征和目标数据长度不一致")
            return jsonify({'success': False, 'error': '数据格式错误：特征和目标数据长度不一致'})
        
        logger.info("✅ 数据验证通过，开始执行符号回归")
        
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
            logger.info(f"✅ 符号回归分析完成，R² = {result['metrics']['r2_test']:.3f}")
            return jsonify(result)
        else:
            logger.error(f"❌ 符号回归分析失败: {result['error']}")
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        logger.error(f"❌ 符号回归分析异常: {str(e)}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'符号回归分析失败: {str(e)}'})

@monte_carlo_bp.route('/analysis', methods=['POST'])
def monte_carlo_analysis():
    """蒙特卡罗分析"""
    try:
        logger.info("🎲 开始蒙特卡罗分析")
        
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                logger.error(f"❌ 缺少必要参数: {field}")
                return jsonify({'success': False, 'error': f'缺少必要参数: {field}'})
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        iterations = data.get('iterations', 1000)
        
        logger.info(f"🎯 目标变量: {target_column}")
        logger.info(f"📊 特征变量: {feature_columns}")
        logger.info(f"🔄 迭代次数: {iterations}")
        
        # 数据预处理
        df = pd.DataFrame(input_data)
        
        # 检查列是否存在
        if target_column not in df.columns:
            logger.error(f"❌ 目标变量列 '{target_column}' 不存在")
            return jsonify({'success': False, 'error': f'目标变量列 "{target_column}" 不存在'})
        
        for col in feature_columns:
            if col not in df.columns:
                logger.error(f"❌ 特征变量列 '{col}' 不存在")
                return jsonify({'success': False, 'error': f'特征变量列 "{col}" 不存在'})
        
        # 执行蒙特卡罗分析
        monte_carlo = MonteCarloAnalysis()
        result = monte_carlo.analyze(
            data=input_data,
            target_column=target_column,
            feature_columns=feature_columns,
            iterations=iterations
        )
        
        logger.info("✅ 蒙特卡罗分析完成")
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        logger.error(f"❌ 蒙特卡罗分析异常: {str(e)}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'蒙特卡罗分析失败: {str(e)}'})

@symbolic_regression_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'service': 'symbolic-regression'})

@monte_carlo_bp.route('/health', methods=['GET'])
def monte_carlo_health():
    """蒙特卡罗健康检查"""
    return jsonify({'status': 'healthy', 'service': 'monte-carlo'})

@data_bp.route('/health', methods=['GET'])
def data_health():
    """数据服务健康检查"""
    return jsonify({'status': 'healthy', 'service': 'data'}) 