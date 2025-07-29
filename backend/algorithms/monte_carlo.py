#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒙特卡罗分析算法实现
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from loguru import logger
import json
from pathlib import Path
import time
import random

class MonteCarloAnalysis:
    """蒙特卡罗分析算法"""
    
    def __init__(self):
        self.results = {}
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        self._load_saved_results()
    
    def analyze(self, data: Dict[str, Any], target_column: str, 
                feature_columns: List[str], iterations: int = 1000) -> Dict[str, Any]:
        """执行蒙特卡罗分析"""
        try:
            logger.info(f"🎲 开始蒙特卡罗分析，目标变量: {target_column}, 特征变量: {feature_columns}")
            logger.info(f"🔄 迭代次数: {iterations}")
            
            # 数据预处理
            df = pd.DataFrame(data['data'])
            logger.info(f"📊 数据形状: {df.shape}")
            
            # 检查列是否存在
            if target_column not in df.columns:
                raise ValueError(f"目标变量列 '{target_column}' 不存在")
            
            for col in feature_columns:
                if col not in df.columns:
                    raise ValueError(f"特征变量列 '{col}' 不存在")
            
            # 提取数据
            X = df[feature_columns].values
            y = df[target_column].values
            
            logger.info(f"📊 特征数据形状: {X.shape}")
            logger.info(f"📊 目标数据形状: {y.shape}")
            
            # 数据质量检查
            if len(y) < 10:
                raise ValueError("数据样本数量太少，至少需要10个样本")
            
            if y.std() < 1e-6:
                raise ValueError("目标变量没有变化，无法进行分析")
            
            # 检查NaN值
            if np.isnan(X).any() or np.isnan(y).any():
                raise ValueError("数据包含NaN值，请检查数据文件")
            
            # 执行蒙特卡罗模拟
            logger.info("🔄 开始蒙特卡罗模拟...")
            
            # 计算基础统计信息
            target_mean = np.mean(y)
            target_std = np.std(y)
            feature_means = np.mean(X, axis=0)
            feature_stds = np.std(X, axis=0)
            
            logger.info(f"📊 目标变量统计: 均值={target_mean:.3f}, 标准差={target_std:.3f}")
            
            # 蒙特卡罗模拟
            simulations = []
            for i in range(iterations):
                # 随机生成特征值
                simulated_features = np.random.normal(feature_means, feature_stds)
                
                # 计算模拟的目标值（基于线性组合）
                simulated_target = np.sum(simulated_features * np.random.uniform(-1, 1, len(feature_columns)))
                
                # 添加噪声
                simulated_target += np.random.normal(0, target_std * 0.1)
                
                simulations.append({
                    'features': simulated_features.tolist(),
                    'target': simulated_target,
                    'iteration': i + 1
                })
                
                if (i + 1) % 100 == 0:
                    logger.info(f"🔄 完成 {i + 1}/{iterations} 次模拟")
            
            # 分析结果
            simulated_targets = [s['target'] for s in simulations]
            
            # 计算统计信息
            analysis_result = {
                'target_statistics': {
                    'mean': float(np.mean(simulated_targets)),
                    'std': float(np.std(simulated_targets)),
                    'min': float(np.min(simulated_targets)),
                    'max': float(np.max(simulated_targets)),
                    'median': float(np.median(simulated_targets))
                },
                'feature_importance': self._calculate_feature_importance(simulations, feature_columns),
                'confidence_intervals': self._calculate_confidence_intervals(simulated_targets),
                'simulations': simulations[:100],  # 只返回前100个模拟结果
                'parameters': {
                    'iterations': iterations,
                    'target_column': target_column,
                    'feature_columns': feature_columns,
                    'n_features': len(feature_columns),
                    'n_samples': len(y)
                },
                'timestamp': time.time()
            }
            
            # 保存结果
            result_id = int(time.time())
            analysis_result['result_id'] = result_id
            self._save_result(result_id, analysis_result)
            
            logger.info(f"✅ 蒙特卡罗分析完成，结果ID: {result_id}")
            logger.info(f"📊 模拟目标值统计: 均值={analysis_result['target_statistics']['mean']:.3f}, 标准差={analysis_result['target_statistics']['std']:.3f}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 蒙特卡罗分析失败: {str(e)}")
            raise
    
    def _calculate_feature_importance(self, simulations: List[Dict], feature_columns: List[str]) -> List[Dict]:
        """计算特征重要性"""
        try:
            # 基于模拟结果计算特征重要性
            importance_scores = []
            
            for i, feature in enumerate(feature_columns):
                # 计算该特征与目标值的相关性
                feature_values = [s['features'][i] for s in simulations]
                target_values = [s['target'] for s in simulations]
                
                # 计算相关系数
                correlation = np.corrcoef(feature_values, target_values)[0, 1]
                if np.isnan(correlation):
                    correlation = 0
                
                importance_scores.append({
                    'feature': feature,
                    'importance': abs(correlation),
                    'correlation': correlation
                })
            
            # 按重要性排序
            importance_scores.sort(key=lambda x: x['importance'], reverse=True)
            
            logger.info(f"📊 特征重要性计算完成，最高重要性: {importance_scores[0]['feature']} ({importance_scores[0]['importance']:.3f})")
            
            return importance_scores
            
        except Exception as e:
            logger.error(f"❌ 特征重要性计算失败: {str(e)}")
            return []
    
    def _calculate_confidence_intervals(self, values: List[float]) -> Dict[str, float]:
        """计算置信区间"""
        try:
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            # 95%置信区间
            lower_95 = sorted_values[int(0.025 * n)]
            upper_95 = sorted_values[int(0.975 * n)]
            
            # 90%置信区间
            lower_90 = sorted_values[int(0.05 * n)]
            upper_90 = sorted_values[int(0.95 * n)]
            
            # 80%置信区间
            lower_80 = sorted_values[int(0.1 * n)]
            upper_80 = sorted_values[int(0.9 * n)]
            
            return {
                'confidence_95': {'lower': float(lower_95), 'upper': float(upper_95)},
                'confidence_90': {'lower': float(lower_90), 'upper': float(upper_90)},
                'confidence_80': {'lower': float(lower_80), 'upper': float(upper_80)}
            }
            
        except Exception as e:
            logger.error(f"❌ 置信区间计算失败: {str(e)}")
            return {}
    
    def _save_result(self, result_id: int, result: Dict[str, Any]):
        """保存分析结果"""
        try:
            # 保存到内存
            self.results[result_id] = result
            
            # 保存到文件
            result_file = self.results_dir / f"{result_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 结果已保存: {result_file}")
            
        except Exception as e:
            logger.error(f"❌ 结果保存失败: {str(e)}")
            raise
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """获取分析结果"""
        return self.results.get(result_id)
    
    def get_saved_results(self) -> List[Dict[str, Any]]:
        """获取所有已保存的结果"""
        results = []
        for result_id, result in self.results.items():
            results.append({
                'result_id': result_id,
                'target_column': result['parameters']['target_column'],
                'iterations': result['parameters']['iterations'],
                'timestamp': result['timestamp']
            })
        return results
    
    def _load_saved_results(self):
        """加载已保存的结果"""
        try:
            for result_file in self.results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    result_id = result.get('result_id', result_file.stem)
                    self.results[result_id] = result
                except Exception as e:
                    logger.warning(f"⚠️  加载结果文件失败 {result_file}: {str(e)}")
            
            logger.info(f"📁 已加载 {len(self.results)} 个分析结果")
            
        except Exception as e:
            logger.error(f"❌ 加载保存的结果失败: {str(e)}") 