#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义 - 模拟数据版本
"""

from flask import Blueprint, request, jsonify, send_file
from loguru import logger
import traceback
import time
import random
import json
import os
import numpy as np
from datetime import datetime
import io
import zipfile
from werkzeug.utils import secure_filename
import shutil

# 创建蓝图
symbolic_regression_bp = Blueprint('symbolic_regression', __name__)
monte_carlo_bp = Blueprint('monte_carlo', __name__)
data_bp = Blueprint('data', __name__)
data_models_bp = Blueprint('data_models', __name__)

# 数据模型存储路径
DATA_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_models')
CSV_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'csv_data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

os.makedirs(DATA_MODELS_DIR, exist_ok=True)
os.makedirs(CSV_DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_data_models():
    """加载所有数据模型"""
    models = []
    if os.path.exists(DATA_MODELS_DIR):
        for filename in os.listdir(DATA_MODELS_DIR):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(DATA_MODELS_DIR, filename), 'r', encoding='utf-8') as f:
                        model = json.load(f)
                        # 检查文件存在性
                        model['metadata'] = model.get('metadata', {})
                        csv_name = model.get('data_files', {}).get('csv_data')
                        reg_name = model.get('data_files', {}).get('regression_model')
                        mc_name = model.get('data_files', {}).get('monte_carlo_results')
                        model['metadata']['has_csv_data'] = bool(csv_name) and os.path.exists(os.path.join(CSV_DATA_DIR, csv_name))
                        model['metadata']['has_regression_model'] = bool(reg_name) and os.path.exists(os.path.join(MODELS_DIR, reg_name))
                        model['metadata']['has_monte_carlo_results'] = bool(mc_name) and os.path.exists(os.path.join(RESULTS_DIR, mc_name))
                        models.append(model)
                except Exception as e:
                    logger.error(f"加载数据模型文件 {filename} 失败: {e}")
    return models

def save_data_model(model):
    """保存数据模型"""
    try:
        model_id = model['id']
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据模型已保存: {filename}")
        return True
    except Exception as e:
        logger.error(f"保存数据模型失败: {e}")
        return False

def create_data_model_files(model_id, csv_data=None, regression_model=None, monte_carlo_results=None):
    """创建数据模型相关的文件"""
    try:
        # 创建CSV数据文件
        if csv_data:
            csv_filename = f"{model_id}_data.csv"
            csv_filepath = os.path.join(CSV_DATA_DIR, csv_filename)
            with open(csv_filepath, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            logger.info(f"CSV数据文件已创建: {csv_filename}")
        
        # 创建符号回归模型文件
        if regression_model:
            model_filename = f"{model_id}_regression.json"
            model_filepath = os.path.join(MODELS_DIR, model_filename)
            with open(model_filepath, 'w', encoding='utf-8') as f:
                json.dump(regression_model, f, ensure_ascii=False, indent=2)
            logger.info(f"符号回归模型文件已创建: {model_filename}")
        
        # 创建蒙特卡洛分析结果文件
        if monte_carlo_results:
            results_filename = f"{model_id}_monte_carlo.txt"
            results_filepath = os.path.join(RESULTS_DIR, results_filename)
            with open(results_filepath, 'w', encoding='utf-8') as f:
                f.write(monte_carlo_results)
            logger.info(f"蒙特卡洛分析结果文件已创建: {results_filename}")
        
        return True
    except Exception as e:
        logger.error(f"创建数据模型文件失败: {e}")
        return False

def delete_data_model(model_id):
    """删除数据模型及其相关文件"""
    try:
        # 删除主模型文件
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if os.path.exists(filepath):
            # 读取模型信息以获取相关文件
            with open(filepath, 'r', encoding='utf-8') as f:
                model = json.load(f)
            
            # 删除相关文件
            data_files = model.get('data_files', {})
            
            # 删除CSV数据文件
            if 'csv_data' in data_files:
                csv_filepath = os.path.join(CSV_DATA_DIR, data_files['csv_data'])
                if os.path.exists(csv_filepath):
                    os.remove(csv_filepath)
                    logger.info(f"CSV数据文件已删除: {data_files['csv_data']}")
            
            # 删除符号回归模型文件
            if 'regression_model' in data_files:
                model_filepath = os.path.join(MODELS_DIR, data_files['regression_model'])
                if os.path.exists(model_filepath):
                    os.remove(model_filepath)
                    logger.info(f"符号回归模型文件已删除: {data_files['regression_model']}")
            
            # 删除蒙特卡洛分析结果文件
            if 'monte_carlo_results' in data_files:
                results_filepath = os.path.join(RESULTS_DIR, data_files['monte_carlo_results'])
                if os.path.exists(results_filepath):
                    os.remove(results_filepath)
                    logger.info(f"蒙特卡洛分析结果文件已删除: {data_files['monte_carlo_results']}")
            
            # 删除主模型文件
            os.remove(filepath)
            logger.info(f"数据模型已删除: {filename}")
            return True
        else:
            logger.warning(f"数据模型文件不存在: {filename}")
            return False
    except Exception as e:
        logger.error(f"删除数据模型失败: {e}")
        return False

# 数据模型管理路由
@data_models_bp.route('/models', methods=['GET'])
def get_data_models():
    """获取所有数据模型列表"""
    try:
        models = load_data_models()
        
        # 按创建时间排序，最新的在前
        models.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        logger.error(f"获取数据模型列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取数据模型列表失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>', methods=['GET'])
def get_data_model(model_id):
    """获取特定数据模型详情"""
    try:
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '数据模型不存在'
            }), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            model = json.load(f)
        
        return jsonify({
            'success': True,
            'model': model
        })
    except Exception as e:
        logger.error(f"获取数据模型详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取数据模型详情失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>/files/<file_type>', methods=['GET'])
def get_data_model_file(model_id, file_type):
    """获取数据模型相关文件内容"""
    try:
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '数据模型不存在'
            }), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            model = json.load(f)
        
        data_files = model.get('data_files', {})
        
        if file_type not in ['csv_data', 'regression_model', 'monte_carlo_results', 'all_as_zip']:
            return jsonify({
                'success': False,
                'error': '不支持的文件类型'
            }), 400
        
        # 打包为 zip：包含 data_model.json、data.csv、regression.json、monte_carlo.json（若存在），统一置于 model_id/ 目录内
        if file_type == 'all_as_zip':
            in_memory = io.BytesIO()
            with zipfile.ZipFile(in_memory, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                base_dir = f"{model_id}/"
                # 写入 data_model.json（规范化）
                zf.writestr(base_dir + 'data_model.json', json.dumps(model, ensure_ascii=False, indent=2))
                # CSV → data.csv（若无则跳过）
                csv_name = data_files.get('csv_data')
                if csv_name:
                    csv_path = os.path.join(CSV_DATA_DIR, csv_name)
                    if os.path.exists(csv_path):
                        with open(csv_path, 'rb') as f:
                            zf.writestr(base_dir + 'data.csv', f.read())
                # 回归模型 JSON → regression.json（若无则跳过）
                reg_name = data_files.get('regression_model')
                if reg_name:
                    reg_path = os.path.join(MODELS_DIR, reg_name)
                    if os.path.exists(reg_path):
                        with open(reg_path, 'r', encoding='utf-8') as f:
                            zf.writestr(base_dir + 'regression.json', f.read())
                # 蒙特卡洛 JSON（可选） → monte_carlo.json
                mc_name = data_files.get('monte_carlo_results')
                if mc_name:
                    mc_path = os.path.join(RESULTS_DIR, mc_name)
                    if os.path.exists(mc_path):
                        with open(mc_path, 'r', encoding='utf-8') as f:
                            zf.writestr(base_dir + 'monte_carlo.json', f.read())

            in_memory.seek(0)
            zip_filename = f"{model_id}.zip"
            return send_file(
                in_memory,
                as_attachment=True,
                download_name=zip_filename,
                mimetype='application/zip'
            )

        # 单文件读取
        file_filename = data_files.get(file_type)
        if not file_filename:
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        if file_type == 'csv_data':
            file_path = os.path.join(CSV_DATA_DIR, file_filename)
        elif file_type == 'regression_model':
            file_path = os.path.join(MODELS_DIR, file_filename)
        elif file_type == 'monte_carlo_results':
            file_path = os.path.join(RESULTS_DIR, file_filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        # 直接返回文件内容（文本）
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({'success': True, 'content': content, 'filename': file_filename, 'file_type': file_type})
        
    except Exception as e:
        logger.error(f"获取数据模型文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取数据模型文件失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>', methods=['DELETE'])
def delete_data_model_api(model_id):
    """删除数据模型"""
    try:
        if delete_data_model(model_id):
            return jsonify({
                'success': True,
                'message': '数据模型删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据模型删除失败'
            }), 500
    except Exception as e:
        logger.error(f"删除数据模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除数据模型失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/clear', methods=['POST'])
def clear_all_models():
    """清空所有数据模型及其关联文件（CSV/回归/蒙特卡洛）。"""
    try:
        # 安全起见，仅清空子目录文件，不删除目录本身
        for folder in [DATA_MODELS_DIR, CSV_DATA_DIR, MODELS_DIR, RESULTS_DIR]:
            if os.path.exists(folder):
                for name in os.listdir(folder):
                    file_path = os.path.join(folder, name)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        logger.warning(f"清理 {file_path} 失败: {e}")
        return jsonify({'success': True, 'message': '所有数据已清空'})
    except Exception as e:
        logger.error(f"清空数据失败: {e}")
        return jsonify({'success': False, 'error': '清空数据失败', 'message': str(e)}), 500

@data_models_bp.route('/import', methods=['POST'])
def import_models_zip():
    """导入一个包含一个或多个模型目录的ZIP包。支持单模型或多模型ZIP。
    规范结构：每个模型一个目录 model_xxx/，内含 data_model.json、data.csv、regression.json、monte_carlo.json(可选)。
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '缺少文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400
        # 读取为内存Zip
        file_bytes = file.read()
        in_mem = io.BytesIO(file_bytes)
        def process_zip(zfile: zipfile.ZipFile) -> int:
            names = zfile.namelist()
            top_dirs = set([n.split('/')[0] for n in names if '/' in n]) or set()
            if not top_dirs:
                top_dirs = {''}
            count = 0
            for root in top_dirs:
                base = (root + '/') if root else ''
                try:
                    dm_path = base + 'data_model.json'
                    if dm_path not in names:
                        legacy_jsons = [n for n in names if n.startswith(base) and n.endswith('.json') and '/data_models/' not in n]
                        if legacy_jsons:
                            dm_path = legacy_jsons[0]
                        else:
                            continue
                    model_obj = json.loads(zfile.read(dm_path).decode('utf-8'))
                    model_id = model_obj.get('id') or f"model_{int(time.time())}"
                    csv_filename = f"{model_id}_data.csv"
                    reg_filename = f"{model_id}_regression.json"
                    # CSV
                    has_csv = False
                    data_csv_path_in_zip = base + 'data.csv'
                    if data_csv_path_in_zip in names:
                        with open(os.path.join(CSV_DATA_DIR, csv_filename), 'wb') as f:
                            f.write(zfile.read(data_csv_path_in_zip))
                        has_csv = True
                    # 回归
                    has_reg = False
                    reg_json_path_in_zip = base + 'regression.json'
                    if reg_json_path_in_zip in names:
                        with open(os.path.join(MODELS_DIR, reg_filename), 'w', encoding='utf-8') as f:
                            f.write(zfile.read(reg_json_path_in_zip).decode('utf-8'))
                        has_reg = True
                    # 蒙特卡洛
                    has_mc = False
                    mc_json_path_in_zip = base + 'monte_carlo.json'
                    if mc_json_path_in_zip in names:
                        mc_filename = f"{model_id}_monte_carlo.json"
                        with open(os.path.join(RESULTS_DIR, mc_filename), 'w', encoding='utf-8') as f:
                            f.write(zfile.read(mc_json_path_in_zip).decode('utf-8'))
                        has_mc = True
                    # 保存模型文件
                    model_obj['id'] = model_id
                    model_obj['data_files'] = {
                        'csv_data': csv_filename if has_csv else None,
                        'regression_model': reg_filename if has_reg else None,
                        'monte_carlo_results': (f"{model_id}_monte_carlo.json" if has_mc else None)
                    }
                    model_obj['metadata'] = model_obj.get('metadata', {})
                    model_obj['metadata']['has_csv_data'] = has_csv
                    model_obj['metadata']['has_regression_model'] = has_reg
                    model_obj['metadata']['has_monte_carlo_results'] = has_mc
                    model_obj['created_at'] = model_obj.get('created_at') or time.time()
                    model_obj['updated_at'] = time.time()
                    save_data_model(model_obj)
                    count += 1
                except Exception as ex:
                    logger.warning(f"导入模型 {root or 'root'} 失败: {ex}")
            return count

        with zipfile.ZipFile(in_mem, 'r') as zf:
            imported = process_zip(zf)
            if imported == 0:
                # 兼容“总ZIP内嵌子ZIP”的情况
                for n in zf.namelist():
                    if n.lower().endswith('.zip'):
                        try:
                            sub_bytes = io.BytesIO(zf.read(n))
                            with zipfile.ZipFile(sub_bytes, 'r') as subzf:
                                imported += process_zip(subzf)
                        except Exception as sube:
                            logger.warning(f"解析子ZIP {n} 失败: {sube}")
        return jsonify({'success': True, 'count': imported})
    except Exception as e:
        logger.error(f"导入数据包失败: {e}")
        return jsonify({'success': False, 'error': '导入失败', 'message': str(e)}), 500

@data_models_bp.route('/models', methods=['POST'])
def create_data_model():
    """创建新的数据模型"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['name', 'description', 'data_source', 'analysis_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': '参数缺失',
                    'message': f'缺少必要参数: {field}'
                }), 400
        
        # 生成模型ID
        model_id = f"model_{int(time.time())}"
        
        # 创建数据模型
        model = {
            'id': model_id,
            'name': data['name'],
            'description': data['description'],
            'data_source': data['data_source'],
            'analysis_type': data['analysis_type'],
            'created_at': time.time(),
            'created_by': data.get('created_by', 'unknown'),
            'status': 'active',
            'symbolic_regression': data.get('symbolic_regression'),
            'monte_carlo': data.get('monte_carlo'),
            'metadata': data.get('metadata', {})
        }
        
        # 保存模型
        if save_data_model(model):
            return jsonify({
                'success': True,
                'model': model,
                'message': '数据模型创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据模型保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"创建数据模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '创建数据模型失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>', methods=['PUT'])
def update_data_model(model_id):
    """更新数据模型"""
    try:
        data = request.get_json()
        
        # 检查模型是否存在
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '数据模型不存在'
            }), 404
        
        # 加载现有模型
        with open(filepath, 'r', encoding='utf-8') as f:
            model = json.load(f)
        
        # 更新模型数据
        allowed_fields = ['name', 'description', 'status', 'symbolic_regression', 'monte_carlo', 'metadata']
        for field in allowed_fields:
            if field in data:
                model[field] = data[field]
        
        model['updated_at'] = time.time()
        
        # 保存更新后的模型
        if save_data_model(model):
            return jsonify({
                'success': True,
                'model': model,
                'message': '数据模型更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据模型保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"更新数据模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新数据模型失败',
            'message': str(e)
        }), 500

# 符号回归路由
@symbolic_regression_bp.route('/analyze', methods=['POST'])
def analyze():
    """符号回归分析 - 模拟数据"""
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
        max_tree_depth = data.get('max_tree_depth', 35)
        max_tree_length = data.get('max_tree_length', 35)
        symbolic_expression_grammar = data.get('symbolic_expression_grammar', ['addition', 'subtraction', 'multiplication', 'division'])
        train_ratio = data.get('train_ratio', 80)
        set_seed_randomly = data.get('set_seed_randomly', False)
        seed_value = int(data.get('seed', 42))
        data_source = data.get('data_source', '数据源')
        
        logger.info(f"开始符号回归分析，目标变量: {target_column}")
        logger.info(f"特征变量: {feature_columns}")
        logger.info(f"输入数据行数: {len(input_data)}")
        logger.info(f"输入数据类型: {type(input_data)}")
        logger.info(f"输入数据内容: {input_data}")
        
        # 模拟处理时间
        time.sleep(2)
        
        # 根据随机种子参数设置随机数生成
        if not set_seed_randomly:
            # 固定模式：使用用户提供或默认的固定种子
            random.seed(seed_value)
            np.random.seed(seed_value)
            logger.info(f"使用固定随机种子: {seed_value}")
        else:
            # 随机模式：前端会下发随机生成的seed，这里也记录并使用该seed
            random.seed(seed_value)
            np.random.seed(seed_value)
            logger.info(f"使用随机种子（每次随机生成）: {seed_value}")
        
        # 生成模拟结果
        model_id = int(time.time())
        expression_parts = []
        for i, feature in enumerate(feature_columns[:min(3, len(feature_columns))]):  # 最多使用3个特征
            coefficient = round(0.5 - i * 0.1, 2)
            expression_parts.append(f"{feature} * {coefficient}")
        
        expression = " + ".join(expression_parts) + " + 0.1"
        
        # 生成特征重要性
        feature_importance = []
        for i, feature in enumerate(feature_columns):
            importance = max(0.1, 0.8 - i * 0.2)
            feature_importance.append({
                "feature": feature,
                "importance": round(importance, 3)
            })
        
        # 生成预测结果
        predictions = []
        for i, row in enumerate(input_data):  # 处理所有数据行
            actual = float(row.get(target_column, 0)) or random.uniform(1.5, 3.0)
            predicted = actual + random.uniform(-0.3, 0.3)
            predictions.append({
                "actual": round(actual, 3),
                "predicted": round(predicted, 3)
            })
        
        # 生成常数 - 只生成公式中实际需要的常数
        constants = {}
        # 根据表达式中的数字数量生成对应数量的常数
        # 这里我们只生成4个常数，对应表达式中的4个数字
        for i in range(4):  # 只生成c0到c3的常数
            constants[f'c_{i}'] = round(random.uniform(-10, 10), 4)
        
        # 生成详细的性能指标
        detailed_metrics = {
            "average_relative_error_test": round(random.uniform(8.0, 18.0), 2),
            "average_relative_error_training": round(random.uniform(7.0, 16.0), 2),
            "mean_absolute_error_test": round(random.uniform(0.15, 0.45), 3),
            "mean_absolute_error_training": round(random.uniform(0.12, 0.40), 3),
            "mean_squared_error_test": round(random.uniform(0.08, 0.25), 3),
            "mean_squared_error_training": round(random.uniform(0.06, 0.20), 3),
            "model_depth": random.randint(4, 12),
            "model_length": random.randint(15, 35),
            "normalized_mean_squared_error_test": round(random.uniform(0.06, 0.20), 3),
            "normalized_mean_squared_error_training": round(random.uniform(0.05, 0.18), 3),
            "pearson_r_test": round(random.uniform(0.85, 0.98), 3),
            "pearson_r_training": round(random.uniform(0.86, 0.99), 3),
            "root_mean_squared_error_test": round(random.uniform(0.25, 0.55), 3),
            "root_mean_squared_error_training": round(random.uniform(0.22, 0.50), 3)
        }
        
        result = {
            "id": model_id,
            "expression": expression,
            "target_variable": target_column,
            "constants": constants,
            "r2": round(random.uniform(0.7, 0.95), 3),
            "mse": round(random.uniform(0.05, 0.25), 3),
            "feature_importance": feature_importance,
            "predictions": predictions,
            "training_time": round(random.uniform(3.0, 8.0), 1),
            "model_complexity": len(feature_columns[:min(3, len(feature_columns))]),
            "detailed_metrics": detailed_metrics,
            "analysis_params": {
                "population_size": population_size,
                "generations": generations,
                "max_tree_depth": max_tree_depth,
                "max_tree_length": max_tree_length,
                "symbolic_expression_grammar": symbolic_expression_grammar,
                "train_ratio": train_ratio,
                "set_seed_randomly": set_seed_randomly,
                "seed": seed_value,
                "seed_mode": "随机" if set_seed_randomly else "固定"
            }
        }
        
        # 自动创建数据模型
        try:
            # 生成模型ID
            model_id = f"model_{int(time.time())}"
            
            # 确定CSV文件：优先使用上传时保存的原始CSV文件
            server_csv_filename = data.get('server_csv_filename')
            csv_data = None
            if server_csv_filename:
                # 直接引用现有CSV文件，不再重构
                csv_source_path = os.path.join(CSV_DATA_DIR, server_csv_filename)
                if os.path.exists(csv_source_path):
                    # 复制为本模型专属文件名，便于打包
                    csv_filename = f"{model_id}_data.csv"
                    csv_target_path = os.path.join(CSV_DATA_DIR, csv_filename)
                    try:
                        with open(csv_source_path, 'r', encoding='utf-8') as src, open(csv_target_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                        csv_data = None  # 标记已使用文件复制
                        logger.info(f"已复制原始CSV到: {csv_filename}")
                    except Exception as e:
                        logger.error(f"复制原始CSV失败，退回到重构: {e}")
                        csv_data = _prepare_csv_data(input_data, target_column, feature_columns)
                else:
                    logger.warning("提供的 server_csv_filename 不存在，退回到重构CSV")
                    csv_data = _prepare_csv_data(input_data, target_column, feature_columns)
            else:
                # 后备：根据内存数据重构CSV
                csv_data = _prepare_csv_data(input_data, target_column, feature_columns)
            
            # 准备符号回归模型数据
            regression_model = {
                'id': model_id,
                'expression': expression,
                'target_variable': target_column,
                'constants': constants,
                'r2': result['r2'],
                'mse': result['mse'],
                'feature_importance': result['feature_importance'],
                'predictions': result['predictions'],
                'training_time': result['training_time'],
                'model_complexity': result['model_complexity'],
                'detailed_metrics': result['detailed_metrics'],
                'target_column': target_column,
                'feature_columns': feature_columns,
                'analysis_params': {
                    'population_size': population_size,
                    'generations': generations,
                    'max_tree_depth': max_tree_depth,
                    'max_tree_length': max_tree_length,
                    'symbolic_expression_grammar': symbolic_expression_grammar,
                    'train_ratio': train_ratio,
                    'set_seed_randomly': set_seed_randomly,
                    'seed': seed_value,
                    'seed_mode': '随机' if set_seed_randomly else '固定'
                },
                'created_at': time.time()
            }
            
            # 生成有区分度的模型名称
            model_name = _generate_model_name(target_column, feature_columns, data_source, "符号回归", model_id)
            
            # 生成详细的模型描述
            feature_count = len(feature_columns)
            feature_list = "、".join(feature_columns[:3])
            if feature_count > 3:
                feature_list += f"等{feature_count}个"
            
            model_description = f"基于{data_source}数据，使用{feature_list}成分预测{target_column}的符号回归模型"
            
            # 创建数据模型
            data_model = {
                'id': model_id,
                'name': model_name,
                'description': model_description,
                'analysis_type': '符号回归',
                'target_column': target_column,
                'feature_columns': feature_columns,
                'data_source': data_source,
                'created_at': time.time(),
                'updated_at': time.time(),
                'status': 'active',
                'analysis_params': {
                    'population_size': population_size,
                    'generations': generations,
                    'max_tree_depth': max_tree_depth,
                    'max_tree_length': max_tree_length,
                    'symbolic_expression_grammar': symbolic_expression_grammar,
                    'train_ratio': train_ratio,
                    'set_seed_randomly': set_seed_randomly,
                    'seed': seed_value,
                    'seed_mode': '随机' if set_seed_randomly else '固定'
                },
                'data_files': {
                    'csv_data': f"{model_id}_data.csv",
                    'regression_model': f"{model_id}_regression.json"
                    # 'monte_carlo_results' 将在蒙特卡洛结果生成时填充
                },
                'metadata': {
                    'data_rows': len(input_data),
                    'has_csv_data': True,
                    'has_regression_model': True,
                    'has_monte_carlo_results': False,
                    'feature_count': feature_count,
                    'model_complexity': result['model_complexity'],
                    'r2_score': result['r2'],
                    'mse_score': result['mse']
                }
            }
            
            # 创建相关文件
            if create_data_model_files(model_id, csv_data, regression_model, None):
                # 保存数据模型
                if save_data_model(data_model):
                    logger.info(f"数据模型创建成功: {model_id}")
                    result['data_model_id'] = model_id
                else:
                    logger.warning("数据模型保存失败")
            else:
                logger.warning("数据模型文件创建失败")
                
        except Exception as e:
            logger.error(f"创建数据模型失败: {e}")
        
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
            'message': str(e),
            'details': traceback.format_exc()
        }), 500

def _generate_model_name(target_column, feature_columns, data_source=None, analysis_type="符号回归", model_id=None):
    """生成有区分度的模型名称"""
    try:
        from datetime import datetime
        
        # 获取当前时间
        now = datetime.now()
        time_str = now.strftime("%m%d_%H%M")
        
        # 生成数据源标识
        if data_source:
            source_identifier = data_source.replace('.csv', '').replace('.xlsx', '').replace('.xls', '')
        else:
            source_identifier = "数据"
        
        # 生成特征变量摘要
        if len(feature_columns) <= 3:
            features_summary = "_".join(feature_columns)
        else:
            features_summary = f"{feature_columns[0]}_{feature_columns[1]}_{feature_columns[2]}+{len(feature_columns)-3}个"
        
        # 生成模型名称 - 使用更友好的格式
        if model_id:
            # 使用模型ID和可读描述
            model_name = f"{target_column}分析模型_{model_id}"
        else:
            # 备用格式
            model_name = f"{analysis_type}_{target_column}_{features_summary}_{source_identifier}_{time_str}"
        
        return model_name
        
    except Exception as e:
        logger.error(f"生成模型名称失败: {e}")
        # 备用名称
        return f"{analysis_type}_{target_column}_{int(time.time())}"

def _prepare_csv_data(data, target_column, feature_columns):
    """准备CSV数据字符串"""
    try:
        # 构建CSV头部
        headers = feature_columns + [target_column]
        csv_lines = [','.join(headers)]
        
        # 添加数据行
        for row in data:
            row_values = []
            for col in headers:
                value = row.get(col, 0)
                row_values.append(str(value))
            csv_lines.append(','.join(row_values))
        
        return '\n'.join(csv_lines)
    except Exception as e:
        logger.error(f"准备CSV数据失败: {e}")
        return ""

def _generate_monte_carlo_report(result, target_efficacy, iterations):
    """生成蒙特卡洛分析报告文本"""
    try:
        from datetime import datetime
        
        # 生成推荐配比方案
        recommendations = []
        components = ["QA", "NCGA", "CGA", "CCGA", "CA"]
        
        for i in range(10):
            # 生成随机配比
            ratios = []
            for j, component in enumerate(components):
                ratio = round(random.uniform(0.1, 0.4), 1)
                ratios.append(f"{component} {ratio}")
            
            # 计算预期药效（基于目标药效的随机偏差）
            expected_efficacy = target_efficacy + random.uniform(-0.5, 0.5)
            expected_efficacy = round(expected_efficacy, 1)
            
            recommendations.append({
                'ratios': ratios,
                'efficacy': expected_efficacy
            })
        
        # 按药效排序
        recommendations.sort(key=lambda x: x['efficacy'], reverse=True)
        
        # 生成报告文本
        report_lines = [
            "=" * 60,
            "中药成分配比推荐方案",
            "=" * 60,
            "",
            f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"目标药效: {target_efficacy}",
            f"采样次数: {iterations:,}",
            f"有效样本: {result['valid_samples']:,}",
            f"成功率: {result['success_rate']*100:.1f}%",
            "",
            "推荐配比方案 (按药效排序):",
            "-" * 60
        ]
        
        for i, rec in enumerate(recommendations, 1):
            ratios_str = ", ".join(rec['ratios'])
            report_lines.append(f"推荐方案 {i}: {ratios_str}, 预期药效: {rec['efficacy']}")
        
        report_lines.extend([
            "",
            "=" * 60,
            "说明: 以上推荐方案基于蒙特卡洛采样分析生成，",
            "成分含量单位为相对比例，药效单位为预期目标值。",
            "=" * 60
        ])
        
        return '\n'.join(report_lines)
        
    except Exception as e:
        logger.error(f"生成蒙特卡洛报告失败: {e}")
        return f"报告生成失败: {str(e)}"

@symbolic_regression_bp.route('/models', methods=['GET'])
def get_models():
    """获取已保存的模型列表 - 模拟数据"""
    try:
        # 生成模拟模型列表
        models = []
        for i in range(3):
            model_id = int(time.time()) - i * 3600  # 每小时一个模型
            models.append({
                "id": model_id,
                "expression": f"QA * {0.4 + i*0.1:.1f} + NCGA * {0.2 + i*0.05:.2f} + 0.1",
                "r2": round(0.75 + i * 0.05, 3),
                "created_at": datetime.now().isoformat()
            })
        
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
    """获取特定模型详情 - 模拟数据"""
    try:
        # 生成模拟模型详情
        model = {
            "id": int(model_id),
            "expression": "QA * 0.5 + NCGA * 0.3 + 0.1",
            "r2": 0.85,
            "mse": 0.12,
            "feature_importance": [
                {"feature": "QA", "importance": 0.8},
                {"feature": "NCGA", "importance": 0.6},
                {"feature": "CGA", "importance": 0.4}
            ],
            "predictions": [
                {"actual": 2.1, "predicted": 2.05},
                {"actual": 2.3, "predicted": 2.28}
            ],
            "created_at": datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'model': model
        })
    except Exception as e:
        logger.error(f"获取模型详情失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

# 蒙特卡洛采样分析路由
@monte_carlo_bp.route('/analyze', methods=['POST'])
def monte_carlo_analyze():
    """蒙特卡洛采样配比分析 - 模拟数据"""
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
        
        logger.info(f"开始蒙特卡洛采样分析，模型ID: {model_id}")
        logger.info(f"目标药效: {target_efficacy}, 采样次数: {iterations}")
        
        # 模拟处理时间
        time.sleep(3)
        
        # 生成模拟结果
        analysis_id = f"mc_{int(time.time())}"
        valid_samples = int(iterations * random.uniform(0.1, 0.2))
        
        # 读取模型信息以获取目标名与特征
        target_name = "药效"
        features = ["QA", "NCGA", "CGA", "CCGA", "CA"]
        # 如果指定了数据模型，加载其特征
        try:
            filename = f"{model_id}.json"
            filepath = os.path.join(DATA_MODELS_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_model = json.load(f)
                target_name = existing_model.get('target_column', target_name)
                features = existing_model.get('feature_columns', features) or features
        except Exception as _e:
            pass

        # 生成Top10最优样本（仅模拟）
        req_ranges = data.get('component_ranges', {}) or {}
        def sample_value(var):
            vr = req_ranges.get(var) or {}
            vmin = float(vr.get('min', 0) if vr.get('min') is not None else 0)
            vmax = vr.get('max', None)
            if vmax is None:
                # 无穷大用一个较大的上界模拟
                vmax = vmin + 1.0
            return round(random.uniform(vmin, vmax), 2)

        top10 = []
        for i in range(10):
            comps = []
            for var in features[:min(8, len(features))]:
                comps.append({"name": var, "value": sample_value(var)})
            # 让前几条更接近目标
            eff = round(target_efficacy + random.uniform(-0.1, 0.1) - i*0.02, 3)
            top10.append({"rank": i+1, "efficacy": eff, "components": comps})
        
        result = {
            "analysis_id": analysis_id,
            "iterations": iterations,
            "target_efficacy": target_efficacy,
            "tolerance": tolerance,
            "valid_samples": valid_samples,
            "success_rate": round(valid_samples / iterations, 3),
            "analysis_time": round(random.uniform(5.0, 12.0), 1),
            "top10": top10,
            "component_ranges": req_ranges,
            "target_name": target_name
        }
        
        # 自动创建或更新数据模型
        try:
            # 检查是否已有对应的数据模型
            model_id = data.get('model_id')
            if model_id:
                # 尝试更新现有模型
                filename = f"{model_id}.json"
                filepath = os.path.join(DATA_MODELS_DIR, filename)
                
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_model = json.load(f)
                    
                    # 保存蒙特卡洛分析结果为 JSON 文件
                    results_filename = f"{model_id}_monte_carlo.json"
                    results_filepath = os.path.join(RESULTS_DIR, results_filename)
                    with open(results_filepath, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    # 更新模型元数据
                    existing_model['updated_at'] = time.time()
                    existing_model['metadata']['has_monte_carlo_results'] = True
                    # 更新数据文件映射
                    existing_model.setdefault('data_files', {})['monte_carlo_results'] = results_filename
                    
                    if save_data_model(existing_model):
                        logger.info(f"数据模型更新成功: {model_id}")
                        result['data_model_id'] = model_id
                    else:
                        logger.warning("数据模型更新失败")
                else:
                    logger.warning(f"指定的数据模型不存在: {model_id}")
                    return jsonify({
                        'success': False,
                        'error': '指定的数据模型不存在',
                        'message': f'模型ID {model_id} 不存在'
                    }), 404
            else:
                logger.warning("未指定数据模型ID")
                return jsonify({
                    'success': False,
                    'error': '缺少数据模型ID',
                    'message': '进行蒙特卡洛采样时必须指定一个现有的数据模型'
                }), 400
                    
        except Exception as e:
            logger.error(f"更新数据模型失败: {e}")
        
        logger.info("蒙特卡洛采样分析完成")
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"蒙特卡洛采样分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '分析失败',
            'message': str(e)
        }), 500

@monte_carlo_bp.route('/results/<analysis_id>', methods=['GET'])
def get_monte_carlo_result(analysis_id):
    """获取蒙特卡洛采样分析结果 - 模拟数据"""
    try:
        # 生成模拟结果
        result = {
            "analysis_id": analysis_id,
            "iterations": 10000,
            "target_efficacy": 2.5,
            "valid_samples": 1500,
            "optimal_ranges": [
                {
                    "component": "QA",
                    "min": 0.2,
                    "max": 0.4,
                    "mean": 0.3,
                    "std": 0.05
                },
                {
                    "component": "NCGA",
                    "min": 0.1,
                    "max": 0.3,
                    "mean": 0.2,
                    "std": 0.04
                }
            ],
            "distribution": [random.uniform(0.1, 2.0) for _ in range(100)],
            "created_at": datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"获取蒙特卡洛结果失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

# 数据处理路由
@data_bp.route('/upload', methods=['POST'])
def upload_data():
    """上传数据文件 - 真实实现"""
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
        
        # 检查文件扩展名
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'error': '文件格式错误',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 读取文件内容
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        if len(lines) < 2:
            return jsonify({
                'error': '文件格式错误',
                'message': 'CSV文件至少需要包含表头和数据行'
            }), 400
        
        # 解析CSV行，处理引号内的逗号
        def parse_csv_line(line):
            result = []
            current = ''
            in_quotes = False
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    result.append(current)
                    current = ''
                else:
                    current += char
            
            result.append(current)
            return result
        
        # 解析表头
        headers = [h.strip() for h in parse_csv_line(lines[0])]
        # 移除列名中的多余空格
        headers = [h.strip() for h in headers]
        if len(headers) == 0:
            return jsonify({
                'error': '文件格式错误',
                'message': 'CSV文件没有有效的表头'
            }), 400
        
        # 解析数据行
        data = []
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if line == '':
                continue
            
            values = parse_csv_line(line)
            row = {}
            
            for j, header in enumerate(headers):
                value = values[j].strip() if j < len(values) else ''
                # 尝试转换为数字
                try:
                    row[header] = float(value) if value else 0.0
                except ValueError:
                    row[header] = value
            
            data.append(row)
        
        # 生成预览数据（前10行）
        preview_data = data[:10] if len(data) > 10 else data
        
        # 保存原始CSV文件到服务器（保持原样）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = secure_filename(file.filename)
        server_csv_filename = f"upload_{timestamp}_{safe_name}"
        server_csv_path = os.path.join(CSV_DATA_DIR, server_csv_filename)
        try:
            with open(server_csv_path, 'w', encoding='utf-8', newline='') as out:
                out.write(content)
        except Exception as e:
            logger.error(f"保存原始CSV失败: {e}")
            return jsonify({'error': '保存失败', 'message': '服务器保存CSV失败'}), 500

        result = {
            "filename": file.filename,
            "rows": len(data),
            "columns": len(headers),
            "columns_list": headers,
            "data_preview": preview_data,
            "full_data": data,  # 包含完整数据
            "server_csv_filename": server_csv_filename
        }
        
        logger.info(f"文件上传成功: {file.filename}, 行数: {len(data)}, 列数: {len(headers)}，已保存为 {server_csv_filename}")
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
    """验证数据格式 - 模拟数据"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': '数据缺失',
                'message': '请提供要验证的数据'
            }), 400
        
        # 模拟数据验证
        input_data = data['data']
        
        # 生成验证结果
        data_types = {}
        for key in input_data[0].keys():
            data_types[key] = "numeric"
        
        validation_result = {
            "is_valid": True,
            "rows": len(input_data),
            "columns": len(input_data[0]) if input_data else 0,
            "missing_values": 0,
            "outliers": random.randint(0, 5),
            "data_types": data_types
        }
        
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
    """预览数据 - 模拟数据"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': '数据缺失',
                'message': '请提供要预览的数据'
            }), 400
        
        input_data = data['data']
        
        # 生成预览数据
        preview = input_data[:5]  # 只取前5行
        
        # 生成统计信息
        statistics = {}
        for key in input_data[0].keys():
            values = [float(row.get(key, 0)) for row in input_data if row.get(key)]
            if values:
                statistics[key] = {
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "mean": round(sum(values) / len(values), 2),
                    "std": round(sum((x - sum(values)/len(values))**2 for x in values) / len(values), 3)
                }
        
        result = {
            "preview": preview,
            "statistics": statistics
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"数据预览失败: {str(e)}")
        return jsonify({
            'error': '预览失败',
            'message': str(e)
        }), 500 

@symbolic_regression_bp.route('/split-plan', methods=['POST'])
def split_plan():
    """返回训练/测试划分方案（空壳模拟）"""
    try:
        data = request.get_json() or {}
        train_ratio = int(data.get('train_ratio', 80))
        test_ratio = 100 - train_ratio
        # 简单回传占比与示例行数（模拟）
        plan = {
            'train_ratio': train_ratio,
            'test_ratio': test_ratio,
            'train_rows': int(0.01 * train_ratio * 100),
            'test_rows': int(0.01 * test_ratio * 100)
        }
        return jsonify({'success': True, 'plan': plan})
    except Exception as e:
        logger.error(f"生成划分方案失败: {e}")
        return jsonify({'success': False, 'error': '生成划分方案失败', 'message': str(e)}), 500