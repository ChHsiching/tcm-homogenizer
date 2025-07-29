#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒙特卡罗分析算法
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

class MonteCarloAnalysis:
    """蒙特卡罗分析算法实现"""
    
    def __init__(self):
        self.results = {}
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        self._load_saved_results()
    
    def analyze(self, data: Dict[str, Any], target_column: str, 
                feature_columns: List[str], n_simulations: int = 1000,
                confidence_level: float = 0.95) -> Dict[str, Any]:
        """执行蒙特卡罗分析"""
        try:
            logger.info(f"开始蒙特卡罗分析，目标变量: {target_column}, 特征变量: {feature_columns}")
            
            # 数据预处理
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
            
            # 检查数据质量
            if len(y) < 10:
                raise ValueError("数据样本数量太少，至少需要10个样本")
            
            # 执行蒙特卡罗分析
            result = self._perform_monte_carlo_analysis(
                X, y, feature_columns, n_simulations, confidence_level
            )
            
            # 保存结果
            analysis_id = int(time.time())
            result['analysis_id'] = analysis_id
            self._save_result(analysis_id, result)
            
            logger.info(f"蒙特卡罗分析完成，分析ID: {analysis_id}")
            return result
            
        except Exception as e:
            logger.error(f"蒙特卡罗分析失败: {str(e)}")
            raise
    
    def _perform_monte_carlo_analysis(self, X: np.ndarray, y: np.ndarray, 
                                    feature_names: List[str], n_simulations: int,
                                    confidence_level: float) -> Dict[str, Any]:
        """执行蒙特卡罗分析"""
        try:
            logger.info("开始执行蒙特卡罗分析...")
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
            
            # 存储所有模拟结果
            all_predictions = []
            all_coefficients = []
            
            for i in range(n_simulations):
                # 随机采样训练数据
                indices = np.random.choice(len(X_train), size=len(X_train), replace=True)
                X_boot = X_train[indices]
                y_boot = y_train[indices]
                
                # 使用线性回归作为基础模型
                from sklearn.linear_model import LinearRegression
                model = LinearRegression()
                model.fit(X_boot, y_boot)
                
                # 预测
                y_pred = model.predict(X_test)
                all_predictions.append(y_pred)
                all_coefficients.append(model.coef_)
            
            # 计算统计信息
            predictions_array = np.array(all_predictions)
            coefficients_array = np.array(all_coefficients)
            
            # 计算预测的置信区间
            mean_predictions = np.mean(predictions_array, axis=0)
            std_predictions = np.std(predictions_array, axis=0)
            
            # 计算置信区间
            alpha = 1 - confidence_level
            z_score = 1.96  # 95%置信区间
            ci_lower = mean_predictions - z_score * std_predictions
            ci_upper = mean_predictions + z_score * std_predictions
            
            # 计算系数的重要性
            mean_coefficients = np.mean(coefficients_array, axis=0)
            std_coefficients = np.std(coefficients_array, axis=0)
            
            # 计算性能指标
            r2_scores = []
            mse_scores = []
            
            for pred in all_predictions:
                r2 = r2_score(y_test, pred)
                mse = mean_squared_error(y_test, pred)
                r2_scores.append(r2)
                mse_scores.append(mse)
            
            # 计算特征重要性
            feature_importance = []
            for i, name in enumerate(feature_names):
                importance = abs(mean_coefficients[i])
                feature_importance.append({
                    'feature': name,
                    'coefficient': float(mean_coefficients[i]),
                    'std': float(std_coefficients[i]),
                    'importance': float(importance)
                })
            
            # 按重要性排序
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            result = {
                'n_simulations': n_simulations,
                'confidence_level': confidence_level,
                'predictions': {
                    'mean': mean_predictions.tolist(),
                    'std': std_predictions.tolist(),
                    'ci_lower': ci_lower.tolist(),
                    'ci_upper': ci_upper.tolist(),
                    'actual': y_test.tolist()
                },
                'performance': {
                    'r2_mean': float(np.mean(r2_scores)),
                    'r2_std': float(np.std(r2_scores)),
                    'mse_mean': float(np.mean(mse_scores)),
                    'mse_std': float(np.std(mse_scores))
                },
                'feature_importance': feature_importance,
                'parameters': {
                    'n_features': X.shape[1],
                    'n_samples': len(y),
                    'n_train': len(y_train),
                    'n_test': len(y_test)
                },
                'timestamp': time.time()
            }
            
            logger.info(f"蒙特卡罗分析完成，R²均值 = {np.mean(r2_scores):.3f}, MSE均值 = {np.mean(mse_scores):.3f}")
            return result
            
        except Exception as e:
            logger.error(f"蒙特卡罗分析执行失败: {str(e)}")
            raise
    
    def _save_result(self, analysis_id: int, result: Dict[str, Any]):
        """保存分析结果"""
        try:
            # 保存到内存
            self.results[analysis_id] = result
            
            # 保存到文件
            result_file = self.results_dir / f"{analysis_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析结果已保存: {result_file}")
            
        except Exception as e:
            logger.error(f"分析结果保存失败: {str(e)}")
            raise
    
    def get_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """获取分析结果"""
        return self.results.get(analysis_id)
    
    def get_saved_results(self) -> List[Dict[str, Any]]:
        """获取所有已保存的分析结果"""
        results = []
        for analysis_id, result in self.results.items():
            results.append({
                'analysis_id': analysis_id,
                'n_simulations': result['n_simulations'],
                'confidence_level': result['confidence_level'],
                'performance': result['performance'],
                'timestamp': result['timestamp']
            })
        return results
    
    def _load_saved_results(self):
        """加载已保存的分析结果"""
        try:
            for result_file in self.results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    analysis_id = result.get('analysis_id', result_file.stem)
                    self.results[analysis_id] = result
                except Exception as e:
                    logger.warning(f"加载分析结果文件失败 {result_file}: {str(e)}")
            
            logger.info(f"已加载 {len(self.results)} 个分析结果")
            
        except Exception as e:
            logger.error(f"加载保存的分析结果失败: {str(e)}")
    
    def predict(self, analysis_id: str, X: np.ndarray) -> np.ndarray:
        """使用分析结果进行预测"""
        try:
            result = self.get_result(analysis_id)
            if not result:
                raise ValueError(f"分析结果 {analysis_id} 不存在")
            
            # 这里应该实现真正的预测逻辑
            # 目前返回随机值作为示例
            return np.random.rand(len(X))
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            raise 