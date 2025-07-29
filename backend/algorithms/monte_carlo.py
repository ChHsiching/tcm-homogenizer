#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒙特卡罗分析算法
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from loguru import logger
import random
import time

class MonteCarloAnalysis:
    """蒙特卡罗分析算法实现"""
    
    def __init__(self):
        self.analyses = {}
        self.analysis_counter = 0
    
    def analyze(self, data, target_column, feature_columns, n_simulations=1000, 
                confidence_level=0.95, test_ratio=0.3):
        """执行蒙特卡罗分析"""
        try:
            logger.info(f"开始蒙特卡罗分析，目标变量: {target_column}, 特征数量: {len(feature_columns)}")
            
            # 数据预处理
            df = pd.DataFrame(data)
            
            # 检查列是否存在
            if target_column not in df.columns:
                raise ValueError(f'目标变量列 "{target_column}" 不存在')
            
            for col in feature_columns:
                if col not in df.columns:
                    raise ValueError(f'特征变量列 "{col}" 不存在')
            
            # 提取数据
            X = df[feature_columns].values
            y = df[target_column].values
            
            # 数据验证
            if len(y) < 10:
                raise ValueError('数据样本数量太少，至少需要10个样本')
            
            if np.std(y) < 1e-6:
                raise ValueError('目标变量没有变化，无法进行分析')
            
            # 处理缺失值
            X = np.nan_to_num(X, nan=0.0)
            y = np.nan_to_num(y, nan=np.nanmean(y))
            
            # 执行蒙特卡罗分析
            results = self._perform_monte_carlo_analysis(
                X, y, feature_columns, n_simulations, confidence_level, test_ratio
            )
            
            # 生成分析ID
            analysis_id = f"mc_{int(time.time())}_{self.analysis_counter}"
            self.analysis_counter += 1
            
            # 保存结果
            self.analyses[analysis_id] = {
                'id': analysis_id,
                'target_column': target_column,
                'feature_columns': feature_columns,
                'n_simulations': n_simulations,
                'confidence_level': confidence_level,
                'results': results,
                'timestamp': time.time()
            }
            
            logger.info(f"蒙特卡罗分析完成，分析ID: {analysis_id}")
            return {
                'success': True,
                'analysis_id': analysis_id,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"蒙特卡罗分析失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _perform_monte_carlo_analysis(self, X, y, feature_names, n_simulations, 
                                     confidence_level, test_ratio):
        """执行蒙特卡罗分析的核心算法"""
        
        # 存储所有模拟结果
        all_predictions = []
        all_actuals = []
        all_r2_scores = []
        all_mse_scores = []
        
        for i in range(n_simulations):
            try:
                # 随机分割数据
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_ratio, random_state=i
                )
                
                # 使用简单的线性回归作为基础模型
                from sklearn.linear_model import LinearRegression
                model = LinearRegression()
                model.fit(X_train, y_train)
                
                # 预测
                y_pred = model.predict(X_test)
                
                # 计算性能指标
                r2 = r2_score(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                
                # 存储结果
                all_predictions.extend(y_pred)
                all_actuals.extend(y_test)
                all_r2_scores.append(r2)
                all_mse_scores.append(mse)
                
            except Exception as e:
                logger.warning(f"模拟 {i} 失败: {str(e)}")
                continue
        
        if len(all_r2_scores) == 0:
            raise ValueError("所有模拟都失败了，无法进行分析")
        
        # 计算统计指标
        r2_mean = np.mean(all_r2_scores)
        r2_std = np.std(all_r2_scores)
        mse_mean = np.mean(all_mse_scores)
        mse_std = np.std(all_mse_scores)
        
        # 计算置信区间
        alpha = 1 - confidence_level
        r2_ci_lower = np.percentile(all_r2_scores, alpha/2 * 100)
        r2_ci_upper = np.percentile(all_r2_scores, (1-alpha/2) * 100)
        mse_ci_lower = np.percentile(all_mse_scores, alpha/2 * 100)
        mse_ci_upper = np.percentile(all_mse_scores, (1-alpha/2) * 100)
        
        # 特征重要性（基于相关系数）
        feature_importance = []
        for i, name in enumerate(feature_names):
            importance = abs(np.corrcoef(X[:, i], y)[0, 1]) if len(y) > 1 else 0
            feature_importance.append({
                'feature': name,
                'importance': float(importance)
            })
        
        # 按重要性排序
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'n_simulations': len(all_r2_scores),
            'r2_mean': float(r2_mean),
            'r2_std': float(r2_std),
            'r2_ci_lower': float(r2_ci_lower),
            'r2_ci_upper': float(r2_ci_upper),
            'mse_mean': float(mse_mean),
            'mse_std': float(mse_std),
            'mse_ci_lower': float(mse_ci_lower),
            'mse_ci_upper': float(mse_ci_upper),
            'feature_importance': feature_importance,
            'confidence_level': confidence_level
        }
    
    def get_analysis(self, analysis_id):
        """获取分析结果"""
        return self.analyses.get(analysis_id)
    
    def get_all_analyses(self):
        """获取所有分析结果"""
        return list(self.analyses.values()) 