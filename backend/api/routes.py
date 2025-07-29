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
symbolic_regression_bp = Blueprint('symbolic_regression', __name__)
monte_carlo_bp = Blueprint('monte_carlo', __name__)
data_bp = Blueprint('data', __name__)

# 全局实例
monte_carlo_engine = MonteCarloAnalysis()
data_loader = DataLoader()

# 健康检查端点
@symbolic_regression_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    logger.info("健康检查请求")
    return jsonify({'status': 'healthy', 'message': '后端服务运行正常'})

# 符号回归路由
@symbolic_regression_bp.route('/symbolic-regression', methods=['POST'])
def symbolic_regression():
    """符号回归分析"""
    try:
        data = request.get_json()
        logger.info(f"收到符号回归请求，数据键: {list(data.keys()) if data else 'None'}")
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                error_msg = f'缺少必要参数: {field}'
                logger.error(error_msg)
                return jsonify({'success': False, 'error': error_msg})
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        population_size = data.get('population_size', 100)
        generations = data.get('generations', 50)
        test_ratio = data.get('test_ratio', 0.3)
        operators = data.get('operators', ['+', '-', '*', '/'])
        
        logger.info(f"开始符号回归分析，目标变量: {target_column}, 特征数量: {len(feature_columns)}")
        logger.info(f"参数: 种群大小={population_size}, 代数={generations}, 测试比例={test_ratio}")
        
        # 数据预处理
        if not input_data or not isinstance(input_data, list):
            error_msg = '数据格式错误：请检查CSV文件中的数据格式'
            logger.error(error_msg)
            logger.error(f"输入数据类型: {type(input_data)}")
            logger.error(f"输入数据内容: {input_data[:2] if input_data else 'None'}")
            return jsonify({'success': False, 'error': error_msg})
        
        df = pd.DataFrame(input_data)
        logger.info(f"数据形状: {df.shape}, 列名: {list(df.columns)}")
        logger.info(f"数据样本: {df.head(2).to_dict('records')}")
        
        # 检查列是否存在
        if target_column not in df.columns:
            error_msg = f'目标变量列 "{target_column}" 不存在，可用列: {list(df.columns)}'
            logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg})
        
        for col in feature_columns:
            if col not in df.columns:
                error_msg = f'特征变量列 "{col}" 不存在，可用列: {list(df.columns)}'
                logger.error(error_msg)
                return jsonify({'success': False, 'error': error_msg})
        
        # 提取数据
        X = df[feature_columns]
        y = df[target_column]
        
        logger.info(f"特征数据形状: {X.shape}, 目标数据形状: {y.shape}")
        logger.info(f"特征列: {list(X.columns)}")
        logger.info(f"目标列: {target_column}")
        
        # 数据质量检查
        if len(y) < 10:
            error_msg = '数据样本数量太少，至少需要10个样本'
            logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg})
        
        # 检查NaN值
        if X.isnull().any().any() or y.isnull().any():
            error_msg = '数据包含NaN值，请检查CSV文件中的数据完整性'
            logger.error(error_msg)
            logger.error(f"特征数据NaN统计: {X.isnull().sum().to_dict()}")
            logger.error(f"目标数据NaN统计: {y.isnull().sum()}")
            return jsonify({'success': False, 'error': error_msg})
        
        # 检查数据长度一致性
        if len(X) != len(y):
            error_msg = '数据格式错误：请检查CSV文件中的数据列长度是否一致'
            logger.error(error_msg)
            logger.error(f"特征数据长度: {len(X)}, 目标数据长度: {len(y)}")
            return jsonify({'success': False, 'error': error_msg})
        
        if y.std() < 1e-6:
            error_msg = '目标变量没有变化，无法进行回归分析'
            logger.error(error_msg)
            logger.error(f"目标变量统计: 均值={y.mean():.6f}, 标准差={y.std():.6f}")
            return jsonify({'success': False, 'error': error_msg})
        
        logger.info(f"数据验证通过，开始执行符号回归...")
        logger.info(f"目标变量统计: 均值={y.mean():.6f}, 标准差={y.std():.6f}")
        logger.info(f"特征变量统计: 均值范围=[{X.mean().min():.6f}, {X.mean().max():.6f}], 标准差范围=[{X.std().min():.6f}, {X.std().max():.6f}]")
        
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
            logger.error(f"符号回归分析失败: {result['error']}")
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        error_msg = f"符号回归分析失败: {str(e)}"
        logger.error(error_msg)
        logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': error_msg})

# 蒙特卡罗分析路由
@monte_carlo_bp.route('/analysis', methods=['POST'])
def monte_carlo_analysis():
    """蒙特卡罗分析"""
    try:
        data = request.get_json()
        logger.info("收到蒙特卡罗分析请求")
        
        # 验证参数
        if not data or 'data' not in data:
            return jsonify({'success': False, 'error': '缺少数据参数'})
        
        # 执行分析
        result = monte_carlo_engine.analyze(data['data'])
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"蒙特卡罗分析失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 数据上传路由
@data_bp.route('/upload', methods=['POST'])
def upload_data():
    """数据上传"""
    try:
        data = request.get_json()
        logger.info("收到数据上传请求")
        
        if not data or 'data' not in data:
            return jsonify({'success': False, 'error': '缺少数据参数'})
        
        # 处理数据
        result = data_loader.load_data(data['data'])
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"数据上传失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}) 