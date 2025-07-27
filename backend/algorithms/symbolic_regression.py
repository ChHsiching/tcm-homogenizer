#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
符号回归算法模块
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from loguru import logger
import json
from pathlib import Path
import time

class SymbolicRegression:
    """符号回归算法实现"""
    
    def __init__(self):
        self.models = {}
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self._load_saved_models()
    
    def analyze(self, data: Dict[str, Any], target_column: str, 
                feature_columns: List[str], population_size: int = 100, 
                generations: int = 50) -> Dict[str, Any]:
        """
        执行符号回归分析
        
        Args:
            data: 输入数据
            target_column: 目标变量列名
            feature_columns: 特征变量列名列表
            population_size: 种群大小
            generations: 进化代数
            
        Returns:
            分析结果字典
        """
        try:
            logger.info(f"开始符号回归分析，目标变量: {target_column}")
            logger.info(f"特征变量: {feature_columns}")
            
            # 数据预处理
            X, y = self._prepare_data(data, target_column, feature_columns)
            
            # 执行符号回归（这里使用模拟实现）
            result = self._perform_symbolic_regression(X, y, feature_columns, 
                                                     population_size, generations)
            
            # 保存模型
            model_id = self._save_model(result)
            
            logger.info(f"符号回归分析完成，模型ID: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"符号回归分析失败: {str(e)}")
            raise
    
    def _prepare_data(self, data: Dict[str, Any], target_column: str, 
                     feature_columns: List[str]) -> tuple:
        """准备训练数据"""
        try:
            df = pd.DataFrame(data['data'])
            
            # 检查列是否存在
            if target_column not in df.columns:
                raise ValueError(f"目标变量列 '{target_column}' 不存在")
            
            for col in feature_columns:
                if col not in df.columns:
                    raise ValueError(f"特征变量列 '{col}' 不存在")
            
            # 提取特征和目标变量
            X = df[feature_columns].values
            y = df[target_column].values
            
            # 检查数据类型
            if not np.issubdtype(X.dtype, np.number):
                raise ValueError("特征变量必须为数值类型")
            
            if not np.issubdtype(y.dtype, np.number):
                raise ValueError("目标变量必须为数值类型")
            
            # 处理缺失值
            X = np.nan_to_num(X, nan=0.0)
            y = np.nan_to_num(y, nan=0.0)
            
            logger.info(f"数据准备完成，特征形状: {X.shape}, 目标形状: {y.shape}")
            return X, y
            
        except Exception as e:
            logger.error(f"数据准备失败: {str(e)}")
            raise
    
    def _perform_symbolic_regression(self, X: np.ndarray, y: np.ndarray, 
                                   feature_names: List[str], population_size: int, 
                                   generations: int) -> Dict[str, Any]:
        """执行符号回归算法（模拟实现）"""
        try:
            # 这里使用模拟实现，实际项目中应该使用真实的符号回归库
            # 如 PySR, gplearn 等
            
            logger.info("开始执行符号回归算法...")
            
            # 模拟计算时间
            time.sleep(2)
            
            # 生成模拟结果
            n_features = X.shape[1]
            
            # 简单的线性组合作为示例
            coefficients = np.random.rand(n_features) * 2 - 1
            intercept = np.random.rand() * 2 - 1
            
            # 构建表达式
            expression_parts = []
            for i, (coef, name) in enumerate(zip(coefficients, feature_names)):
                if abs(coef) > 0.01:  # 只保留显著系数
                    if coef >= 0 and i > 0:
                        expression_parts.append(f"+ {coef:.3f} * {name}")
                    else:
                        expression_parts.append(f"{coef:.3f} * {name}")
            
            expression = " + ".join(expression_parts)
            if intercept >= 0:
                expression += f" + {intercept:.3f}"
            else:
                expression += f" - {abs(intercept):.3f}"
            
            # 计算预测值
            y_pred = np.dot(X, coefficients) + intercept
            
            # 计算性能指标
            mse = np.mean((y - y_pred) ** 2)
            r2 = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            # 特征重要性（基于系数绝对值）
            feature_importance = []
            for name, coef in zip(feature_names, coefficients):
                feature_importance.append({
                    'feature': name,
                    'coefficient': float(coef),
                    'importance': float(abs(coef))
                })
            
            # 按重要性排序
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            result = {
                'expression': expression,
                'r2': float(r2),
                'mse': float(mse),
                'feature_importance': feature_importance,
                'predictions': {
                    'actual': y.tolist(),
                    'predicted': y_pred.tolist()
                },
                'parameters': {
                    'population_size': population_size,
                    'generations': generations,
                    'n_features': n_features,
                    'n_samples': len(y)
                },
                'timestamp': time.time()
            }
            
            logger.info(f"符号回归完成，R² = {r2:.3f}, MSE = {mse:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"符号回归执行失败: {str(e)}")
            raise
    
    def _save_model(self, result: Dict[str, Any]) -> str:
        """保存模型"""
        try:
            model_id = f"model_{int(time.time())}"
            result['model_id'] = model_id
            
            # 保存到内存
            self.models[model_id] = result
            
            # 保存到文件
            model_file = self.models_dir / f"{model_id}.json"
            with open(model_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"模型已保存: {model_file}")
            return model_id
            
        except Exception as e:
            logger.error(f"模型保存失败: {str(e)}")
            raise
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取模型"""
        return self.models.get(model_id)
    
    def get_saved_models(self) -> List[Dict[str, Any]]:
        """获取所有已保存的模型"""
        models = []
        for model_id, model in self.models.items():
            models.append({
                'model_id': model_id,
                'expression': model['expression'],
                'r2': model['r2'],
                'mse': model['mse'],
                'timestamp': model['timestamp']
            })
        return models
    
    def _load_saved_models(self):
        """加载已保存的模型"""
        try:
            for model_file in self.models_dir.glob("*.json"):
                try:
                    with open(model_file, 'r', encoding='utf-8') as f:
                        model = json.load(f)
                    model_id = model.get('model_id', model_file.stem)
                    self.models[model_id] = model
                except Exception as e:
                    logger.warning(f"加载模型文件失败 {model_file}: {str(e)}")
            
            logger.info(f"已加载 {len(self.models)} 个模型")
            
        except Exception as e:
            logger.error(f"加载保存的模型失败: {str(e)}")
    
    def predict(self, model_id: str, X: np.ndarray) -> np.ndarray:
        """使用模型进行预测"""
        try:
            model = self.get_model(model_id)
            if not model:
                raise ValueError(f"模型 {model_id} 不存在")
            
            # 这里应该实现真正的预测逻辑
            # 目前返回随机值作为示例
            return np.random.rand(len(X))
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            raise 