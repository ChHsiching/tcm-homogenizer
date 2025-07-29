#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

from flask import Blueprint, request, jsonify
from loguru import logger
import traceback
import pandas as pd

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
    return jsonify({'status': 'healthy', 'message': '后端服务运行正常'})

# 符号回归路由
@symbolic_regression_bp.route('/symbolic-regression', methods=['POST'])
def symbolic_regression():
    """符号回归分析"""
    try:
        logger.info("收到符号回归分析请求")
        data = request.get_json()
        
        if not data:
            logger.error("请求数据为空")
            return jsonify({'success': False, 'error': '请求数据为空'})
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                logger.error(f"缺少必要参数: {field}")
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
        logger.info(f"参数: 种群大小={population_size}, 代数={generations}, 测试比例={test_ratio}")
        
        # 数据预处理
        try:
            df = pd.DataFrame(input_data)
            logger.info(f"数据加载成功，形状: {df.shape}")
        except Exception as e:
            logger.error(f"数据加载失败: {str(e)}")
            return jsonify({'success': False, 'error': f'数据格式错误: {str(e)}'})
        
        # 检查列是否存在
        if target_column not in df.columns:
            logger.error(f"目标变量列不存在: {target_column}")
            return jsonify({'success': False, 'error': f'目标变量列 "{target_column}" 不存在'})
        
        missing_features = [col for col in feature_columns if col not in df.columns]
        if missing_features:
            logger.error(f"特征变量列不存在: {missing_features}")
            return jsonify({'success': False, 'error': f'特征变量列不存在: {missing_features}'})
        
        # 提取数据
        X = df[feature_columns]
        y = df[target_column]
        
        # 数据质量检查
        logger.info(f"数据样本数量: {len(y)}")
        if len(y) < 10:
            logger.error("数据样本数量太少")
            return jsonify({'success': False, 'error': '数据样本数量太少，至少需要10个样本'})
        
        # 检查NaN值
        if X.isnull().any().any():
            logger.error("特征变量包含NaN值")
            return jsonify({'success': False, 'error': '特征变量包含NaN值，请检查数据质量'})
        
        if y.isnull().any():
            logger.error("目标变量包含NaN值")
            return jsonify({'success': False, 'error': '目标变量包含NaN值，请检查数据质量'})
        
        # 检查数据长度一致性
        if len(X) != len(y):
            logger.error("特征变量和目标变量长度不一致")
            return jsonify({'success': False, 'error': '特征变量和目标变量长度不一致'})
        
        # 检查目标变量变化
        y_std = y.std()
        logger.info(f"目标变量标准差: {y_std}")
        if y_std < 1e-6:
            logger.error("目标变量没有变化")
            return jsonify({'success': False, 'error': '目标变量没有变化，无法进行回归分析'})
        
        # 执行符号回归（使用新的HeuristicLab算法）
        try:
            from algorithms.symbolic_regression import perform_symbolic_regression_gplearn
            
            logger.info("开始执行符号回归算法...")
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
            logger.error(f"符号回归算法执行失败: {str(e)}")
            logger.error(f"详细错误: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'符号回归分析失败: {str(e)}'})
            
    except Exception as e:
        logger.error(f"符号回归分析请求处理失败: {str(e)}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'请求处理失败: {str(e)}'})

@symbolic_regression_bp.route('/models', methods=['GET'])
def get_models():
    """获取已保存的模型列表"""
    try:
        # The original code had symbolic_regression_engine.get_saved_models()
        # but symbolic_regression_engine was removed.
        # Assuming this functionality is no longer available or needs to be re-evaluated.
        # For now, returning an empty list or a placeholder message.
        return jsonify({
            'success': True,
            'models': [] # Placeholder, as symbolic_regression_engine is removed
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
        # The original code had symbolic_regression_engine.get_model(model_id)
        # but symbolic_regression_engine was removed.
        # Assuming this functionality is no longer available or needs to be re-evaluated.
        # For now, returning a placeholder message.
        return jsonify({
            'error': '模型详情获取失败',
            'message': '符号回归模型功能已移除'
        }), 501 # 501 Not Implemented
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