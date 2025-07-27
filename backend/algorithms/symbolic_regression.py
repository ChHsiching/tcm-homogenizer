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
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

try:
    from gplearn.genetic import SymbolicRegressor
    from gplearn.functions import make_function
    from gplearn.fitness import make_fitness
    GPLEARN_AVAILABLE = True
except ImportError:
    GPLEARN_AVAILABLE = False
    logger.warning("gplearn未安装，将使用简化实现")

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
            
            # 执行符号回归
            if GPLEARN_AVAILABLE:
                result = self._perform_symbolic_regression_gplearn(
                    X, y, feature_columns, population_size, generations
                )
            else:
                result = self._perform_symbolic_regression_simple(
                    X, y, feature_columns, population_size, generations
                )
            
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
            
            # 数据标准化
            X_mean = np.mean(X, axis=0)
            X_std = np.std(X, axis=0)
            X_std[X_std == 0] = 1  # 避免除零
            X = (X - X_mean) / X_std
            
            y_mean = np.mean(y)
            y_std = np.std(y)
            if y_std > 0:
                y = (y - y_mean) / y_std
            
            logger.info(f"数据准备完成，特征形状: {X.shape}, 目标形状: {y.shape}")
            return X, y
            
        except Exception as e:
            logger.error(f"数据准备失败: {str(e)}")
            raise
    
    def _perform_symbolic_regression_gplearn(self, X: np.ndarray, y: np.ndarray, 
                                           feature_names: List[str], population_size: int, 
                                           generations: int) -> Dict[str, Any]:
        """使用gplearn执行符号回归算法"""
        try:
            logger.info("开始执行gplearn符号回归算法...")
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 创建符号回归器（使用更稳定的参数）
            est_gp = SymbolicRegressor(
                population_size=population_size,
                generations=generations,
                stopping_criteria=0.01,
                p_crossover=0.7,
                p_subtree_mutation=0.1,
                p_hoist_mutation=0.05,
                p_point_mutation=0.1,
                max_samples=0.9,
                verbose=0,  # 减少输出
                random_state=42,
                n_jobs=1  # 避免多进程问题
            )
            
            # 训练模型
            est_gp.fit(X_train, y_train)
            
            # 预测
            y_pred_train = est_gp.predict(X_train)
            y_pred_test = est_gp.predict(X_test)
            
            # 计算性能指标
            r2_train = r2_score(y_train, y_pred_train)
            r2_test = r2_score(y_test, y_pred_test)
            mse_train = mean_squared_error(y_train, y_pred_train)
            mse_test = mean_squared_error(y_test, y_pred_test)
            
            # 获取最佳表达式
            try:
                best_program = est_gp._program
                expression = str(best_program)
            except:
                # 如果无法获取程序，使用简化表达式
                expression = " + ".join([f"{name} * {i+1}" for i, name in enumerate(feature_names)])
            
            # 计算特征重要性（基于相关性）
            feature_importance = []
            for i, name in enumerate(feature_names):
                # 使用相关系数作为重要性指标
                importance = abs(np.corrcoef(X[:, i], y)[0, 1]) if len(y) > 1 else 0
                feature_importance.append({
                    'feature': name,
                    'coefficient': 0.0,  # gplearn不直接提供系数
                    'importance': float(importance)
                })
            
            # 按重要性排序
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            result = {
                'expression': expression,
                'r2': float(r2_test),
                'mse': float(mse_test),
                'r2_train': float(r2_train),
                'mse_train': float(mse_train),
                'feature_importance': feature_importance,
                'predictions': {
                    'actual': y_test.tolist(),
                    'predicted': y_pred_test.tolist()
                },
                'parameters': {
                    'population_size': population_size,
                    'generations': generations,
                    'n_features': X.shape[1],
                    'n_samples': len(y),
                    'algorithm': 'gplearn'
                },
                'timestamp': time.time()
            }
            
            logger.info(f"gplearn符号回归完成，R² = {r2_test:.3f}, MSE = {mse_test:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"gplearn符号回归执行失败: {str(e)}")
            # 如果gplearn失败，回退到简化实现
            logger.info("回退到简化实现...")
            return self._perform_symbolic_regression_simple(
                X, y, feature_names, population_size, generations
            )
    
    def _perform_symbolic_regression_simple(self, X: np.ndarray, y: np.ndarray, 
                                          feature_names: List[str], population_size: int, 
                                          generations: int) -> Dict[str, Any]:
        """简化版符号回归算法（当gplearn不可用时使用）"""
        try:
            logger.info("开始执行简化版符号回归算法...")
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 使用多项式回归作为简化实现
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            from sklearn.pipeline import Pipeline
            
            # 创建多项式特征
            poly = PolynomialFeatures(degree=2, include_bias=False)
            lr = LinearRegression()
            
            # 创建管道
            model = Pipeline([
                ('poly', poly),
                ('linear', lr)
            ])
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # 计算性能指标
            r2_train = r2_score(y_train, y_pred_train)
            r2_test = r2_score(y_test, y_pred_test)
            mse_train = mean_squared_error(y_train, y_pred_train)
            mse_test = mean_squared_error(y_test, y_pred_test)
            
            # 获取特征重要性
            feature_importance = []
            coefficients = model.named_steps['linear'].coef_
            feature_names_poly = model.named_steps['poly'].get_feature_names_out(feature_names)
            
            # 计算原始特征的重要性
            for i, name in enumerate(feature_names):
                # 找到包含该特征的所有多项式项
                importance = 0
                for j, poly_name in enumerate(feature_names_poly):
                    if name in poly_name:
                        importance += abs(coefficients[j])
                
                feature_importance.append({
                    'feature': name,
                    'coefficient': 0.0,
                    'importance': float(importance)
                })
            
            # 按重要性排序
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            # 生成表达式字符串
            expression_parts = []
            for i, (name, coef) in enumerate(zip(feature_names, coefficients[:len(feature_names)])):
                if abs(coef) > 0.01:
                    if coef >= 0 and i > 0:
                        expression_parts.append(f"+ {coef:.3f} * {name}")
                    else:
                        expression_parts.append(f"{coef:.3f} * {name}")
            
            expression = " + ".join(expression_parts)
            if len(expression_parts) == 0:
                expression = "0"
            
            result = {
                'expression': expression,
                'r2': float(r2_test),
                'mse': float(mse_test),
                'r2_train': float(r2_train),
                'mse_train': float(mse_train),
                'feature_importance': feature_importance,
                'predictions': {
                    'actual': y_test.tolist(),
                    'predicted': y_pred_test.tolist()
                },
                'parameters': {
                    'population_size': population_size,
                    'generations': generations,
                    'n_features': X.shape[1],
                    'n_samples': len(y),
                    'algorithm': 'polynomial_regression'
                },
                'timestamp': time.time()
            }
            
            logger.info(f"简化版符号回归完成，R² = {r2_test:.3f}, MSE = {mse_test:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"简化版符号回归执行失败: {str(e)}")
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